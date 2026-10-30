from flask import Flask, render_template, request, jsonify, send_file
import sqlite3
import os
import webbrowser
from threading import Timer
from datetime import datetime, date
import database

app = Flask(__name__)
database.init_db()

@app.route('/')
def index():
    database.refresh_overdue_status()
    return render_template('index.html')

@app.route('/api/stats', methods=['GET'])
def get_stats():
    database.refresh_overdue_status()
    conn = database.get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM students")
    total_students = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM books")
    total_books = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM borrowings WHERE return_date IS NULL")
    active_borrowings = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM borrowings WHERE status = 'overdue' AND return_date IS NULL")
    overdue_borrowings = c.fetchone()[0]

    conn.close()
    return jsonify({
        'total_students': total_students,
        'total_books': total_books,
        'active_borrowings': active_borrowings,
        'overdue_borrowings': overdue_borrowings,
        'today': date.today().isoformat()
    })

@app.route('/api/borrowings', methods=['GET', 'POST'])
def handle_borrowings():
    database.refresh_overdue_status()
    conn = database.get_db()
    c = conn.cursor()

    if request.method == 'GET':
        status = request.args.get('status')
        query = """
            SELECT b.id, b.borrow_date, b.due_date, b.return_date, b.status, b.notes,
                   s.id as student_id, s.name as student_name, s.grade as student_grade, s.phone as student_phone,
                   bk.id as book_id, bk.title as book_title, bk.category as book_category
            FROM borrowings b
            JOIN students s ON b.student_id = s.id
            JOIN books bk ON b.book_id = bk.id
        """
        params = []
        if status and status != 'all':
            query += " WHERE b.status = ?"
            params.append(status)
        query += " ORDER BY b.created_at DESC"

        c.execute(query, params)
        rows = [dict(row) for row in c.fetchall()]
        conn.close()
        return jsonify(rows)

    elif request.method == 'POST':
        data = request.json
        borrow_id = 'BOR-' + str(int(datetime.now().timestamp()))[-5:]
        student_id = data.get('student_id')
        book_id = data.get('book_id')
        borrow_date = data.get('borrow_date', date.today().isoformat())
        due_date = data.get('due_date')
        notes = data.get('notes', '')

        status = 'overdue' if due_date < date.today().isoformat() else 'active'

        c.execute("""
            INSERT INTO borrowings (id, student_id, book_id, borrow_date, due_date, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (borrow_id, student_id, book_id, borrow_date, due_date, status, notes))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'id': borrow_id})

@app.route('/api/borrowings/<borrow_id>/return', methods=['POST'])
def return_borrowing(borrow_id):
    conn = database.get_db()
    c = conn.cursor()
    today = date.today().isoformat()
    data = request.json or {}
    condition = data.get('condition', 'سليمة')
    c.execute("""
        UPDATE borrowings
        SET return_date = ?, status = 'returned',
            notes = coalesce(notes || ' | ', '') || 'أعيدت بتاريخ ' || ? || ' بحالة: ' || ?
        WHERE id = ?
    """, (today, today, condition, borrow_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/borrowings/<borrow_id>', methods=['DELETE'])
def delete_borrowing(borrow_id):
    conn = database.get_db()
    c = conn.cursor()
    c.execute("DELETE FROM borrowings WHERE id = ?", (borrow_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/students', methods=['GET', 'POST'])
def handle_students():
    conn = database.get_db()
    c = conn.cursor()
    if request.method == 'GET':
        c.execute("SELECT * FROM students ORDER BY name ASC")
        rows = [dict(row) for row in c.fetchall()]
        conn.close()
        return jsonify(rows)
    else:
        data = request.json
        s_id = 'S' + str(int(datetime.now().timestamp()))[-4:]
        c.execute("""
            INSERT INTO students (id, name, grade, section, phone)
            VALUES (?, ?, ?, ?, ?)
        """, (s_id, data['name'], data['grade'], data.get('section', ''), data.get('phone', '')))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'id': s_id})

@app.route('/api/students/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    conn = database.get_db()
    c = conn.cursor()
    c.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/books', methods=['GET', 'POST'])
def handle_books():
    conn = database.get_db()
    c = conn.cursor()
    if request.method == 'GET':
        c.execute("SELECT * FROM books ORDER BY title ASC")
        rows = [dict(row) for row in c.fetchall()]
        conn.close()
        return jsonify(rows)
    else:
        data = request.json
        b_id = 'B' + str(int(datetime.now().timestamp()))[-4:]
        c.execute("""
            INSERT INTO books (id, title, category, author, code, copies)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (b_id, data['title'], data['category'], data.get('author', ''), data.get('code', 'ST-01'), data.get('copies', 1)))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'id': b_id})

@app.route('/api/books/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    conn = database.get_db()
    c = conn.cursor()
    c.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/backup/db', methods=['GET'])
def download_db():
    db_file = os.path.join(os.path.dirname(__file__), 'library.db')
    return send_file(db_file, as_attachment=True, download_name='school_library.db')

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')


@app.route('/api/sync', methods=['GET', 'POST'])
def sync_library_data():
    database.refresh_overdue_status()
    conn = database.get_db()
    c = conn.cursor()
    
    if request.method == 'GET':
        c.execute("SELECT id, name, grade, section, phone FROM students ORDER BY name ASC")
        students = [dict(row) for row in c.fetchall()]
        
        c.execute("SELECT id, title, category, author, code, copies FROM books ORDER BY title ASC")
        books = [dict(row) for row in c.fetchall()]
        
        query = """
            SELECT b.id, b.borrow_date as borrowDate, b.due_date as dueDate, b.return_date as returnDate,
                   b.status, b.notes,
                   s.id as studentId, s.name as studentName, s.grade as studentGrade, s.phone as studentPhone,
                   bk.id as bookId, bk.title as bookTitle
            FROM borrowings b
            JOIN students s ON b.student_id = s.id
            JOIN books bk ON b.book_id = bk.id
            ORDER BY b.created_at DESC
        """
        c.execute(query)
        borrowings = [dict(row) for row in c.fetchall()]
        conn.close()
        return jsonify({
            'students': students,
            'books': books,
            'borrowings': borrowings
        })
        
    elif request.method == 'POST':
        data = request.json or {}
        if 'students' in data and len(data['students']) > 0:
            for s in data['students']:
                c.execute("INSERT OR REPLACE INTO students (id, name, grade, section, phone) VALUES (?, ?, ?, ?, ?)",
                          (s['id'], s['name'], s['grade'], s.get('section', ''), s.get('phone', '')))
                          
        if 'books' in data and len(data['books']) > 0:
            for b in data['books']:
                c.execute("INSERT OR REPLACE INTO books (id, title, category, author, code, copies) VALUES (?, ?, ?, ?, ?, ?)",
                          (b['id'], b['title'], b.get('category', 'General'), b.get('author', ''), b.get('code', 'ST-01'), b.get('copies', 1)))
                          
        if 'borrowings' in data:
            for br in data['borrowings']:
                c.execute("""
                    INSERT OR REPLACE INTO borrowings (id, student_id, book_id, borrow_date, due_date, return_date, status, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (br['id'], br['studentId'], br['bookId'], br['borrowDate'], br['dueDate'], br.get('returnDate'), br['status'], br.get('notes', '')))
                
        conn.commit()
        conn.close()
        return jsonify({'status': 'success'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    is_render = os.environ.get('RENDER') is not None
    if not is_render:
        print("==================================================")
        print("📚 تم تشغيل خادم مكتبة المدرسة بنجاح!")
        print(f"🌐 يرجى فتح الرابط التالي في المتصفح: http://127.0.0.1:{port}")
        print("==================================================")
        Timer(1.5, open_browser).start()
    app.run(host='0.0.0.0', port=port, debug=False)

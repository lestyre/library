-- سكربت إنشاء جداول قاعدة بيانات مكتبة المدرسة
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS students (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    grade TEXT NOT NULL,
    section TEXT,
    phone TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS books (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    author TEXT,
    code TEXT,
    copies INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS borrowings (
    id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL,
    book_id TEXT NOT NULL,
    borrow_date TEXT NOT NULL,
    due_date TEXT NOT NULL,
    return_date TEXT,
    status TEXT NOT NULL, -- 'active', 'overdue', 'returned'
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

-- بيانات أولية تجريبية لمكتبة المدرسة
INSERT OR IGNORE INTO students (id, name, grade, section, phone) VALUES
('S101', 'عمر خالد المنصور', 'الخامس الأساسي', 'أ', '03112233'),
('S102', 'سارة يوسف النجار', 'الرابع الأساسي', 'ب', '70445566'),
('S103', 'كريم هاني حمود', 'السادس الأساسي', 'أ', '03778899'),
('S104', 'مريم طارق السعيد', 'الخامس الأساسي', 'ج', '71223344'),
('S105', 'جاد زياد العلي', 'الثالث الأساسي', 'ب', '76554433');

INSERT OR IGNORE INTO books (id, title, category, author, code, copies) VALUES
('B201', 'مغامرات سندباد البحري', 'قصص ومغامرات', 'تراث عربي', 'ST-01', 3),
('B202', 'كليلة ودمنة للناشئة', 'قصص وحكم', 'ابن المقفع', 'ST-02', 2),
('B203', 'عجائب الفضاء والمجرات', 'علمي مبسط', 'د. سامي مراد', 'SC-10', 2),
('B204', 'حكايات ألف ليلة وليلة الميسرة', 'قصص وأساطير', 'إعداد مدرسي', 'ST-05', 4),
('B205', 'تاريخ الأندلس المصور', 'تاريخ', 'أحمد شلبي', 'HI-04', 1);

INSERT OR IGNORE INTO borrowings (id, student_id, book_id, borrow_date, due_date, return_date, status, notes) VALUES
('BOR-1001', 'S101', 'B201', '2026-10-10', '2026-10-20', NULL, 'overdue', 'استعار القصة للمطالعة الأسبوعية'),
('BOR-1002', 'S102', 'B202', '2026-10-15', '2026-10-25', NULL, 'overdue', 'قصة لمادة اللغة العربية'),
('BOR-1003', 'S103', 'B203', '2026-10-28', '2026-11-05', NULL, 'active', 'بحث علمي للمكتبة'),
('BOR-1004', 'S104', 'B204', '2026-10-01', '2026-10-12', '2026-10-11', 'returned', 'تمت الإعادة بحالة ممتازة');

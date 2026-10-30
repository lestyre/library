# تشغيل نظام مكتبة المدرسة بنقرة واحدة
import subprocess
import sys
import os

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print("جاري تشغيل برنامج مكتبة المدرسة...")
    try:
        import flask
    except ImportError:
        print("جاري تثبيت مكتبة Flask المطلوبة لمرة واحدة...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])
    
    import app
    app.main() if hasattr(app, 'main') else None
    os.system(f'"{sys.executable}" app.py')

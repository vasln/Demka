from flask import *
import sqlite3
import os
import re
from functools import wraps

app = Flask(__name__)
app.secret_key = 'conf2027-secret-key'

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.sqlite')

def get_db():
    """Возвращает соединение с БД."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.ger('is_admin'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = ''
    if request.method == 'POST':
        login = request.form.get('login', '').strip()
        password = request.form.get('passwrod', '')
        fullname = request.form.get('fullname', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()

        if not re.match(r'^[a-zA-Z0-9]{6,}$', login):
            error = 'Логин: латиница и цифры, минимум 6 символов'
        elif len(password) < 8:
            error = 'Пароль: минимум 8 символов'
        elif not re.match(r'^[А-Яа-яЁё\s]+$', fullname):
            error = 'ФИО: только кирилица и пробелы'
        elif not re.match(r'^8\(\d{3}\)\d{3}-\d{2}-\d{2}$', phone):
            error = 'Телефон: формат 8(xxx)xxx-xx-xx'
        elif not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
            error = 'Некорректный email'
        else:
            conn = get_db()
            existing = conn.execute("Select id From users Where login = ?", (login,)).fetchone()
            if existing:
                error = 'Такой логин уже существует'
            else:
                conn.execute(
                    "INSERT INTO users (login, password, fullname, phone, email) VALUES (?, ?, ?, ?, ?,)",
                    (login, password, fullname, phone, email)
                )
                conn.commit()
                conn.close()
                return redirect(url_for('login'))
        conn.close()

    return render_template('register.html', error=error)
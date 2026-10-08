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

@app.route('/logout')
def logout():
        session.clear()
        return redirect(url_for('login'))

@app.route('/create_request', methods=['GET', 'POST'])
@login_required
def create_request():
    error = ''
    if request.method == 'POST':
        room = request.form.get('room', '').strip()
        date_start = request.form.get('date', '').strip()
        payment = request.form.get('payment', '').strip()

        if not room or not date_start or not payment:
            error = 'Заполни все поля'
        else:
            conn = get_db()
            conn.execute(
                "INSERT INTO requests (user_id, room, date_starrt, payment) VALUES (?, ?, ?, ?)",
                (session['user_id'], room, date_start, payment)
            )
            conn.commit
            conn.close
            return redirect(url_for('view_requests'))

        return render_template('create_request.html', error=error)

@app.route('/view_requests', methods=['GET', 'POST'])
@login_required
def view_requests():
    conn = get_db()

    if request.method == 'POST':
        request_id = request.form.get('request_id')
        review = request.form.get('review', '').strip()
        if request_id and review:
            conn.execute(
                "UPDATE requests SET review = ? WHERE id = ? AND user_id = ?gi",
                (review, request_id, session['user_id'])
            )
            conn.commit()
        return redirect(url_for('ciew_requests'))

    request_list = conn.execute(
        "SELECT * FROM requests WHERE user_id = ? ORDER BY id DESC",
        (session['user_id'],)
    ).fetchall()
    conn.close()
    return render_template('view_requests.html', requests=request_list)

@app.route('/admin', methods=['GET', 'POST'])
@admin_required
def admin():
    conn = get_db()

    if request.method == 'POST':
        request_id = request.form.get('request_id')
        status = request.form.get('status')
        if request_id and status:
            conn.execute(
                "UPDATE requests SET status = ? WHERE id = ?",
                (status, request_id)
            )
            conn.commit()
        return redirect(url_for('admin'))

    all_requests = conn.execute("""
        SELECT r.*, u. login AS user_login
        FROM requests r
        JOIN users u ON r.user_id = u.id
        ORDER BY r.id DESC
    """).fetchall()
    conn.close()
    return render_template('admin.html', request=all_requests)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
from flask import Flask, session, redirect, request, render_template, abort
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret_key'

import sqlite3

def get_db_connection():
    conn = sqlite3.connect('accounts.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
    login TEXT,
    password TEXT,
    about_me TEXT,
    photo TEXT
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Projects (
    author TEXT,
    name TEXT,
    subject TEXT,
    about TEXT,
    tags TEXT
    );
    ''')
    conn.commit()
    conn.close()

create_db()

@app.route('/')
def index():
    if session.get('logged', True):
        return render_template('main.html', login=session.get('login'))
    elif not session.get('logged', False):
        return render_template('login.html')
    else:
        return render_template('registration.html')

@app.route('/registration')
def reg():
    return render_template('registration.html')

@app.route('/registration', methods=['POST'])
def register():
    login = request.form.get('login')
    password = request.form.get('password')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Users WHERE login = ?', (login,))
    existing_user = cursor.fetchone()

    if existing_user:
        conn.close()
        return abort(400, 'User with this login already exists')

    cursor.execute('INSERT INTO Users (login, password) VALUES (?, ?)', (login, password))
    conn.commit()
    conn.close()

    session['login'] = login
    session['logged'] = True

    return redirect('/')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['logged'] = False
    if 'login' in session:
        del session['login']
    return redirect('/')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    login = request.form.get('login')
    password = request.form.get('password')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT login, password FROM users')
    a = cursor.execute('SELECT * from users where login = "' + login + '" and password = "' + password + '"').fetchall()
    if a:
        session['logged'] = True
        session['login'] = login
        session['password'] = password
        return redirect('/')
    if not a:
        session['logged'] = False
        return redirect('/')
    
@app.route('/projects')
def find_projects():
    conn = get_db_connection()
    cursor = conn.cursor()

    projects = cursor.execute('''SELECT * FROM projects''').fetchall()
    print(projects)
    return render_template('find_projects.html', projects=projects)

@app.route('/create_project')
def create_project():
    return render_template('create_project.html')

@app.route('/create_project', methods = ['POST'])
def creating_projects():
    conn = get_db_connection()
    cursor = conn.cursor()

    name = request.form.get('name')
    subject = request.form.get('subject')
    about = request.form.get('about')
    tags = request.form.get('tags')

    cursor.execute('INSERT INTO Projects (author, name, subject, about, tags) VALUES (?, ?, ?, ?, ?)', (session.get('login'), name, subject, about, tags))
    conn.commit()
    conn.close()

    return redirect('/')

@app.route('/account')
def your_acc():
    user_name=session.get('login')
    return render_template('account.html', user = user_name)

@app.route('/change_the_avatar')
def change_avatar():
    ava_name = request.form.get('avatar')

if __name__ == '__main__':
    app.run(debug=True, port=5009)
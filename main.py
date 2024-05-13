from flask import Flask, session, redirect, request, render_template, abort
import sqlite3
import random

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
    user_name TEXT,
    user_id INTEGER,
    login TEXT,
    password TEXT,
    about_me TEXT,
    photo TEXT,
    tg TEXT,
    git TEXT
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Projects (
    author TEXT,
    name TEXT,
    subject TEXT,
    about TEXT,
    tags list
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Hackathons (
    author TEXT,
    name TEXT,
    about TEXT,
    tags list,
    time INTEGER,
    max_mates INTEGER
    );
    ''')
    conn.commit()
    conn.close()

create_db()

@app.route('/')
def index():
    id = session.get('id')
    if session.get('logged', True):
        return render_template('main.html', id = id, login=session.get('login'))
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
    user_name = request.form.get('user_name')
    password = request.form.get('password')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Users WHERE login = ?', (login,))
    existing_user = cursor.fetchone()

    if existing_user:
        conn.close()
        return abort(400, 'User with this login already exists')

    id = random.randint(1, 18446744073)
    session['id'] = id
    cursor.execute('INSERT INTO Users (user_name, login, password, user_id) VALUES (?, ?, ?, ?)', (user_name, login, password, id))
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

    id = session.get('id')
    projects = cursor.execute('''SELECT * FROM Projects''').fetchall()
    tags = cursor.execute('''SELECT tags FROM Projects WHERE author = "Wall_street" ''')
    print(tags)
    return render_template('find_projects.html', projects=projects, id = id)

@app.route('/create_project')
def create_project():
    id = session.get('id')
    return render_template('create_project.html', id = id)

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

    return redirect('/projects')

@app.route('/account/<int:user_id>')
def your_acc(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    id = session.get('id')
    author = session.get('login')
    password = session.get('password')
    projects = cursor.execute('SELECT * FROM Projects WHERE author = ?', (author,)).fetchall()
    rows = cursor.execute('SELECT about_me, tg, git FROM Users WHERE login = ? and password = ?', (author, password)).fetchone()

    about = rows['about_me']
    telegram = rows['tg']
    github = rows['git']

    return render_template('account.html', id = id, user=author, projects=projects, about=about, telegram=telegram, github=github)


@app.route('/change_the_avatar')
def change_avatar():
    ava_name = request.form.get('avatar')

@app.route('/hackathons')
def the_hack():
    conn = get_db_connection()
    cursor = conn.cursor()

    id = session.get('id')
    hackathons = cursor.execute('''SELECT * FROM Hackathons''').fetchall()
    return render_template("hackathons.html", id = id, hackathons = hackathons)

@app.route('/creation_hack')
def create_hack():
    id = session.get('id')
    return render_template("create_hack.html", id = id)

@app.route('/create_hack', methods = ['POST'])
def create_hackathon():
    conn = get_db_connection()
    cursor = conn.cursor()

    author = session.get('login')
    name = request.form.get('name')
    about = request.form.get('about')
    tags = request.form.get('tags')
    date = request.form.get('date')
    hrefs = request.form.get('hrefs')
    maxmates = request.form.get('maxmates')

    print(date)

    cursor.execute('INSERT INTO Hackathons (author, name, about, tags, time, max_mates) VALUES (?, ?, ?, ?, ?, ?)', (author, name, about, tags, date, maxmates))
    conn.commit()
    conn.close()
    return redirect('/hackathons')

@app.route('/settings')
def set_acc():
    id = session.get('id')
    return render_template('settings.html', id = id)

@app.route('/about_me', methods = ['POST'])
def insert():
    conn = get_db_connection()
    cursor = conn.cursor()

    id = session.get('id')
    git = request.form.get('github')
    about = request.form.get('about')
    telegram = request.form.get('telegram')

    login = session.get('login')
    password = session.get('password')

    if telegram:
        cursor.execute('UPDATE Users SET tg = ? WHERE login = ? and password = ?', (telegram, login, password))
    if git:
        cursor.execute('UPDATE Users SET git = ? WHERE login = ? and password = ?', (git, login, password))
    if about:
        cursor.execute('UPDATE Users SET about_me = ? WHERE login = ? and password = ?', (about, login, password))

    conn.commit()
    conn.close()
    return redirect('/account/'+ session.get('id'))

@app.route('/nofications')
def noficetes():
    id = session.get('id')
    return render_template('nofications.html', id = id)


if __name__ == '__main__':
    app.run(debug=True, port=5008)
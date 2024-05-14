from flask import Flask, session, redirect, request, render_template, abort
import random
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret_key'

conn = sqlite3.connect('accounts.db', check_same_thread=False)
def get_db_connection():
    global conn
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
    tags list,
    id INTEGER,
    git TEXT,
    team INTEGER,
    author_id INTEGER
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Hackathons (
    author TEXT,
    name TEXT,
    about TEXT,
    time INTEGER,
    max_mates INTEGER,
    discord TEXT,
    hackathon_id INTEGER,
    author_id INTEGER
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Messages (
    sender INTEGER,
    sender_name TEXT,
    getter INTEGER,
    getter_name TEXT,
    plot TEXT,
    project_id INTEGER
    );
    ''')
    conn.commit()

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
        return abort(400, 'Введите другой логин и имя пользователя')
    if login and user_name and password:
        id = random.randint(1, 18446744073)
        session['id'] = id
        cursor.execute('INSERT INTO Users (user_name, login, password, user_id) VALUES (?, ?, ?, ?)', (user_name, login, password, id))
        conn.commit()

        session['login'] = login
        session['name'] = user_name
        session['logged'] = True

        return redirect('/login')

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
        session['name'] = cursor.execute('SELECT user_name FROM Users WHERE login = ?', (login,)).fetchone()[0]
        id = cursor.execute('SELECT user_id FROM Users WHERE login = ?', (login,)).fetchone()
        session['id'] = id[0]
        return redirect('/')
    if not a:
        session['logged'] = False
        return redirect('/')
    
@app.route('/projects')
def find_projects():
    conn = get_db_connection()
    cursor = conn.cursor()

    projects = cursor.execute('SELECT * FROM Projects WHERE author_id IS NOT ?', (session.get('id'),)).fetchall()

    return render_template('find_projects.html', projects=projects, id = session.get('id'))
@app.route('/projects/<int:project_id>')
def project(project_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    projects = cursor.execute('SELECT * FROM Projects WHERE id = ' + str(project_id)).fetchone()
    id = session.get('id')
    return render_template('more.html', id = id, projects = projects)

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
    github = request.form.get('github')
    teammates = request.form.get('teammates')
    id = random.randint(1, 18446744073)

    cursor.execute('INSERT INTO Projects (author, name, subject, about, tags, id, git, team, author_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', (session.get('login'), name, subject, about, tags, id, github, teammates, session.get('id')))
    conn.commit()

    return redirect('/projects')

@app.route('/account/<int:user_id>')
def your_acc(user_id):
    cursor = conn.cursor()
    if user_id == session.get('id'):
        author = session.get('login')
        password = session.get('password')
        projects = cursor.execute('SELECT * FROM Projects WHERE author = ?', (author,)).fetchall()

        about = cursor.execute('SELECT about_me FROM Users WHERE login = ? and password = ?', (author, password)).fetchone()
        telegram = cursor.execute('SELECT tg FROM Users WHERE login = ? and password = ?', (author, password)).fetchone()
        github = cursor.execute('SELECT git FROM Users WHERE login = ? and password = ?', (author, password)).fetchone()



        if about: about = about[0]
        elif about == None or about == (None,): about = ''
        if telegram: telegram = telegram[0]
        elif telegram == None or telegram == (None,): telegram = ''
        if github: github = github[0]
        elif github == None or github == (None,): github = ''

        return render_template('account.html', id = user_id, user=author, projects=projects, about=about, telegram=telegram, github=github)

    elif user_id != session.get('id'):
        author = cursor.execute('SELECT user_name FROM Users WHERE user_id = ?', (user_id,)).fetchone()[0]
        projects = cursor.execute('SELECT * FROM Projects WHERE author_id = ?', (user_id,)).fetchall()
        about = cursor.execute('SELECT about_me FROM Users WHERE user_id = ?', (user_id,)).fetchone()[0]
        telegram = cursor.execute('SELECT tg FROM Users WHERE user_id = ?', (user_id,)).fetchone()[0]
        github = cursor.execute('SELECT git FROM Users WHERE user_id = ?', (user_id,)).fetchone()[0]

        return render_template('off_account.html', id = user_id, user=author, projects=projects, about=about, telegram=telegram, github=github)

@app.route('/change_the_avatar')
def change_avatar():
    ava_name = request.form.get('avatar')

@app.route('/hackathons')
def the_hackathons():
    conn = get_db_connection()
    cursor = conn.cursor()

    id = session.get('id')
    hackathons = cursor.execute('''SELECT * FROM Hackathons''').fetchall()
    return render_template("hackathons.html", id = id, hackathons = hackathons)

@app.route('/hackathons/<int:hackathon_id>')
def the_hack(hackathon_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    hackathons = cursor.execute('SELECT * FROM Hackathons WHERE hackathon_id = ?', (hackathon_id,)).fetchone()
    print(hackathons)

    return render_template('hackathon.html', hackathon = hackathons)
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
    date = request.form.get('date')
    discord = request.form.get('hrefs')
    maxmates = request.form.get('maxmates')
    id = random.randint(1, 18446744073)

    cursor.execute('INSERT INTO Hackathons (author, name, about, time, max_mates, discord, hackathon_id, author_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (author, name, about, date, maxmates, discord, id, session.get('id')))
    conn.commit()
    return redirect('/hackathons')

@app.route('/settings')
def set_acc():
    id = session.get('id')
    return render_template('settings.html', id = id)

@app.route('/about_me', methods = ['POST'])
def insert():
    conn = get_db_connection()
    cursor = conn.cursor()

    git = request.form.get('github')
    about = request.form.get('about')
    telegram = request.form.get('telegram')
    print(git, about, telegram)

    login = session.get('login')
    password = session.get('password')

    if telegram:
        cursor.execute('UPDATE Users SET tg = ? WHERE login = ? and password = ?', (telegram, login, password))
    if git:
        cursor.execute('UPDATE Users SET git = ? WHERE login = ? and password = ?', (git, login, password))
    if about:
        cursor.execute('UPDATE Users SET about_me = ? WHERE login = ? and password = ?', (about, login, password))

    conn.commit()
    return redirect('/account/'+ str(session.get('id')))

@app.route('/join_project/<int:project_id>', methods = ['POST'])
def join_project(project_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    getter = cursor.execute('SELECT author_id FROM Projects WHERE id = ?', (project_id,)).fetchone()[0]
    getter_name = cursor.execute('SELECT author FROM Projects WHERE id = ?', (project_id,)).fetchone()[0]
    project = cursor.execute('SELECT name FROM Projects WHERE id = ?', (project_id,)).fetchone()[0]

    cursor.execute('INSERT INTO Messages (sender, sender_name, getter, getter_name, plot) VALUES (?, ?, ?, ?, ?)', ((session.get('id'), session.get('name'), getter, getter_name, session.get('name') +' хочет помочь вам с проектом "' + project + '"!')))
    conn.commit()
    return redirect('/')

@app.route('/join_hack/<int:hackathon_id>', methods = ['POST'])
def join_hackathon(hackathon_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    getter = cursor.execute('SELECT author_id FROM Hackathons WHERE hackathon_id = ?', (hackathon_id,)).fetchone()[0]
    getter_name = cursor.execute('SELECT author FROM Hackathons WHERE hackathon_id = ?', (hackathon_id,)).fetchone()[0]
    hack_name = cursor.execute('SELECT name FROM Hackathons WHERE hackathon_id = ?', (hackathon_id,)).fetchone()[0]

    cursor.execute('INSERT INTO Messages (sender, sender_name, getter, getter_name, plot) VALUES (?, ?, ?, ?, ?)', ((session.get('id'), session.get('name'), getter, getter_name,session.get('name') + ' хочет поучаствовать в хакатоне "' + hack_name + '"!')))
    conn.commit()
    return redirect('/')


@app.route('/nofications')
def noficates():
    id = session.get('id')
    conn = get_db_connection()
    cursor = conn.cursor()

    mess = cursor.execute('SELECT * FROM Messages WHERE getter = ?', (id,)).fetchall()
    nofications = []
    for i in mess:
        nofications.append(i)
    return render_template('nofications.html', id = id, nofications = nofications)

# @app.route('/accept', methods = ['POST'])
# def accept():
#     conn = get_db_connection()
#     cursor = conn.cursor()
#
#     team = cursor.execute('SELECT team FROM Projects WHERE id = ?', (project_id,)).fetchone()
#
#     mass = []
#     for i in team:
#         mass.append(i)
#     cursor.execute('UPDATE Projects SET team = ? WHERE id = ?', (mass[0]-1, project_id))

if __name__ == '__main__':
    app.run(debug=True, port=5008)
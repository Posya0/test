import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, abort, Response

app = Flask(__name__)
app.secret_key = "your secret key"


def get_workflows():
    conn = get_db_connection()
    ex = 'CREATE table if not exists workflows(id integer PRIMARY KEY, name text)'
    conn.execute(ex)
    conn.commit()
    ex = 'SELECT * FROM workflows'
    wfs = conn.execute(ex)
    return wfs


def find_by_id(id):
    conn = sqlite3.connect('database.db')
    ex = 'SELECT name FROM workflows WHERE id=?'
    name = conn.execute(ex, (id,)).fetchone()
    return name


def get_names():
    conn = sqlite3.connect('database.db')
    ex = 'CREATE table if not exists workflows(id integer PRIMARY KEY, name text)'
    conn.execute(ex)
    conn.commit()
    names = conn.execute('SELECT name FROM workflows').fetchall()
    conn.close()
    lnames = []
    for n in names:
        lnames.append(n[0])
    return lnames


def create_workflow(workflow):
    conn = get_db_connection()
    ex = 'CREATE table if not exists workflows(id integer PRIMARY KEY, name text)'
    conn.execute(ex)
    conn.commit()
    id = get_id()
    ex = 'INSERT INTO workflows(id, name) VALUES(?, ?)'
    conn.execute(ex, (int(id + 1), workflow))
    ex = 'CREATE TABLE w' + str(id + 1) + '(variable text)'
    conn.execute(ex)
    conn.commit()
    conn.close()


def insert_variable(variable):
    conn = get_db_connection()
    id = get_id()
    print(variable)
    ex = 'INSERT INTO w' + str(id) + '(variable) VALUES(?)'
    conn.execute(ex, (variable,))
    conn.commit()
    conn.close()


def get_variables(id):
    conn = sqlite3.connect('database.db')
    ex = 'SELECT variable FROM w' + str(id)
    variable = conn.execute(ex).fetchall()
    conn.close()
    lv = []
    for v in variable:
        lv.append(v[0])
    return lv


def get_id():
    conn = sqlite3.connect('database.db')
    id = conn.execute('SELECT id FROM workflows ORDER BY id DESC LIMIT 1').fetchone()
    conn.close()
    if not id:
        return 0
    return id[0]


def get_db_connection():
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    return con


@app.route('/')
def index():
    wfs = get_workflows()
    return render_template('index.html', wfs=wfs)

@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        name = request.form.get('name')
        variables = request.form.getlist('variable')
        if not name:
            flash('Задайте название!')
        elif name in get_names():
            flash('Название не уникально')
        else:
            create_workflow(name)
            for variable in variables:
                if not variable:
                    pass
                else:
                    insert_variable(variable)
            return redirect(url_for('index'))
    return render_template('create.html')


@app.route('/<int:id>', methods=('GET', 'POST'))
def template(id):
    if not find_by_id(id):
        abort(404)
    else:
        name = find_by_id(id)[0]
        variable = get_variables(id)
    return render_template('temp.html', name=name, variables=variable)


@app.route('/<string:id>/run', methods=('GET', 'POST'))
def run(id):
    if not find_by_id(id):
        abort(404)
    else:
        name = find_by_id(id)[0]
        variable = get_variables(id)
        mail = ''
        if request.method == 'POST':
            text = ''
            email = request.form['email']
            for i in range(1, 10):
                if request.form['copy'] == str(i):
                    text = request.form['variable' + str(i)]
            text1 = request.form['mail']
            if not text:
                mail = text1
            else:
                mail = text1 + text
    return render_template('run.html', variables=variable, name=name, mail=mail)

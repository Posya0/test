import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, abort


app = Flask(__name__)
app.secret_key = "polina prozorova"


def get_names():
    conn = sqlite3.connect('base.db')
    ex = 'CREATE table if not exists workflows(name text)'
    conn.execute(ex)
    conn.commit()
    names = conn.execute('SELECT name FROM workflows').fetchall()
    conn.close()
    list_names = []
    for n in names:
        list_names.append(n[0])
    return list_names

def create_workflow(workflow):
    conn = get_db_connection()
    ex = 'CREATE table if not exists workflows(name text)'
    conn.execute(ex)
    conn.commit()
    ex = 'INSERT INTO workflows(name) VALUES(?)'
    conn.execute(ex, (workflow, ))
    ex = 'CREATE TABLE '+workflow+'(parametr text, znachenie text)'
    conn.execute(ex)
    conn.commit()
    conn.close()

def append_parametr(workflow, parametr):
    conn = get_db_connection()
    ex = 'INSERT INTO '+workflow+'(parametr, znachenie) VALUES(?,?)'
    conn.execute(ex, (parametr, ''))
    conn.commit()
    conn.close()

def get_par(workflow):
    conn = sqlite3.connect('base.db')
    ex = 'SELECT parametr FROM '+workflow
    par = conn.execute(ex).fetchall()
    conn.close()
    list_par = []
    for p in par:
        list_par.append(p[0])
    return list_par


def get_db_connection():
    con = sqlite3.connect('base.db')
    con.row_factory = sqlite3.Row
    return con


@app.route('/')
def index():
    names = get_names()
    return render_template('index.html', names=names)


@app.route('/<string:wf_id>', methods=('GET', 'POST'))
def workflow(wf_id):
    if not (wf_id in get_names()):
        abort(404)
    else:
        par = get_par(wf_id)
    return render_template('workflow.html', name=wf_id, parametrs=par)

@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        name = request.form.get('workflow')
        pers = request.form.getlist('per')
        if not name:
            flash('Задайте название!')
        elif not pers[0]:
            flash('Задайте переменную!')
        elif name in get_names():
            flash('Шаблон с таким названием уже существует!')
        else:
            create_workflow(name)
            for per in pers:
                if not per:
                    pass
                else:
                    append_parametr(name, per)
            return redirect(url_for('index'))
    return render_template('create.html')

@app.route('/<string:wf_id>/run', methods=('GET', 'POST'))
def run(wf_id):
    if not (wf_id in get_names()):
        abort(404)
    else:
        par = get_par(wf_id)
        content = ''
        if request.method == 'POST':
            text = ''
            for i in range(1,10):
                if request.form['submit_button'] == str(i):
                    text = request.form['per'+str(i)]
                    print('text ' + text)
            mes = request.form['content']
            if not text:
                pass
            else:
                content = mes + text
    return render_template('run.html', name=wf_id, parametrs=par, content=content)


@app.route('/run', methods=('GET', 'POST'))
def run_select():
    names = get_names()
    if request.method == 'POST':
        wf_id = request.form['workflow']
        if wf_id == 'None':
            flash('Выберите workflow')
        else:
            return redirect(url_for('run', wf_id=wf_id))
    return render_template('run0.html', names=names)



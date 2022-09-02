import sqlite3
import os
from datetime import datetime
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort


app = Flask(__name__)
app.config['SECRET_KEY'] = 'polina prozorova'
PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))


def update(data):
    date = str(datetime.now().strftime("%d.%m.%Y %H:%M"))
    conn = get_db_connection()
    ex = """UPDATE vidacha SET vidan=True, date=? WHERE shtrih=?"""
    conn.execute(ex, (date, data))
    conn.commit()
    conn.close()

def get_note(note_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM vidacha WHERE id = ?', (note_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

def get_spisok(shtrih):
    conn = get_db_connection()
    spisok = conn.execute('SELECT * FROM nakladnaya WHERE reason = ?', (shtrih,)).fetchall()
    conn.close()
    return spisok

def get_tovari():
    conn = get_db_connection()
    tovari = conn.execute('SELECT tovar, ed FROM tovari').fetchall()
    conn.close()
    return tovari

def find_tovar(name):
    conn = get_db_connection()
    tovar = conn.execute('SELECT * FROM tovari WHERE tovar = ?', (name,)).fetchone()
    conn.close()
    return tovar

def get_id_0():
    conn = get_db_connection()
    id = conn.execute('SELECT id FROM vidacha ORDER BY id DESC LIMIT 1').fetchone()
    conn.close()
    return id

def get_id_1():
    conn = get_db_connection()
    id = conn.execute('SELECT id FROM nakladnaya ORDER BY id DESC LIMIT 1',).fetchone()
    conn.close()
    return id

def get_db_connection():
    con = sqlite3.connect(os.path.join(PROJECT_ROOT, 'base.db'))
    con.row_factory = sqlite3.Row
    return con

@app.route('/')
def index():
    conn = get_db_connection()
    number = conn.execute('SELECT * FROM vidacha').fetchall()
    name = conn.execute('SELECT DISTINCT consignee, reason FROM nakladnaya').fetchall()
    conn.close()
    return render_template('index.html', numbers=number, names=name)


@app.route('/<int:note_id>', methods=('GET', 'POST'))
def note(note_id):
    note = get_note(note_id)
    spisok = get_spisok(note['shtrih'])
    consignee = spisok[0][2]
    if request.method == 'POST':
        update(note['shtrih'])
        return redirect(url_for('index'))
    return render_template('note.html', note=note, spisok=spisok, consignee=consignee)


@app.route('/create', methods=('GET', 'POST'))
def create():
    tovari = get_tovari()
    if request.method == 'POST':
        consignee = request.form['consignee']
        ndate = request.form['date']
        elem = []
        flag =True
        for i in range(10):
            name = request.form.get('tovar'+str(i))
            if name!='None':
                kol = request.form['kolvo'+str(i)]
                if kol == '':
                    flag = False
                else:
                    elem.append([name, kol])

        if not consignee or not ndate:
            flash('Не все поля заполнены!')
        elif not flag:
            flash('Количество не заполнено!')
        else:
            data = datetime.strptime(ndate, '%Y-%m-%d').strftime("%d.%m.%Y")
            conn = get_db_connection()
            vidachaID = get_id_0()[0] + 1
            shtrih = 'AB'+str(vidachaID)+'_'+str(data)
            conn.execute('INSERT INTO vidacha (id, shtrih, vidan, date) VALUES (?, ?, ?, ?)',
                         (vidachaID, shtrih, False, ''))
            conn.commit()
            for e in elem:
                nakladnayaID = get_id_1()[0] + 1
                print(e)
                tov = find_tovar(e[0])
                conn.execute('INSERT INTO nakladnaya(id, shepper, consignee, reason, tovar, ed, price, num, summa) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)',
                             (nakladnayaID, 'СУПЕРФИРМА', consignee, shtrih, tov[0], tov[1], tov[2], e[1], int(e[1])* tov[2]))
                conn.commit()
            conn.close()
            return redirect(url_for('index'))
    return render_template('create.html', tovari=tovari)

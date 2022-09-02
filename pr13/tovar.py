import sqlite3
from sqlite3 import Error


def sql_connection():
    try:
        con = sqlite3.connect('../base.db')
        return con
    except Error:
        print(Error)


def sql_table(con):
    cursorObj = con.cursor()
    ex = 'CREATE TABLE tovari(tovar text, ed text, price int)'
    cursorObj.execute(ex)
    con.commit()

def sql_insert(con, entities):
    cursorObj = con.cursor()
    ex = 'INSERT INTO tovari(tovar, ed, price) VALUES(?, ?, ?)'
    cursorObj.execute(ex, entities)
    con.commit()

def find(con):
    cursor = con.cursor()
    cursor.execute('SELECT DISTINCT tovar, ed, price from nakladnaya')
    return cursor.fetchall()


def main():
    con = sql_connection()
    sql_table(con)

    tovari = find(con)

    for tovar in tovari:
        entities = (tovar[0], tovar[1], tovar[2])
        sql_insert(con, entities)


main()
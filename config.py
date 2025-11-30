import sqlite3
from flask import Flask

app = Flask(__name__)

def gdbconnec():
    connection = sqlite3.connect('instance/ecommerce.db')
    connection.row_factory = sqlite3.Row
    return connection

@app.route('/')
def index():
    connection = gdbconnec()
    prod = connection.execute('SELECT * FROM products').fetchall()
    connection.close()
    return '<br>'.join([f"{p['name']} - ${p['price']}" for p in prod])
import MySQLdb
from MySQLdb import cursors
from flask import Flask, jsonify


DB_CONF = {
    'host': '172.16.238.3',
    'port': 3306,
    'user': 'root',
    'passwd': '1234',
    'db': 'flask_app',
    'charset': 'utf8',
    'cursorclass': cursors.DictCursor
}


app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/students', methods=['GET'])
def get_students():
    conn = MySQLdb.Connection(**DB_CONF)
    cursor = conn.cursor()
    sql = 'SELECT id, name from student'
    cursor.execute(sql)
    student_list = cursor.fetchall()
    return jsonify(student_list)


if __name__ == '__main__':
    app.run()

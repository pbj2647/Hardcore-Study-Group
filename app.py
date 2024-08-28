from flask import Flask, request, redirect, url_for, render_template
import pymysql

app = Flask(__name__)

def connectdb():
    conn = pymysql.connect(host='localhost',
                     user='root',
                     passwd='root',
                     db='hardcoreDB',
                     charset='utf8'
                     )
    return conn 

@app.route('/')
def main():
    return redirect(url_for('login'))

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method =="POST":
        username = request.form['username']
        passwd = request.form['passwd']
        return render_template('board.html')
    else:
        return render_template('login.html')

@app.route('/board')
def viewBoard():
    return render_template('board.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method =="POST":
        username = request.form['username']
        passwd = request.form['passwd']
        conn = connectdb()
        cursor = conn.cursor()
        query = f"insert into usertable (username, passwd) values ('{username}', '{passwd}');"
        cursor.execute(query)
        conn.commit()
        conn.close()
        return render_template('login.html')
    else:
        return render_template('signup.html')
    
@app.route('/board', methods=['GET'])
def viewboard():
    conn = connectdb()
    cursor = conn.cursor()
    query = "select * from boardtable"
    cursor.execute(query)
    board_data = cursor.fetchall
    conn.commit()
    conn.close()
    return render_template('board.html', board_data=board_data)



if __name__ == '__main__':
    app.run(debug=True)

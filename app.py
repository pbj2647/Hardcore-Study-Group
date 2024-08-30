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

@app.route('/loginrequire')
def loginrequire():
    return render_template('loginrequire.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method =="POST":
        username = request.form['username']
        passwd = request.form['passwd']
        return viewboard()
    else:
        return render_template('login.html')

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
    query = f"select * from boardtable;"
    cursor.execute(query)
    board_data = cursor.fetchall()
    conn.commit()
    conn.close()
    return render_template('board.html', board_datas=board_data)

@app.route('/write', methods=['POST', 'GET'])
def writepost():
    if request.method =="POST":
        title = request.form['title']
        content = request.form['content']
        username = request.form['username']
        conn = connectdb()
        cursor = conn.cursor()
        query = f"insert into boardtable (title, content, username) values ('{title}', '{content}', '{username}');"
        cursor.execute(query)
        conn.commit()
        conn.close()
        return redirect(url_for('viewboard'))   
    else:
        return render_template('write.html')
    
@app.route('/post', methods=['GET'])
def viewpost():
    arg = request.args.get('id')
    conn = connectdb()
    cursor = conn.cursor()
    query = f"select * from boardtable where id='{arg}';"
    cursor.execute(query)
    post_data = cursor.fetchone()
    conn.commit()
    conn.close()
    return render_template('post.html', post_data=post_data)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)

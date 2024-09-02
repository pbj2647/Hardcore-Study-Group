from flask import Flask, request, session, redirect, url_for, render_template
import pymysql
import jwt

app = Flask(__name__)
app.secret_key = "app_Hardcore"
JWT_SECRET_KEY = "jwt_Hardcore"
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY

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
        conn = connectdb()
        cursor = conn.cursor()
        query = f"select * from usertable where username='{username}' and passwd='{passwd}';"
        cursor.execute(query)
        data = cursor.fetchone
        conn.commit()
        conn.close()
        if data:
            Hardcore_token = jwt.encode({'username': username}, JWT_SECRET_KEY, algorithm='HS256')
            session['Hardcore_token'] = Hardcore_token
            session.permanent = True
            return redirect(url_for('viewboard'))
        else:            
            return render_template('login.html')
    else:
        return render_template('login.html')

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('Hardcore_token', None)
    return redirect(url_for('login'))

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
    if 'Hardcore_token' in session:
        conn = connectdb()
        cursor = conn.cursor()
        keyword = request.args.get('keyword', '').strip()
        index = request.args.get('index')
        if not keyword:
            query = f"select * from boardtable;"
        else:
            if index == "all":
                query = f"select * from boardtable where title like '%{keyword}%' or content like '%{keyword}%' or username like '%{keyword}%';"
            elif index == "title":
                query = f"select * from boardtable where title like '%{keyword}%';"
            elif index == "content":
                query = f"select * from boardtable where content like '%{keyword}%';"
            elif index == "username":
                query = f"select * from boardtable where username like '%{keyword}%';"
        cursor.execute(query)
        board_data = cursor.fetchall()
        conn.commit()
        conn.close()
        return render_template('board.html', board_datas=board_data)
    else:
        return render_template('loginrequire.html')

@app.route('/write', methods=['POST', 'GET'])
def writepost():
    if 'Hardcore_token' in session:
        if request.method =="POST":
            title = request.form['title']
            content = request.form['content']
            username = session['username']
            conn = connectdb()
            cursor = conn.cursor()
            query = f"insert into boardtable (title, content, username) values ('{title}', '{content}', '{username}');"
            cursor.execute(query)
            conn.commit()
            conn.close()
            return redirect(url_for('viewboard'))   
        else:
            return render_template('write.html')
    else:
        return render_template('loginrequire.html')
    
@app.route('/modify', methods=['POST', 'GET'])

@app.route('/delete', methods=['POST', 'GET'])
    
@app.route('/post', methods=['GET'])
def viewpost():
    if 'Hardcore_token' in session:    
        arg = request.args.get('id')
        conn = connectdb()
        cursor = conn.cursor()
        query = f"select * from boardtable where id='{arg}';"
        cursor.execute(query)
        post_data = cursor.fetchone()
        conn.commit()
        conn.close()
        return render_template('post.html', post_data=post_data)
    else:
        return render_template('loginrequire.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)

from flask import Flask, request, session, flash, redirect, url_for, render_template
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
    return render_template('error_page/loginrequire.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method =="POST":
        username = request.form['username']
        passwd = request.form['passwd']
        conn = connectdb()
        cursor = conn.cursor()
        query = f"select * from usertable where username='{username}' and passwd='{passwd}';"
        cursor.execute(query)
        data = cursor.fetchone()
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
    
@app.route('/change_passwd', methods=['POST', 'GET'])
def change_passwd():
    if 'Hardcore_token' in session:
        if request.method =="POST":
            Hardcore_token = session['Hardcore_token']
            username = jwt.decode(Hardcore_token, JWT_SECRET_KEY, algorithms=['HS256'])['username']
            new_passwd = request.form['new_passwd']
            confirm_new_passwd = request.form['confirm_new_passwd']
            conn = connectdb()
            cursor = conn.cursor()
            if new_passwd == confirm_new_passwd:
                query = f"update usertable set passwd = '{new_passwd}' where username = '{username}'"
                cursor.execute(query)
                conn.commit()
                conn.close()
                return redirect(url_for('viewboard'))
            else:
                flash('새 비밀번호와 비밀번호 확인이 일치하지 않습니다')
                return render_template('error_page/passwd_check_error.html')
        else:
            return render_template('change_passwd.html') 
    else:
        return render_template('error_page/loginrequire.html')
    
@app.route('/board', methods=['GET'])
def viewboard():
    if 'Hardcore_token' in session:
        conn = connectdb()
        cursor = conn.cursor()
        keyword = request.args.get('keyword', '').strip()
        index = request.args.get('index')
        sorting_index = request.args.get('sorting_index')
        if not keyword:
            query = f"select * from boardtable"
        else:
            if index == "all":
                query = f"select * from boardtable where title like '%{keyword}%' or content like '%{keyword}%' or username like '%{keyword}%'"
            elif index == "title":
                query = f"select * from boardtable where title like '%{keyword}%'"
            elif index == "content":
                query = f"select * from boardtable where content like '%{keyword}%'"
            elif index == "username":
                query = f"select * from boardtable where username like '%{keyword}%'"
        if sorting_index is not None:
            query += f" order by {sorting_index};"
        else:
            query += ";"
        cursor.execute(query)
        board_data = cursor.fetchall()
        conn.commit()
        conn.close()
        return render_template('board.html', board_datas=board_data)
    else:
        return render_template('error_page/loginrequire.html')

@app.route('/write', methods=['POST', 'GET'])
def writepost():
    if 'Hardcore_token' in session:
        if request.method =="POST":
            Hardcore_token = session['Hardcore_token']
            username = jwt.decode(Hardcore_token, JWT_SECRET_KEY, algorithms=['HS256'])['username']
            title = request.form['title']
            content = request.form['content']
            file = request.files['file']
            conn = connectdb()
            cursor = conn.cursor()
            if file:
                file.save('./uploads/' + file.filename)
                query = f"insert into boardtable (title, content, username, filename) values ('{title}', '{content}', '{username}' ,'{file.filename}');"
            else:
                query = f"insert into boardtable (title, content, username) values ('{title}', '{content}', '{username}');"
            cursor.execute(query)
            conn.commit()
            conn.close()
            return redirect(url_for('viewboard'))   
        else:
            return render_template('write.html')
    else:
        return render_template('error_page/loginrequire.html')
    
@app.route('/modify', methods=['POST', 'GET'])
def modify_post():
    if 'Hardcore_token' in session:
        if request.method =="POST":
            Hardcore_token = session['Hardcore_token']
            username = jwt.decode(Hardcore_token, JWT_SECRET_KEY, algorithms=['HS256'])['username']
            modify_username = request.form['username']
            post_id = request.form['post_id']
            modify_title = request.form['title']
            modify_content = request.form['content']
            modify_file = request.files['file']
            if username == modify_username:
                conn = connectdb()
                cursor = conn.cursor()
                if modify_file:
                    modify_file.save('./uploads/' + modify_file.filename)
                    query = f"update boardtable set title = '{modify_title}', content = '{modify_content}', filename = '{modify_file.filename}' where id = '{post_id}';"
                else:
                    query = f"update boardtable set title = '{modify_title}', content = '{modify_content}', filename = null where id = '{post_id}';"
                cursor.execute(query)
                conn.commit()
                conn.close()
                return redirect(url_for('viewpost', id = post_id))
            else:
                return render_template('error_page/passwd_check_error.html')
        else:
            post_id = request.args.get('id')
            conn = connectdb()
            cursor = conn.cursor()
            query = f"select * from boardtable where id='{post_id}';"
            cursor.execute(query)
            post_data = cursor.fetchone()
            conn.commit()
            conn.close()
            return render_template('modify.html', post_data=post_data) 
    else:
        return render_template('error_page/loginrequire.html')

@app.route('/delete', methods=['POST', 'GET'])
def delete_post():
    if 'Hardcore_token' in session:
        if request.method =="POST":
            Hardcore_token = session['Hardcore_token']
            username = jwt.decode(Hardcore_token, JWT_SECRET_KEY, algorithms=['HS256'])['username']
            post_id = request.form['post_id']
            conn = connectdb()
            cursor = conn.cursor()
            query1 = f"select username from boardtable where id = '{post_id}';"
            query2 = f"delete from boardtable where id = '{post_id}';"
            cursor.execute(query1)
            data = cursor.fetchone()[0]
            if data == username:
                cursor.execute(query2)
                conn.commit()
                conn.close()
                return redirect(url_for('viewboard'))
            else:
                return render_template('error_page/delete_error.html', post_id = post_id)
        else:
            post_id = request.args.get('id')
            return render_template('delete.html', post_id=post_id) 
    else:
        return render_template('error_page/loginrequire.html')

@app.route('/post', methods=['GET'])
def viewpost():
    if 'Hardcore_token' in session:    
        post_id = request.args.get('id')
        conn = connectdb()
        cursor = conn.cursor()
        query = f"select * from boardtable where id='{post_id}';"
        cursor.execute(query)
        post_data = cursor.fetchone()
        conn.commit()
        conn.close()
        return render_template('post.html', post_data=post_data)
    else:
        return render_template('error_page/loginrequire.html')
    
@app.route('/post/donwload', methods=['POST'])
def download():
    return


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)

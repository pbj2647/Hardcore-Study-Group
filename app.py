from flask import Flask, request, session, flash, redirect, url_for, send_file, render_template
from pymysql.err import IntegrityError
import pymysql
import jwt
import os

app = Flask(__name__)
app.secret_key = "app_Hardcore"
JWT_SECRET_KEY = os.urandom(32)
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY

upload_folder = './uploads/'
profileimg_folder = './uploads/profile/'

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
    return render_template('alert_page/loginrequire.html')

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
        phonenumber = request.form['phonenumber']
        email = request.form['email']
        address = request.form['address']
        conn = connectdb()
        cursor = conn.cursor()
        query = f"insert into usertable (username, passwd, phonenumber, email, address) values ('{username}', '{passwd}', '{phonenumber}', '{email}', '{address}');"
        try:
            cursor.execute(query)
            conn.commit()
            conn.close()
            return render_template('login.html')
        except IntegrityError:
            conn.rollback()  
            conn.close()
            return render_template('alert_page/signup_error.html')
    else:
        return render_template('signup.html')

@app.route('/find_username', methods=['POST', 'GET'])
def find_username():
    if request.method =="POST":
        phonenumber = request.form['phonenumber']
        conn = connectdb()
        cursor = conn.cursor()
        query = f"select username from usertable where phonenumber='{phonenumber}';"
        cursor.execute(query)
        username = cursor.fetchone()
        print(username)
        return render_template('alert_page/your_username.html', username=username)
    else:
        return render_template('find_username.html')

@app.route('/find_passwd', methods=['POST', 'GET'])
def find_passwd():
    if request.method =="POST":
        username = request.form['username']
        passwd = request.form['passwd']
        phonenumber = request.form['phonenumber']
        email = request.form['email']
        address = request.form['address']
    else:
        return render_template('find_passwd.html')

@app.route('/uploads/profile/<filename>')
def profile_image(filename):
    return send_file(f'./uploads/profile/{filename}')

@app.route('/mypage', methods=['POST', 'GET'])
def mypage():
    if 'Hardcore_token' in session:
        Hardcore_token = session['Hardcore_token']
        current_username = jwt.decode(Hardcore_token, JWT_SECRET_KEY, algorithms=['HS256'])['username']
        if request.method =="POST":
            username = request.form['username']
            if username == current_username:
                current_username = current_username
                email = request.form['email']
                address = request.form['address']
                profileimg = request.files['profileimg']
                conn = connectdb()
                cursor = conn.cursor()
                if profileimg:
                    profileimg.save(profileimg_folder + profileimg.filename)
                    query = f"update usertable set email='{email}', address='{address}', profileimg='{profileimg.filename}' where username='{current_username}'"
                else:
                    query = f"update usertable set email='{email}', address='{address}' where username='{current_username}';"
                cursor.execute(query)
                conn.commit()
                conn.close()
                return redirect(url_for('mypage'))
            else:
                return render_template('alert_page/not_your_mypage.html')
        else:
            if request.args.get('username'):
                username = request.args.get('username')
            else:
                username = current_username
            conn = connectdb()
            cursor = conn.cursor()
            query = f"select * from usertable where username = '{username}'"
            cursor.execute(query)
            mypage_data = cursor.fetchone()
            if mypage_data[6] == None:
                profile_img = profileimg_folder + 'defaultprofile.png'
            else:
                profile_img = profileimg_folder + mypage_data[6]
            conn.close()
            return render_template('mypage.html', mypage_data = mypage_data, profile_img = profile_img)
    else:
        return render_template('alert_page/loginrequire.html')

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
                return render_template('alert_page/passwd_check_error.html')
        else:
            return render_template('change_passwd.html') 
    else:
        return render_template('alert_page/loginrequire.html')
    
@app.route('/board', methods=['GET'])
def viewboard():
    if 'Hardcore_token' in session:
        Hardcore_token = session['Hardcore_token']
        username = jwt.decode(Hardcore_token, JWT_SECRET_KEY, algorithms=['HS256'])['username']
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
        conn.close()
        return render_template('board.html', board_datas=board_data, username=username)
    else:
        return render_template('alert_page/loginrequire.html')

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
                file.save(upload_folder + file.filename)
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
        return render_template('alert_page/loginrequire.html')
    
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
                    modify_file.save(upload_folder + modify_file.filename)
                    query = f"update boardtable set title = '{modify_title}', content = '{modify_content}', filename = '{modify_file.filename}' where id = '{post_id}';"
                else:
                    query = f"update boardtable set title = '{modify_title}', content = '{modify_content}', filename = null where id = '{post_id}';"
                cursor.execute(query)
                conn.commit()
                conn.close()
                return redirect(url_for('viewpost', id = post_id))
            else:
                return render_template('alert_page/not_write_user.html', id = post_id)
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
        return render_template('alert_page/loginrequire.html')

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
                return render_template('alert_page/delete_error.html', post_id = post_id)
        else:
            post_id = request.args.get('id')
            return render_template('delete.html', post_id=post_id) 
    else:
        return render_template('alert_page/loginrequire.html')

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
        return render_template('alert_page/loginrequire.html')
    
@app.route('/post/download', methods=['GET'])
def download():
    if 'Hardcore_token' in session:
        filename = request.args.get('filename')
        file_path = upload_folder + filename
        return send_file(file_path, as_attachment=True)
    else:
        return render_template('alert_page/loginrequire.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)

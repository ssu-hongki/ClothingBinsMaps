from flask import Flask, render_template, jsonify, request, redirect, url_for, session
import pymysql
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.secret_key = 'super-secret-key'

def get_connection():
    return pymysql.connect(
        host=os.getenv('MYSQL_HOST'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DB'),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def home():
    return render_template('map.html')

@app.route('/bins')
def bins():
    gu = request.args.get('gu')
    conn = get_connection()
    cursor = conn.cursor()
    if gu:
        cursor.execute("SELECT * FROM bins WHERE gu = %s", (gu,))
    else:
        cursor.execute("SELECT * FROM bins")
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)

# ✅ 댓글 조회 API
@app.route('/reviews')
def reviews():
    bin_id = request.args.get('bin_id')
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reviews WHERE bin_id = %s ORDER BY created_at DESC", (bin_id,))
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)

# ✅ 댓글 작성 API
@app.route('/add-review', methods=['POST'])
def add_review():
    bin_id = request.form['bin_id']
    content = request.form['content']
    gu = request.form['gu']

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO reviews (bin_id, content) VALUES (%s, %s)",
        (bin_id, content)
    )
    conn.commit()
    conn.close()

    return redirect(url_for('map_by_gu', gu=gu))

# ✅ 구 선택 지도 라우트
@app.route('/map')
def map_by_gu():
    gu = request.args.get('gu')
    return render_template('map.html', gu=gu, is_admin=session.get('admin'))

# ✅ 관리자 로그인 (숨겨진 URL)
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        pw = request.form['password']
        if pw == os.getenv('ADMIN_PASSWORD'):
            session['admin'] = True
            return redirect(url_for('home'))
        else:
            return "비밀번호가 틀렸습니다"
    return '''
        <form method="post">
            <input type="password" name="password" placeholder="관리자 비밀번호">
            <input type="submit" value="로그인">
        </form>
    '''

# ✅ 로그아웃
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import pymysql

app = Flask(__name__)
app.secret_key = 'super-secret-key'  # 세션용

# DB 연결 함수
def get_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',  # 너의 비번 입력
        database='clothing_bins_db',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/map')
def map_page():
    gu = request.args.get('gu')
    return render_template('map.html', gu=gu)

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

@app.route('/reviews/<int:bin_id>')
def get_reviews(bin_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, content, created_at FROM reviews WHERE bin_id = %s ORDER BY created_at DESC", (bin_id,))
    reviews = cursor.fetchall()
    conn.close()
    return jsonify(reviews)

@app.route('/add-review', methods=['POST'])
def add_review():
    bin_id = request.form['bin_id']
    content = request.form['content']
    gu = request.form['gu']
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO reviews (bin_id, content) VALUES (%s, %s)", (bin_id, content))
    conn.commit()
    conn.close()
    return redirect(url_for('map_page', gu=gu))

# ✅ 관리자 로그인
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form['password']
        if password == 'admin123':
            session['admin'] = True
            return redirect(url_for('home'))
        else:
            return "비밀번호가 틀렸습니다!", 401
    return '''
        <form method="POST">
            <input type="password" name="password" placeholder="관리자 비밀번호 입력">
            <button type="submit">로그인</button>
        </form>
    '''

# ✅ 댓글 삭제
@app.route('/delete-review/<int:id>')
def delete_review(id):
    if not session.get('admin'):
        return "접근 불가", 403
    gu = request.args.get('gu', '강남구')
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reviews WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('map_page', gu=gu))

# ✅ 댓글 수정
@app.route('/edit-review/<int:id>', methods=['GET', 'POST'])
def edit_review(id):
    if not session.get('admin'):
        return "접근 불가", 403
    conn = get_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        content = request.form['content']
        gu = request.form['gu']
        cursor.execute("UPDATE reviews SET content = %s WHERE id = %s", (content, id))
        conn.commit()
        conn.close()
        return redirect(url_for('map_page', gu=gu))
    cursor.execute("SELECT content FROM reviews WHERE id = %s", (id,))
    review = cursor.fetchone()
    conn.close()
    return f'''
        <form method="POST">
            <textarea name="content">{review['content']}</textarea>
            <input type="hidden" name="gu" value="강남구">
            <button type="submit">수정 완료</button>
        </form>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
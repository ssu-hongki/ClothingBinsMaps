from flask import Flask, render_template, request, jsonify, redirect, session
import pymysql
import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.permanent_session_lifetime = timedelta(days=1)

# ✅ MySQL 연결 함수
def get_connection():
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DB"),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
@app.route('/generic')
def generic():
    return render_template('generic.html')
# ✅ 1️⃣ 홈화면: 구 선택 페이지
@app.route('/')
def home():
    return render_template('home.html')

# ✅ 2️⃣ 지도 페이지
@app.route('/map')
def map_page():
    gu = request.args.get('gu')
    if not gu:
        return redirect('/')  # 홈화면으로 돌려보냄
    return render_template('map_generic.html', gu=gu)

@app.route('/gu/<gu_name>') #정지훈 추가
def gu_page(gu_name):
    return redirect(f"/map?gu={gu_name}")

# ✅ 3️⃣ 수거함 위치 마커 데이터
@app.route('/bins')
def bins():
    gu = request.args.get('gu')
    conn = get_connection()
    cursor = conn.cursor()
    if gu:
        cursor.execute("SELECT * FROM bins WHERE gu = %s", (gu,))
    else:
        cursor.execute("SELECT * FROM bins")
    bins = cursor.fetchall()
    conn.close()
    return jsonify(bins)

# ✅ 4️⃣ 댓글 작성
@app.route('/add-review', methods=['POST'])
def add_review():
    bin_id = request.form.get('bin_id')
    content = request.form.get('content')
    gu = request.form.get('gu')

    if not bin_id or not content:
        return "Missing data", 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO reviews (bin_id, content) VALUES (%s, %s)", (bin_id, content))
    conn.commit()
    conn.close()
    return redirect(f"/map?gu={gu}")

# ✅ 5️⃣ 댓글 불러오기 (한국 시간으로)
@app.route('/reviews')
def reviews():
    bin_id = request.args.get('bin_id')
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, content, created_at FROM reviews WHERE bin_id = %s ORDER BY created_at DESC", (bin_id,))
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        if row['created_at']:
            row['created_at'] = (row['created_at'] + timedelta(hours=9)).strftime('%Y-%m-%d %H:%M:%S')

    return jsonify(rows)
# /admin : 게이트웨이
@app.route('/admin')
def admin_entry():
    if session.get('admin'):
        return redirect('/admin-dashboard')
    return redirect('/admin-login')

# 관리자 대시보드
@app.route('/admin-dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect('/admin-login')
    return render_template('admin_dashboard_generic.html')

# ✅ (관리자) 모든 리뷰 조회
@app.route('/reviews-all')
def reviews_all():
    if not session.get('admin'):
        return "권한 없음", 403
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, content, created_at FROM reviews ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        if row['created_at']:
            row['created_at'] = (row['created_at'] + timedelta(hours=9)).strftime('%Y-%m-%d %H:%M:%S')

    return jsonify(rows)


# ✅ 6️⃣ 댓글 삭제 (관리자)
@app.route('/delete-review/<int:review_id>', methods=['POST'])
def delete_review(review_id):
    if not session.get('admin'):
        return "권한 없음", 403
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reviews WHERE id = %s", (review_id,))
    conn.commit()
    conn.close()
    return "삭제 완료", 200

# ✅ 7️⃣ 댓글 수정 (관리자)
@app.route('/update-review/<int:review_id>', methods=['POST'])
def update_review(review_id):
    if not session.get('admin'):
        return "권한 없음", 403
    new_content = request.form.get('new_content')
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE reviews SET content = %s WHERE id = %s", (new_content, review_id))
    conn.commit()
    conn.close()
    return "수정 완료", 200

# ✅ 8️⃣ 관리자 로그인
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        pw = request.form.get('password')
        if pw == os.getenv('ADMIN_PASSWORD'):
            session['admin'] = True
            return redirect('/')
        else:
            return "비밀번호가 틀렸습니다", 401
    return render_template('admin_login.html')

# ✅ 9️⃣ 관리자 로그아웃
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
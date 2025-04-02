import pymysql
import json

# ✅ 여기에 네 DB 접속 정보 입력
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='',  # 비밀번호 설정했으면 입력
    database='clothing_bins_db',
    charset='utf8mb4'
)

cursor = conn.cursor()

# ✅ JSON 파일 읽기
with open('data/bins_all.json', encoding='utf-8') as f:
    bins = json.load(f)

inserted = 0

for bin in bins:
    try:
        cursor.execute(
            """
            INSERT INTO bins (name, address, lat, lng, gu)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (bin['name'], bin['address'], bin['lat'], bin['lng'], bin['gu'])
        )
        inserted += 1
    except Exception as e:
        print(f"⚠️ 에러 발생: {e}")
        continue

conn.commit()
conn.close()

print(f"\n✅ MySQL에 {inserted}개 데이터 삽입 완료!")
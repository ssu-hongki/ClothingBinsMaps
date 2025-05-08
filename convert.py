import csv
import chardet
import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return pymysql.connect(
        host=os.getenv('MYSQL_HOST'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DB'),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

files = [
    ('bins_jongno.csv', '종로구'),
    ('bins_seongdong.csv', '성동구'),
    ('bins_dongdaemun.csv', '동대문구'),
    ('bins_jungnang.csv', '중랑구'),
    ('bins_seongbuk.csv', '성북구'),
    ('bins_gangbuk.csv', '강북구'),
    ('bins_eunpyeong.csv', '은평구'),
    ('bins_seodaemun.csv', '서대문구'),
    ('bins_mapo.csv', '마포구'),
    ('bins_yangcheon.csv', '양천구'),
    ('bins_gangseo.csv', '강서구'),
    ('bins_geumcheon.csv', '금천구'),
    ('bins_yeongdeungpo.csv', '영등포구'),
    ('bins_dongjak.csv', '동작구'),
    ('bins_gwanak.csv', '관악구'),
    ('bins_seocho.csv', '서초구'),
    ('bins_gangnam.csv', '강남구'),
    ('bins_songpa.csv', '송파구'),
    ('bins_gangdong.csv', '강동구'),
    ('bins_gwangjin.csv', '광진구')
]

conn = get_connection()
cursor = conn.cursor()
inserted_count = 0

for filename, gu in files:
    file_path = os.path.join('data', filename)

    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
        encoding = result['encoding']
        print(f"📂 {filename} 인코딩 감지됨 → {encoding}")

    with open(file_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            try:
                # ✅ 필드명 깨짐 방지: BOM 제거 + strip
                row = {key.strip().replace('\ufeff', ''): value for key, value in row.items()}

                address = (
                    row.get('주소') or
                    row.get('도로명 주소') or
                    row.get('소재지도로명주소') or
                    row.get('소재지지번주소') or
                    row.get('위치') or
                    row.get('설치장소') or
                    row.get('도로명주소') or
                    row.get('설치장소(도로명주소)') or
                    row.get('설치장소(도로명)') or
                    '주소 미상'
                )

                name = row.get('설치장소명') or address
                lat = float(row['위도'])
                lng = float(row['경도'])

                # ✅ 덮어쓰기 방식 (좌표+구가 같으면 교체)
                cursor.execute("""
                    REPLACE INTO bins (id, name, address, lat, lng, gu)
                    VALUES (
                        (SELECT id FROM (
                            SELECT id FROM bins WHERE lat = %s AND lng = %s AND gu = %s LIMIT 1
                        ) AS subquery),
                        %s, %s, %s, %s, %s
                    )
                """, (lat, lng, gu, name, address, lat, lng, gu))

                inserted_count += 1
                if inserted_count % 100 == 0:
                    print(f"➡️ {inserted_count}개 삽입 중...")

            except Exception as e:
                print(f"❌ [행 {idx}] 오류 발생: {e}")
                print(f"  ▶ 주소: {address}, 위도: {row.get('위도')}, 경도: {row.get('경도')}")

conn.commit()
conn.close()

print(f"\n🎉 총 {inserted_count}개 수거함 → 클라우드 MySQL 덮어쓰기 완료!")
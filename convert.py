import csv
import json
import os
import chardet

# ✅ 자동 인코딩 감지 함수
def detect_encoding(filepath):
    with open(filepath, 'rb') as f:
        return chardet.detect(f.read())['encoding']

# ✅ 구별 CSV 파일 정보
files = {
    "동작구": "bins_dongjak.csv",
    "강남구": "bins_gangnam.csv",
    "서초구": "bins_seocho.csv",
    "관악구": "bins_gwanak.csv"
}

all_data = []

# ✅ 각 구 CSV 순회하면서 데이터 읽기
for gu, filename in files.items():
    filepath = os.path.join("data", filename)
    encoding = detect_encoding(filepath)
    print(f"📂 {filename} 인코딩 감지됨 → {encoding}")

    with open(filepath, newline='', encoding=encoding) as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                lat = float(row['위도'])
                lng = float(row['경도'])

                # 💡 주소 컬럼 자동 대응
                address = (
                    row.get('주소') or
                    row.get('도로명 주소') or
                    row.get('소재지도로명주소') or
                    row.get('지번주소') or
                    ''
                )

                # 💡 이름 컬럼 자동 대응
                name = (
                    row.get('이름') or
                    row.get('설치장소명') or
                    f"{gu} 수거함"
                )

                all_data.append({
                    "name": name,
                    "address": address,
                    "lat": lat,
                    "lng": lng,
                    "gu": gu
                })

            except Exception as e:
                print(f"⚠️ {filename}에서 에러 발생: {e}")
                continue

# ✅ 결과 저장
output_path = 'data/bins_all.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print(f"\n✅ 총 {len(all_data)}개 수거함 데이터 → {output_path} 저장 완료!")
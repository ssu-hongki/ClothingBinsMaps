import csv
import json

csv_file = 'data/bins.csv'
json_file = 'data/bins.json'

data = []

with open(csv_file, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        item = {
            "name" : f"{row['행정동']} 수거함",
            "lat" : float(row['위도']),
            "lng" : float(row['경도']),
            "address" : row['주소']
        }
        data.append(item)

with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ {len(data)}개의 수거함이 bins.json 으로 저장되었습니다!")
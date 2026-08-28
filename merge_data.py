import csv, io
from datetime import datetime

# --------------------------------------------------------------
# 파일 경로 (필요에 따라 수정)
ORIGINAL_FILE = 'myDeductionExpenses.csv'          # 백업 파일
GENERATED_FILE = 'FYN93N_ATO_Logbook.csv'          # 방금 만든 로그북
OUTPUT_FILE = 'myDeductionExpenses_ReadyToImport.csv'  # 최종 병합 결과

# --------------------------------------------------------------
def _parse_date(s: str):
    """dd/mm/yyyy 형식 문자열을 datetime 으로 변환."""
    try:
        return datetime.strptime(s, '%d/%m/%Y')
    except Exception:
        return None


def _read_sections(path: str):
    """원본 CSV 를 읽어 Header / Trips / Logbooks / Vehicles 로 구분."""
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    sections = {'Header': [], 'Trips': [], 'Logbooks': [], 'Vehicles': []}
    cur = 'Header'
    for line in lines:
        stripped = line.strip()
        if stripped == 'Trips':
            cur = 'Trips'
        elif stripped == 'Logbooks':
            cur = 'Logbooks'
        elif stripped == 'Vehicles':
            cur = 'Vehicles'
        sections[cur].append(line)
    return sections


def _load_existing_trips(trip_lines):
    """Trips 섹션 전체를 CSV 로 파싱 → 리스트 반환."""
    # 첫 번째 라인은 "Trips\n", 두 번째는 헤더
    csv_body = io.StringIO(''.join(trip_lines[1:]))   # 헤더 포함
    reader = csv.DictReader(csv_body)
    return [row for row in reader]   # 모든 기존 기록을 보존


def _load_generated_trips(path):
    """새로 만든 로그북 파일을 읽어 리스트 반환."""
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


def _write_merged(
        sections,
        merged_trips,
        out_path):
    """Header, Trips, Logbooks, Vehicles 를 순서대로 파일에 기록."""
    with open(out_path, 'w', encoding='utf-8', newline='') as f:
        # Header
        for line in sections['Header']:
            f.write(line)

        # Trips
        f.write('Trips\n')
        fieldnames = merged_trips[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for trip in merged_trips:
            # 누락된 컬럼은 빈 문자열로 채움
            clean = {k: trip.get(k, '') for k in fieldnames}
            writer.writerow(clean)

        f.write('\n')
        # Logbooks
        for line in sections['Logbooks']:
            f.write(line)

        f.write('\n')
        # Vehicles
        for line in sections['Vehicles']:
            f.write(line)


def merge():
    # 1️⃣ 원본 파일 파싱
    sections = _read_sections(ORIGINAL_FILE)

    # 2️⃣ 기존 Trips 전체 보존
    existing_trips = _load_existing_trips(sections['Trips'])

    # 3️⃣ 새로 만든 로그북 읽기
    generated_trips = _load_generated_trips(GENERATED_FILE)

    # 4️⃣ 모든 Trips 를 합치고 날짜 기준 정렬
    all_trips = existing_trips + generated_trips
    all_trips.sort(key=lambda r: _parse_date(r.get('Date', '')) or datetime.min)

    # 5️⃣ 병합 파일 쓰기
    _write_merged(sections, all_trips, OUTPUT_FILE)

    print(f'✅ 병합 완료 → {OUTPUT_FILE}')
    print(f'전체 Trip 수: {len(all_trips)}')


if __name__ == '__main__':
    merge()

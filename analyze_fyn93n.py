import csv
from datetime import datetime

FILE = 'myDeductionExpenses_ReadyToImport.csv'

def parse_date(s):
    return datetime.strptime(s, '%d/%m/%Y')

def fiscal_year(date):
    # fiscal year starts July 1
    if date.month >= 7:
        return date.year
    else:
        return date.year - 1

today = datetime(2026, 8, 25)
prev_fy_start = datetime(2025, 7, 1)
prev_fy_end = datetime(2026, 6, 30)
curr_fy_start = datetime(2026, 7, 1)

prev_total = 0.0
curr_total = 0.0

with open(FILE, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        vehicle = row.get('Vehicle', '').strip().upper()
        if vehicle != 'FYN93N':
            continue
        try:
            d = parse_date(row['Date'])
            km = float(row.get('Total Km', '0') or 0)
        except Exception:
            continue
        if prev_fy_start <= d <= prev_fy_end:
            prev_total += km
        if curr_fy_start <= d <= today:
            curr_total += km

print('지난 회계년도 총 운행 km:', prev_total)
print('올 회계년도 현재까지 총 운행 km:', curr_total)

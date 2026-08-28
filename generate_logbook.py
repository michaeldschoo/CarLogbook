import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import csv

# ==========================================
# [설정 영역] 추후 데이터 생성 시 아래 값들만 수정하세요!
# ==========================================

# 1. 목표치 및 총 주행거리 설정
TARGET_PERCENTAGE = 0.95        # 비즈니스 사용 비율 (95% -> 0.95)
TOTAL_MILEAGE = 4425            # 현재 차량의 총 누적 주행거리 (수정 필요!)
TARGET_BUSINESS_KM = TOTAL_MILEAGE * TARGET_PERCENTAGE

# 2. 시작 계기판 숫자 및 날짜 범위 설정
START_ODOMETER = 120            # 차량의 시작 주행계기판 숫자
START_DATE = datetime(2026, 5, 1)  # 기록 시작 날짜 (년, 월, 일)
END_DATE = datetime(2026, 8, 24)   # 기록 종료 날짜 (년, 월, 일)

# 3. 공휴일 설정 (제외할 날짜)
PUBLIC_HOLIDAYS = [
    datetime(2026, 6, 8), # King's Birthday
    datetime(2026, 8, 3), # Bank Holiday
]

# 4. 주중 추가 목적지 목록 (원하는 만큼 추가/수정 가능)
# 새로운 목적지가 생기면 아래 중괄호 {...} 블록을 복사해서 추가하세요.
EXTRA_DESTINATIONS = [
    {
        "End location#": "Ikea Marsden Park, Hollinsworth, Marsden Park NSW, Australia",
        "Trip details": "To purchase office furniture, accessories",
        "Trip distance*": 22.62, # 편도 거리
        "Total Km": 45.24        # 왕복 거리 (편도 x 2)
    },
    {
        "End location#": "KMall09 Lidcombe Shopping Centre, Parramatta Road, Lidcombe NSW, Australia",
        "Trip details": "To purchase office supplies",
        "Trip distance*": 39.40,
        "Total Km": 78.80
    }
]
# ==========================================

def load_and_clean_data(file_path):
    # Read the file to find the Trips section
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    start_idx = -1
    end_idx = -1
    for i, line in enumerate(lines):
        if line.startswith('Uploaded,Type,Status,Date'):
            start_idx = i
        elif line.startswith('Logbooks') and start_idx != -1:
            end_idx = i - 1
            break
            
    if start_idx == -1:
        raise ValueError("Could not find Trips section in CSV")
        
    # Extract the Trips section
    import io
    csv_data = "".join(lines[start_idx:end_idx])
    # Parse CSV robustly: skip malformed lines and respect quoting
    df = pd.read_csv(io.StringIO(csv_data), index_col=False, on_bad_lines='skip', quoting=csv.QUOTE_MINIMAL)
    
    # Clean and standardize
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
    df = df.dropna(subset=['Date'])
    
    # Filter for dates from May 2026 to August 24 2026
    mask = (df['Date'] >= START_DATE) & (df['Date'] <= END_DATE)
    df = df[mask].copy()
    
    # Standardize vehicle to FYN93N
    df['Vehicle'] = 'FYN93N'
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['Date', 'End location#', 'Total Km'])
    
    return df

def generate_random_trips(current_km):
    remaining_km = TARGET_BUSINESS_KM - current_km
    new_trips = []
    
    if remaining_km <= 0:
        return new_trips
        
    # Generate list of possible dates (excluding Sundays, Mondays, and public holidays)
    possible_dates = []
    current_date = START_DATE
    while current_date <= END_DATE:
        if current_date.weekday() not in [0, 6]: # Skip Monday(0) and Sunday(6)
            if current_date not in PUBLIC_HOLIDAYS:
                possible_dates.append(current_date)
        current_date += timedelta(days=1)
        
    # To allow random multiple trips per day (e.g., 0, 1, or 2), we multiply the possible dates
    # so that each day has up to 2 "slots". Then we sample without replacement.
    possible_slots = possible_dates * 2
        
    while remaining_km > 0 and possible_slots: # ensure at least 95%
        # Pick a random date slot
        slot_idx = random.randint(0, len(possible_slots) - 1)
        date = possible_slots.pop(slot_idx) 
        
        # Pick a random destination
        dest = random.choice(EXTRA_DESTINATIONS)
        
        new_trips.append({
            'Uploaded': 'Not uploaded',
            'Type': 'Employee',
            'Status': 'Completed',
            'Date': date,
            'Vehicle': 'FYN93N',
            'Purpose of trip': 'Employee - work',
            'Start location#': 'Edu-Kingdom College High Street Penrith NSW Australia',
            'End location#': dest['End location#'],
            'Trip details': dest['Trip details'],
            'Trip distance*': dest['Trip distance*'],
            'Record multiple trips*': 1,
            'Record the return journey*': 'Yes',
            'Total Km': dest['Total Km'],
            'Logbook trip': 'Y'
        })
        remaining_km -= dest['Total Km']
            
    return pd.DataFrame(new_trips)

def main():
    file_path = 'myDeductionExpenses.csv'
    
    print("Loading and cleaning data...")
    df = load_and_clean_data(file_path)
    current_km = df['Total Km'].sum()
    print(f"Current business km in period: {current_km:.2f}")
    
    print(f"Target business km (95% of {TOTAL_MILEAGE}): {TARGET_BUSINESS_KM:.2f}")
    
    if current_km < TARGET_BUSINESS_KM:
        print("Generating random extra trips...")
        new_trips_df = generate_random_trips(current_km)
        df = pd.concat([df, new_trips_df], ignore_index=True)
    
    # Sort by date
    df = df.sort_values(by='Date').reset_index(drop=True)
    
    # Distribute the remaining personal km randomly across the days as blank gaps in odometer
    # But logbook usually only requires business trips. We'll fill odometer readings sequentially.
    
    # Actually, ATO requires start and end odometer for each trip.
    # Total distance is 4425. We have business distance ~4203.
    # So there is ~222km of personal use. We can just add small personal gaps between some trips.
    
    total_business_km = df['Total Km'].sum()
    personal_km = TOTAL_MILEAGE - total_business_km
    
    current_odo = START_ODOMETER
    start_odos = []
    end_odos = []
    
    for i, row in df.iterrows():
        # Randomly assign some personal km before this trip
        if personal_km > 0 and random.random() > 0.7:
            gap = min(personal_km, random.uniform(5, 20))
            current_odo += gap
            personal_km -= gap
            
        start_odos.append(round(current_odo))
        current_odo += row['Total Km']
        end_odos.append(round(current_odo))
        
    df['Start odometer*'] = start_odos
    df['End odometer*'] = end_odos
    df['Logbook trip'] = 'Y'
    
    # Format Date back to string
    df['Date'] = df['Date'].dt.strftime('%d/%m/%Y')
    
    # Select columns to match output format
    cols = ['Uploaded', 'Type', 'Status', 'Date', 'Vehicle', 'Purpose of trip', 
            'Start odometer*', 'End odometer*', 'Start location#', 'End location#', 
            'Trip details', 'Trip distance*', 'Record multiple trips*', 
            'Record the return journey*', 'Total Km', 'Logbook trip']
    
    for col in cols:
        if col not in df.columns:
            df[col] = ''
            
    df = df[cols]
    
    output_excel = 'FYN93N_ATO_Logbook.xlsx'
    output_csv = 'FYN93N_ATO_Logbook.csv'
    
    df.to_excel(output_excel, index=False)
    df.to_csv(output_csv, index=False)
    
    print(f"\nFinal Logbook generated:")
    print(f"- Total Business Trips: {len(df)}")
    print(f"- Total Business Km: {total_business_km:.2f}")
    print(f"- Target Business Km: {TARGET_BUSINESS_KM:.2f}")
    print(f"- Business Use Percentage: {(total_business_km/TOTAL_MILEAGE)*100:.2f}%")
    print(f"\nSaved to {output_excel} and {output_csv}")

if __name__ == "__main__":
    main()

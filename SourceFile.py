import pandas as pd
import openpyxl

# 주행 기록 샘플 데이터
data = [
    {
        "Date": "2026-07-01",
        "Odometer Start (km)": 45200,
        "Odometer End (km)": 45245,
        "Total Kilometers": 45,
        "Business Purpose": "Client consultation and site inspection at Penrith",
        "Vehicle": "BYD Shark 6"
    },
    {
        "Date": "2026-07-03",
        "Odometer Start (km)": 45245,
        "Odometer End (km)": 45280,
        "Total Kilometers": 35,
        "Business Purpose": "Pickup supplies for business operations",
        "Vehicle": "BYD Shark 6"
    },
    {
        "Date": "2026-07-06",
        "Odometer Start (km)": 45280,
        "Odometer End (km)": 45330,
        "Total Kilometers": 50,
        "Business Purpose": "Meeting with regional partners in Parramatta",
        "Vehicle": "BYD Shark 6"
    }
]

df = pd.DataFrame(data)

# CSV 파일로 저장
df.to_csv("ato_vehicle_logbook_sample.csv", index=False)

# Excel(엑셀) 파일로 저장
df.to_excel("ato_vehicle_logbook_sample.xlsx", index=False)

print("파일 생성이 완료되었습니다!")
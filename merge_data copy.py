import csv
from datetime import datetime

original_file = 'myDeductionExpenses.csv'
generated_file = 'FYN93N_ATO_Logbook.csv'
output_file = 'myDeductionExpenses_ReadyToImport.csv'

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%d/%m/%Y')
    except:
        return None

def merge():
    # 1. Read original file and separate sections
    with open(original_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    sections = {'Trips': [], 'Logbooks': [], 'Vehicles': [], 'Header': []}
    current_section = 'Header'
    
    # We know the markers
    for line in lines:
        if line.strip() == 'Trips':
            current_section = 'Trips'
            sections[current_section].append(line)
            continue
        elif line.strip() == 'Logbooks':
            current_section = 'Logbooks'
            sections[current_section].append(line)
            continue
        elif line.strip() == 'Vehicles':
            current_section = 'Vehicles'
            sections[current_section].append(line)
            continue
            
        sections[current_section].append(line)

    # 2. Process Trips section
    trips_lines = sections['Trips']
    # The first line of trips_lines is 'Trips\n'
    # The second is the CSV header for Trips
    trips_header = trips_lines[1]
    
    # Parse existing trips, excluding FYN93N after 01/05/2026 and excluding corrupt lines
    import io
    old_trips_csv = io.StringIO("".join(trips_lines[1:]))
    reader = csv.DictReader(old_trips_csv)
    
    retained_trips = []
    for row in reader:
        # Check if row is malformed due to manual edit
        if None in row or len(row) < 5:
            continue
            
        vehicle = row.get('Vehicle', '').strip()
        date_str = row.get('Date', '').strip()
        
        # We want to remove FYN93N or Fyn93n(2) trips after 01/05/2026 because we generated new ones
        if vehicle.lower() in ['fyn93n', 'fyn93n(2)']:
            d = parse_date(date_str)
            if d and d >= datetime(2026, 5, 1):
                continue # Skip, we will replace this
                
        retained_trips.append(row)
        
    # 3. Read newly generated trips
    new_trips = []
    with open(generated_file, 'r', encoding='utf-8') as f:
        new_reader = csv.DictReader(f)
        for row in new_reader:
            new_trips.append(row)
            
    # Combine trips
    all_trips = retained_trips + new_trips
    
    # Sort all trips by date just to be clean
    def sort_key(row):
        d = parse_date(row.get('Date', ''))
        return d if d else datetime(1970, 1, 1)
        
    all_trips.sort(key=sort_key)
    
    # 4. Write output file
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        # Write Header
        for line in sections['Header']:
            f.write(line)
            
        # Write Trips
        f.write('Trips\n')
        
        # Ensure we write with the same fieldnames
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for trip in all_trips:
            # fill missing fields with empty string to match fieldnames
            clean_trip = {k: trip.get(k, '') for k in fieldnames}
            writer.writerow(clean_trip)
            
        f.write('\n')
        
        # Write Logbooks
        for line in sections['Logbooks']:
            f.write(line)
            
        f.write('\n')
            
        # Write Vehicles
        for line in sections['Vehicles']:
            f.write(line)
            
    print(f"Merge successful! Saved to {output_file}")
    print(f"Total Trips: {len(all_trips)}")

if __name__ == '__main__':
    merge()

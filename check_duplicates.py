import csv, collections, sys
path = r'F:/Source/AICoding/VibeCoding/penrithekc/RPA/CarLogbook/myDeductionExpenses.csv'
duplicates = collections.defaultdict(list)
with open(path, newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    for i, row in enumerate(reader, start=1):
        key = tuple(row)
        duplicates[key].append(i)

found = False
for key, lines in duplicates.items():
    if len(lines) > 1:
        found = True
        print('Duplicate rows at lines:', lines)
        print('Row content:', ','.join(key))
if not found:
    print('No duplicate rows found')

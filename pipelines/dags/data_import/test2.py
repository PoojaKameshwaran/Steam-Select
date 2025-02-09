import csv
with open('containers/thisistheone_part1.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f, delimiter='|')
    for i, row in enumerate(reader):
        if len(row) != 12:
            print(f"Row {i} has {len(row)} columns: {row}")
import csv

with open("data/food_db.csv", newline="") as f:
    reader = list(csv.reader(f))

header = reader[0]
col_index = header.index("Related to Recipes")

# remove from header
header.pop(col_index)

# remove from each row
for row in reader[1:]:
    row.pop(col_index)

with open("data/new.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(reader)
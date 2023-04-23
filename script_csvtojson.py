import csv
import json

# Open the CSV file and read the data into a dictionary
with open('csv_data.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    data = [row for row in reader]

# Convert the dictionary to JSON format
json_data = json.dumps(data)

# Write the JSON data to a new file
with open('pokemon_data.json', 'w') as jsonfile:
    jsonfile.write(json_data)
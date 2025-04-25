import csv
import re

def extract_notion_ids():
    notion_ids = []
    
    with open('pages.csv', 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            match = re.search(r'([a-f0-9]{32})\?pvs=4', row['url'])
            if match:
                notion_ids.append(match.group(1))
                print(row['title'])
    return notion_ids

ids = extract_notion_ids()

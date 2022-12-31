import sqlite3
import json

with open('receipts.json') as f:
    data = json.load(f)
    receipts = data['data']['rewardsActivityFeed']['list']['groups'][1:-1]
    print(receipts)
# Initialise database with tables for receipts and receipt items

import sqlite3

conn = sqlite3.connect("receipt_data.db")
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS receipt
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            receipt_id TEXT NOT NULL UNIQUE,
            receipt_url TEXT,
            receipt_date TEXT,
            receipt_total REAL,
            storeNo TEXT,
            raw_data TEXT,
            FOREIGN KEY(storeNo) REFERENCES branch(storeNo))''')

c.execute('''CREATE TABLE IF NOT EXISTS branch
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            storeNo TEXT NOT NULL UNIQUE,
            title TEXT,
            content TEXT,
            division TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS items
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            receipt_id TEXT,
            item_name TEXT,
            item_qty REAL,
            item_unit TEXT,
            item_total REAL,
            raw_data TEXT,
            FOREIGN KEY(receipt_id) REFERENCES receipt(receipt_id))''')

conn.commit()
conn.close()
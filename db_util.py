import sqlite3
import json
from datetime import datetime

conn = sqlite3.connect("data/receipt_data.db")
c = conn.cursor()


def commit_close():
    conn.commit()
    conn.close()


def add_item(receipt_id, item_name, item_qty, item_unit, item_total, raw_data):
    try:
        c.execute("INSERT INTO items VALUES(null,?,?,?,?,?,?)",
                  [receipt_id, item_name, item_qty, item_unit, item_total, raw_data])
    except Exception as e:
        print(e, f'{receipt_id} - {item_name}')


def add_branch(store_no, title, content, division):
    try:
        c.execute("INSERT OR IGNORE INTO branch VALUES(null,?,?,?,?)", [store_no, title, content, division])
    except Exception as e:
        print(e, f'Store No - {store_no}')


def add_receipt(receipt_id, receipt_url, receipt_date, receipt_total, store_no, raw_data):
    try:
        c.execute("INSERT INTO receipt VALUES(null,?,?,?,?,?,?)",
                  [receipt_id, receipt_url, receipt_date, receipt_total, store_no, raw_data])
    except Exception as e:
        print(e, f'Receipt ID - {receipt_id}')


def get_db_receipt_ids():
    query = "SELECT receipt_id FROM receipt"

    c.execute(query)
    data = c.fetchall()
    return [item[0] for item in data]


def get_new_receipt_ids(receipt_list):
    stored_ids = get_db_receipt_ids()
    new_ids = [item['id'] for item in receipt_list]
    return set(new_ids).difference(set(stored_ids))


def get_receipts_from_response(response):
    receipt_list = response
    receipts = sum([receipt['items'] for receipt in receipt_list['data']['rewardsActivityFeed']['list']['groups'][1:]],
                   [])
    items = [item for item in receipts if item['receipt']]
    return items


def get_branch_data(item):
    keys = ['storeNo', 'title', 'content', 'division']
    return list(item[key] for key in keys)


def get_list_of_line_items(receipt_id, item):
    skip_to = 0
    receipt_items = []
    raw_data = json.dumps(item)
    for i, e in enumerate(item['items']):
        item_qty = 0
        item_unit = ''
        if i < skip_to:
            continue
        if e['amount'] == '':
            skip_to = i + 2
            try:
                next_item = item['items'][i + 1]
            except IndexError as index_error:
                print(i, item['items'])
                print(e)
                if 'PRICE REDUCED' in e['description']:
                    break
                else:
                    print(index_error)
            if 'PRICE REDUCED' in e['description']:
                skip_to = i + 1
                continue

            if 'Qty' in next_item['description']:
                item_qty = float(next_item['description'].split(" ")[1])
                item_unit = "pc"
            elif 'NET @' in next_item['description']:
                item_qty = float(next_item['description'].split(" ")[0])
                item_unit = next_item['description'].split(" ")[1]

            item_name = e['description']
            item_total = float(next_item['amount'])

            receipt_items.append((receipt_id, item_name, item_qty, item_unit, item_total, raw_data))

        elif 'PRICE REDUCED' in e['description']:
            skip_to = i + 1
            continue
        else:
            item_name = e['description']
            item_total = float(e['amount'])
            item_qty = 1
            item_unit = 'pc'

            receipt_items.append((receipt_id, item_name, item_qty, item_unit, item_total, raw_data))

    return receipt_items


def get_iso_date_from_string(date_str: str):
    d = datetime.strptime(date_str, '%d/%m/%Y')
    return d.strftime("%Y-%m-%d")


def get_data(receipt_id, items):
    # receipt_id,receipt_date,receipt_total,store_no,raw_data
    receipt_date = ''
    receipt_total = ''
    raw_data = json.dumps(items)
    receipt_url = ''

    receipt_items = []

    try:
        receipt_url = items['data']['receiptDetails']['download']['url']
        for item in items['data']['receiptDetails']['details']:
            if item['__typename'] == 'ReceiptDetailsHeader':
                branch = get_branch_data(item)
                store_no = branch[0]
            elif item['__typename'] == 'ReceiptDetailsTotal':
                receipt_total = float(item['total'][1:])
            elif item['__typename'] == 'ReceiptDetailsFooter':
                receipt_date = get_iso_date_from_string(item['transactionDetails'][-10:])
            elif item['__typename'] == 'ReceiptDetailsItems':
                receipt_items = get_list_of_line_items(receipt_id, item)

    except KeyError as e:
        with open('data/error.txt', 'a+') as error_file:
            error_file.writelines(f'{receipt_id} - Key error at {e}\n')

    receipt_info = (receipt_id, receipt_url, receipt_date, receipt_total, store_no, raw_data)

    return [branch, receipt_info, receipt_items]


def initialise_db():
    conn = sqlite3.connect("data/receipt_data.db")
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS receipt
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                receipt_id TEXT NOT NULL,
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


def run_sql_query(query):
    conn = sqlite3.connect("data/receipt_data.db")
    c = conn.cursor()

    c.execute(query)
    data = c.fetchall()
    conn.close()
    return [item for item in data]


def get_total_expenses_by_month():
    query = """
    SELECT COUNT(*) id, strftime('%Y-%m', receipt_date) year_month, sum(receipt_total)
    FROM receipt
    GROUP BY year_month
    ORDER BY year_month DESC
    """
    return run_sql_query(query)


def get_total_amount_by_item():
    query = """
        SELECT COUNT(*) id, strftime('%Y-%m', receipt_date) year_month, sum(receipt_total)
        FROM receipt
        GROUP BY year_month
        ORDER BY year_month DESC
        """
    return run_sql_query(query)


def get_items_by_receipt_id(id):
    query = f'''
    SELECT *
    FROM items
    WHERE items.receipt_id == '{id}'
    '''
    return run_sql_query(query)


def get_all_receipts():
    query = '''
    SELECT *
    FROM receipt
    '''
    return run_sql_query(query)


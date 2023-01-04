import sqlite3
import json
import logging

conn = sqlite3.connect("data/receipt_data.db")
c = conn.cursor()
def commit_close():
    conn.commit()
    conn.close()
def add_item(receipt_id,item_name,item_qty,item_unit,item_total,raw_data):
    try:
        c.execute("INSERT INTO items VALUES(null,?,?,?,?,?,?)", [receipt_id,item_name,item_qty,item_unit,item_total,raw_data])
    except Exception as e:
        print(e, f'{receipt_id} - {item_name}')
def add_branch(storeNo,title,content,division):
    try:
        c.execute("INSERT OR IGNORE INTO branch VALUES(null,?,?,?,?)", [storeNo,title,content,division])
    except Exception as e:
        print(e, f'Store No - {storeNo}')
def add_receipt(receipt_id,receipt_url,receipt_date,receipt_total,storeNo,raw_data):
    try:
        c.execute("INSERT INTO receipt VALUES(null,?,?,?,?,?,?)", [receipt_id,receipt_url,receipt_date,receipt_total,storeNo,raw_data])
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
    receipts = sum([receipt['items'] for receipt in receipt_list['data']['rewardsActivityFeed']['list']['groups'][1:]],[])
    items = [item for item in receipts if item['receipt']]
    return items

def get_data(receipt_id, items):
    total = 0;
    # storeNo,title,content,division
    storeNo = ''
    title = ''
    content = ''
    division = ''

    # receipt_id,receipt_date,receipt_total,storeNo,raw_data
    receipt_date = ''
    receipt_total = ''
    raw_data = json.dumps(items)
    receipt_url = ''

    receipt_items = []

    try:
        for item in items['data']['receiptDetails']['details']:
        # print(json.dumps(item, indent=4))
            if item['__typename'] == 'ReceiptDetailsHeader':
                storeNo = item['storeNo']
                title = item['title']
                content = item['content']
                division = item['division']
            elif item['__typename'] == 'ReceiptDetailsTotal':
                receipt_total = float(item['total'][1:])
            elif item['__typename'] == 'ReceiptDetailsFooter':
                receipt_date = item['transactionDetails'][-10:]
            elif item['__typename'] == 'ReceiptDetailsItems':
                skip_to = 0
                for i, e in enumerate(item['items']):
                    item_qty = 0
                    item_unit = ''
                    if i < skip_to:
                        continue
                    if e['amount'] == '':
                        skip_to = i + 2
                        try:
                            next_item = item['items'][i + 1]
                        except IndexError:
                            if 'PRICE REDUCED' in e['description'] or next_item['description']:
                                break
                            else:
                                print(IndexError)
                        if 'PRICE REDUCED' in e['description']:
                            skip_to = i + 1
                            continue

                        if 'Qty' in next_item['description']:
                            item_qty = float(next_item['description'].split(" ")[1])
                        elif 'NET @' in next_item['description']:
                            item_qty = float(next_item['description'].split(" ")[0])
                            item_unit = next_item['description'].split(" ")[1]

                        item_name = e['description']
                        item_total = float(next_item['amount'])

                        # print('------------')
                        # print(e['description'], e['amount'])
                        # print(item_qty)
                        # print(next_item['description'], next_item['amount'])
                        # print('------------')
                        receipt_items.append((receipt_id,item_name,item_qty,item_unit,item_total,raw_data))
                        total += float(next_item['amount'])

                    elif 'PRICE REDUCED' in e['description']:
                        skip_to = i + 1
                        continue
                    else:
                        # print(e['description'], e['amount'])
                        item_name = e['description']
                        item_total = float(e['amount'])
                        item_qty = 1
                        item_unit = ''

                        receipt_items.append((receipt_id,item_name,item_qty,item_unit,item_total,raw_data))
                        total += float(e['amount'])

    except KeyError as e:
        with open('data/error.txt','a+') as error_file:
            error_file.writelines(f'{receipt_id} - Key error at {e}\n')

    branch = (storeNo,title,content,division)
    receipt_info = (receipt_id,receipt_url,receipt_date,receipt_total,storeNo,raw_data)

    return [branch,receipt_info,receipt_items]
    # print('*********', receipt_date, receipt_total, "|", round(total, 2), '*********')
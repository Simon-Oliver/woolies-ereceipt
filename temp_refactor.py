import json
import db_util

with open('data/receipt-items-20230103213809.json') as file:
    receipt_list = json.load(file)


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
            except IndexError as e:
                if 'PRICE REDUCED' in e['description'] or next_item['description']:
                    break
                else:
                    print(e)
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

            receipt_items.append((receipt_id, item_name, item_qty, item_unit, item_total, raw_data))

        elif 'PRICE REDUCED' in e['description']:
            skip_to = i + 1
            continue
        else:
            item_name = e['description']
            item_total = float(e['amount'])
            item_qty = 1
            item_unit = ''

            receipt_items.append((receipt_id, item_name, item_qty, item_unit, item_total, raw_data))

    return receipt_items


def get_data(receipt_id, items):
    # receipt_id,receipt_date,receipt_total,store_no,raw_data
    receipt_date = ''
    receipt_total = ''
    raw_data = json.dumps(items)
    receipt_url = ''

    receipt_items = []

    try:
        for item in items['data']['receiptDetails']['details']:
            # print(json.dumps(item, indent=4))
            if item['__typename'] == 'ReceiptDetailsHeader':
                branch = get_branch_data(item)
                store_no = branch[0]
            elif item['__typename'] == 'ReceiptDetailsTotal':
                receipt_total = float(item['total'][1:])
            elif item['__typename'] == 'ReceiptDetailsFooter':
                receipt_date = item['transactionDetails'][-10:]
            elif item['__typename'] == 'ReceiptDetailsItems':
                receipt_items = get_list_of_line_items(receipt_id, item)

    except KeyError as e:
        with open('data/error.txt', 'a+') as error_file:
            error_file.writelines(f'{receipt_id} - Key error at {e}\n')

    receipt_info = (receipt_id, receipt_url, receipt_date, receipt_total, store_no, raw_data)

    return [branch, receipt_info, receipt_items]


data = get_data('test123', receipt_list[7])
print(data[0])
# print([item[0:2] for item in data[2]])

# print(data[2])

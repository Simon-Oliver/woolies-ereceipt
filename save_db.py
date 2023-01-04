import sqlite3
import json
import re
import db_util

# with open('receipts.json') as f:
#     data = json.load(f)
#     receipts = data['data']['rewardsActivityFeed']['list']['groups'][1:-1]
#     print(receipts)

with open('data/data.json') as f:
    data = json.load(f)
    # first_re = data[0]
    # receipt_url = first_re['data']['receiptDetails']['download']['url']
    # receipt_total = ''
    # storeNo = ''
    # storetitle = ''
    # storeAdr = ''

    items = []

    # print(data[0]['data']['receiptDetails']['details'])
    # print(json.dumps(first_re['data']['receiptDetails']['details'],indent=4))



    for x in data:
        total = 0;
        # storeNo,title,content,division
        storeNo = ''
        title = ''
        content = ''
        division = ''

        # receipt_id,receipt_date,receipt_total,storeNo,raw_data
        receipt_id = ''
        receipt_date = ''
        receipt_total = ''
        raw_data = x

        # receipt_id,item_name,item_qty,item_unit,item_total,raw_data
        item_name = ''
        item_qty = ''
        item_unit = ''
        item_total = ''

        for item in x['data']['receiptDetails']['details']:
            # print(json.dumps(x['data']['receiptDetails']['details'], indent=4))
            if item['__typename'] == 'ReceiptDetailsHeader':
                storeNo = item['storeNo']
                title = item['title']
                content = item['content']
                division = item['division']
            elif item['__typename'] == 'ReceiptDetailsTotal':
                receipt_total = item['total']
            elif item['__typename'] == 'ReceiptDetailsFooter':
                receipt_date = item['transactionDetails'][-10:]
            elif item['__typename'] == 'ReceiptDetailsItems':
                skip_to = 0

                for i, e in enumerate(item['items']):
                    if i < skip_to:
                        continue
                    if e['amount'] == '':
                        skip_to = i + 2
                        try:
                            next_item = item['items'][i + 1]
                        except IndexError:
                            if 'PRICE REDUCED' in next_item['description']:
                                break
                            else:
                                print(IndexError)
                        if 'PRICE REDUCED' in e['description']:
                            skip_to = i + 1
                            continue

                        if 'Qty' in next_item['description']:
                            item_qty = next_item['description'].split(" ")[1]
                        elif 'NET @' in next_item['description']:
                            item_qty = next_item['description'].split(" ")[0:2]

                        print('------------')
                        print(e['description'], e['amount'])
                        print(item_qty)
                        print(next_item['description'], next_item['amount'])
                        print('------------')
                        total += float(next_item['amount'])

                    elif 'PRICE REDUCED' in e['description']:
                        skip_to = i + 1
                        continue
                    else:
                        print(e['description'], e['amount'])
                        total += float(e['amount'])

        print('*********', receipt_date ,receipt_total, "|", round(total,2) ,'*********')




                # for e in item['items']:
                #     if not e['amount'] == '':
                #         print(e['description'], e['amount'])
                #     else:
                #         print('-------------')
                #         print(e['description'])
                #         next(iter(item['items']))
                #         print(e['description'], e['amount'])
                #         print('-------------')

# print(storetitle)
# print(receipt_total)

    # print(json.dumps(first_re['data']['receiptDetails']['details'],indent=4))
    # print(json.dumps(data[0], indent=4))

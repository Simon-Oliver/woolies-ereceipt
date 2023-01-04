import download
import os
import json
import db_util
import db

db.initialise_db()

download.refresh_token(os.environ.get("REFRESH_TOKEN"))
res = download.get_list()

# with open('data/receipt-list-20230103213809.json') as f:
#     res = json.load(f)

receipt_list = db_util.get_receipts_from_response(res)
# receipt_list = res

# with open('data/receipt-items-20230103213809.json') as r_f:
#     receipt_items_list = json.load(r_f)


new_receipts = db_util.get_new_receipt_ids(receipt_list)


# for receipt in receipt_list:
for index, receipt in enumerate(receipt_list):
    if receipt['id'] in new_receipts:
        receipt_res = download.get_receipt(receipt['receipt']['receiptId'])
        # receipt_res = receipt_items_list[index]
        branch,receipt_info,receipt_items = db_util.get_data(receipt['id'],receipt_res)

        # print(receipt_info)
        db_util.add_receipt(*receipt_info)
        db_util.add_branch(*branch)

        for item in receipt_items:
            # print('----',item[0:5])
            db_util.add_item(*item)

db_util.commit_close()
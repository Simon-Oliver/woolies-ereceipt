import download
import os
import json
import db_util

download.refresh_token(os.environ.get("REFRESH_TOKEN"))
res = download.get_list()

receipt_list = db_util.get_receipts_from_response(res)

for receipt in receipt_list:
    receipt_res = download.get_receipt(receipt['receipt']['receiptId'])
    branch,receipt_info,receipt_items = db_util.get_data(receipt['id'],receipt_res)
    print(receipt_info)
    db_util.add_receipt(*receipt_info)
    db_util.add_branch(*branch)

    for item in receipt_items:
        db_util.add_item(*item)

db_util.commit_close()
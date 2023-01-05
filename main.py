import download
import os
import db_util
import db

db.initialise_db()

download.refresh_token(os.environ.get("REFRESH_TOKEN"))
res = download.get_list()

receipt_list = db_util.get_receipts_from_response(res)

new_receipts = db_util.get_new_receipt_ids(receipt_list)
print(f'Found {len(new_receipts)} new receipts.')
for index, receipt in enumerate(receipt_list):
    if receipt['id'] in new_receipts:
        receipt_res = download.get_receipt(receipt['receipt']['receiptId'])

        branch, receipt_info, receipt_items = db_util.get_data(receipt['id'], receipt_res)
        db_util.add_receipt(*receipt_info)
        db_util.add_branch(*branch)

        for item in receipt_items:
            db_util.add_item(*item)

        print(f'Saved Receipt {receipt["id"]}')

db_util.commit_close()

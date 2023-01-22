import os
from utils import db_util, download

db_util.initialise_db()

download.refresh_token()
res = download.get_list_of_receipts()

receipt_list = db_util.get_receipts_from_response(res)
print(f'Found {len(receipt_list)} receipts.')

new_receipts = db_util.get_new_receipt_ids(receipt_list)
# The below line is used for the initialisation of the db.
# This is neccessary because ID's were not unique for a period of time
# new_receipts = [item['id'] for item in receipt_list]

print(f'{len(new_receipts)} are new receipts.')
for index, receipt in enumerate(receipt_list):
    if receipt['id'] in new_receipts:
        receipt_res = download.get_receipt_by_id(receipt['receipt']['receiptId'])

        branch, receipt_info, receipt_items = db_util.get_data(receipt['id'], receipt_res)
        db_util.add_receipt(*receipt_info)
        db_util.add_branch(*branch)

        for item in receipt_items:
            db_util.add_item(*item)

        print(f'{index}: Saved Receipt {receipt["id"]}')

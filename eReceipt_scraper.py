import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()

receipt_url = 'https://prod.mobile-api.woolworths.com.au/zeus/metis/v1/rewards/graphql'
token_url = 'https://prod.mobile-api.woolworths.com.au/zeus/metis/v1/rewards/token'

bearer_token = f"Bearer {os.environ.get('ACCESS_TOKEN')}"

headers = {"Content-Type": "application/json; charset=utf-8","authorization":bearer_token,"x-api-key":os.environ.get("API_KEY")}

# Opening JSON file
f = open('receipts.json')

# returns JSON object as
# a dictionary
data = json.load(f)
receipts = data['data']['rewardsActivityFeed']['list']['groups'][1:-1]
jsonString =[]

for receipt in receipts:
    for item in receipt['items']:
        try:
            receipt_query = {
                "query": "query ReceiptDetails($receiptId: String!) {\n    receiptDetails(receiptId: $receiptId) {\n        download {\n    url\n    filename\n}\ndetails {\n    ...on ReceiptDetailsHeader {\n        __typename\niconUrl\ntitle\ncontent\nstoreNo\ndivision\n    }\n    ...on ReceiptDetailsTotal {\n        __typename\n        total\n    }\n    ...on ReceiptDetailsSavings {\n        __typename\n        savings\n    }\n    ...on ReceiptDetailsFooter {\n        __typename\nbarcode {\n    value\n    type\n}\ntransactionDetails\nabnAndStore\n    }\n    ...on ReceiptDetailsItems {\n        __typename\nheader {\n    ...receiptLineItem\n}\nitems {\n    ...receiptLineItem\n}\n    }\n    ...on ReceiptDetailsSummary {\n        __typename\ndiscounts {\n    ...receiptLineItem\n}\nsummaryItems {\n    ...receiptLineItem\n}\ngst {\n    ...receiptLineItem\n}\nreceiptTotal {\n    ...receiptLineItem\n}\n    }\n    ...on ReceiptDetailsPayments {\n        __typename\npayments {\n    details {\n        text\n    }\n    description\n    iconUrl\n    altText\n    amount\n}\n    }\n    ...on ReceiptDetailsInfo {\n        __typename\nheader {\n    ...receiptLineItem\n}\ninfo {\n    ...receiptLineItem\n}\n    }\n    ...on ReceiptDetailsCoupon {\n        __typename\nheaderImageUrl\nsections {\n    sectionTitle\n    details\n}\nfooter\nbarcode {\n    value\n    type\n}\n    }\n}\n    }\n}\n\nfragment receiptLineItem on ReceiptDetailsLineItem {\n    prefixChar\n    description\n    amount\n}",
                "variables": {
                    "receiptId": item['receipt']['receiptId'] }}
            response = requests.post(receipt_url, headers=headers, json=receipt_query)
            jsonString.append(response.json())

        except Exception as e:
            print(e)

with open("data.json", 'w') as fout:
    json.dump(jsonString , fout)
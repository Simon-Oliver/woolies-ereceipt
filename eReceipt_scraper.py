import dotenv
import requests
import json
import os
import sqlite3
from dotenv import load_dotenv
load_dotenv()

conn = sqlite3.connect("receipt_data.db")
c = conn.cursor()

receipt_url = 'https://prod.mobile-api.woolworths.com.au/zeus/metis/v1/rewards/graphql'
token_url = 'https://prod.mobile-api.woolworths.com.au/zeus/metis/v1/rewards/token'

def refresh_token(ref_token):
    refresh_header = {"Content-Type": "application/json; charset=utf-8", "x-api-key":os.environ.get("API_KEY")}
    refresh_body = {"refreshToken":ref_token}
    refresh_response = requests.post(token_url, headers=refresh_header, json=refresh_body)
    print(refresh_response.json())
    token_data = refresh_response.json()
    os.environ['REFRESH_TOKEN'] = token_data['data']['refreshToken']
    dotenv.set_key('.env', 'REFRESH_TOKEN', os.environ['REFRESH_TOKEN'])
    os.environ['ACCESS_TOKEN'] = token_data['data']['accessToken']
    dotenv.set_key('.env', 'ACCESS_TOKEN', os.environ['ACCESS_TOKEN'])

refresh_token(os.environ.get("REFRESH_TOKEN"))



# Opening JSON file
with open('receipts.json') as f:
    # returns JSON object as
    # a dictionary
    data = json.load(f)
    receipts = data['data']['rewardsActivityFeed']['list']['groups'][1:-1]
    jsonString =[]

def get_receipts():
    bearer_token = f"Bearer {os.environ.get('ACCESS_TOKEN')}"
    headers = {"Content-Type": "application/json; charset=utf-8", "authorization": bearer_token,
               "x-api-key": os.environ.get("API_KEY")}
    receipts_query = {"query":"query($page: Int) {\n    rewardsActivityFeed(pageNumber: $page) {\n        list {\n    groups {\n        ...on RewardsActivityFeedGroup {\n            __typename\n            id\n            title\n            items {\n                id\n                displayDate\n                description\n                message\n                \n                displayValue\n                iconUrl\n                receipt {\n                    receiptId\n                    analytics {\n                        partnerName\n                    }\n                }\n                transactionType\n                actionURL\n            }\n        }\n        ...on RewardsActivityBanner {\n  __typename\n  id\n  iconUrl\n  title\n  message\n  messageCta\n  action {\n    url\n    type\n  }\n  onDismissCoachMark {\n    text\n    anchor\n  }\n  analytics {\n    label\n  }\n}\n    }\n    actionableMessage {\n    message {\n    iconUrl\n    title\n    message\n}\nbottomSheet {\n    title\n    items {\n        iconUrl\n        text\n    }\n    dismissButtonLabel\n    helpCta {\n        label\n        url\n    }\n}\n}\n    pageInfo {\n    nextPage\n}\n}\nallFilterMessage {\n    message {\n    iconUrl\n    title\n    message\n}\nbottomSheet {\n    title\n    items {\n        iconUrl\n        text\n    }\n    dismissButtonLabel\n    helpCta {\n        label\n        url\n    }\n}\n}\neReceiptsFilterMessage {\n    message {\n    iconUrl\n    title\n    message\n}\nbottomSheet {\n    title\n    items {\n        iconUrl\n        text\n    }\n    dismissButtonLabel\n    helpCta {\n        label\n        url\n    }\n}\n}\n    }\n    pointsBalance: rewardsHomePage {\n    balance {\n        pointsBalance {\n            pointsBalance\n            redemptionPercentage\n            displayMessage\n            statusMarkUrl\n            showStatusMark\n         }\n    }\n}\n}","variables":{"page":1}}
    receipts_response = requests.post(receipt_url, headers=headers, json=receipts_query)
    print(receipts_response.json())
    return receipts_response.json()

query = "SELECT receipt_id FROM receipt"

c.execute(query)
data = c.fetchall()
receipt_ids = [item[0] for item in data]

# for receipt in receipts:
#     for item in receipt['items']:
#         try:
#             if item['receipt']:
#                 receipt_ids.append(item['id'])
#         except Exception as e:
#             print(e)

print(receipt_ids)

new_items = []
data_new_receipts = get_receipts()
for r in data_new_receipts['data']['rewardsActivityFeed']['list']['groups'][1:-1]:
    for item in r['items']:
        try:
            if item['receipt']:
                new_items.append(item['id'])
        except Exception as e:
            print(e)

print(new_items)
print('Old Items', len(set(receipt_ids)))
print('New Items',len(set(new_items)))
print("Overlap",set(new_items).difference(set(receipt_ids)))



# with open("test_token.json") as token_file:
#     token_data = json.load(token_file)
#     os.environ['TEST_REFRESH'] = token_data['data']['refreshToken']
#     dotenv.set_key('.env', 'TEST_REFRESH', os.environ['TEST_REFRESH'])
#     os.environ['TEST_ACCESS'] = token_data['data']['accessToken']
#     dotenv.set_key('.env', 'TEST_ACCESS', os.environ['TEST_ACCESS'])


# for receipt in receipts:
#     for item in receipt['items']:
#         try:
#             receipt_query = {
#                 "query": "query ReceiptDetails($receiptId: String!) {\n    receiptDetails(receiptId: $receiptId) {\n        download {\n    url\n    filename\n}\ndetails {\n    ...on ReceiptDetailsHeader {\n        __typename\niconUrl\ntitle\ncontent\nstoreNo\ndivision\n    }\n    ...on ReceiptDetailsTotal {\n        __typename\n        total\n    }\n    ...on ReceiptDetailsSavings {\n        __typename\n        savings\n    }\n    ...on ReceiptDetailsFooter {\n        __typename\nbarcode {\n    value\n    type\n}\ntransactionDetails\nabnAndStore\n    }\n    ...on ReceiptDetailsItems {\n        __typename\nheader {\n    ...receiptLineItem\n}\nitems {\n    ...receiptLineItem\n}\n    }\n    ...on ReceiptDetailsSummary {\n        __typename\ndiscounts {\n    ...receiptLineItem\n}\nsummaryItems {\n    ...receiptLineItem\n}\ngst {\n    ...receiptLineItem\n}\nreceiptTotal {\n    ...receiptLineItem\n}\n    }\n    ...on ReceiptDetailsPayments {\n        __typename\npayments {\n    details {\n        text\n    }\n    description\n    iconUrl\n    altText\n    amount\n}\n    }\n    ...on ReceiptDetailsInfo {\n        __typename\nheader {\n    ...receiptLineItem\n}\ninfo {\n    ...receiptLineItem\n}\n    }\n    ...on ReceiptDetailsCoupon {\n        __typename\nheaderImageUrl\nsections {\n    sectionTitle\n    details\n}\nfooter\nbarcode {\n    value\n    type\n}\n    }\n}\n    }\n}\n\nfragment receiptLineItem on ReceiptDetailsLineItem {\n    prefixChar\n    description\n    amount\n}",
#                 "variables": {
#                     "receiptId": item['receipt']['receiptId'] }}
#             bearer_token = f"Bearer {os.environ.get('ACCESS_TOKEN')}"
#             headers = {"Content-Type": "application/json; charset=utf-8","authorization":bearer_token,"x-api-key":os.environ.get("API_KEY")}
#             response = requests.post(receipt_url, headers=headers, json=receipt_query)
#             jsonString.append(response.json())
#
#         except Exception as e:
#             print(e)
#
# with open("data.json", 'w') as fout:
#     json.dump(jsonString , fout)
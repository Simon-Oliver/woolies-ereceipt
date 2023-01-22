from utils import db_util, download
import requests
from datetime import datetime
import os
import json

receipt_url = 'https://prod.mobile-api.woolworths.com.au/zeus/metis/v1/rewards/graphql'
token_url = 'https://prod.mobile-api.woolworths.com.au/zeus/metis/v1/rewards/token'

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
token_file = os.path.join(ROOT_DIR, 'data', 'token.json')


def save_raw_json_to_file():
    refresh_token()
    res = get_list_of_receipts()

    # get current date and time
    current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")

    receipt_list = db_util.get_receipts_from_response(res)

    with open(token_file, 'r') as f:
        token = json.loads(f.read())
        api_key = token['API_KEY']
        access_token = token['ACCESS_TOKEN']

    with open(f'data/receipt-list-{current_datetime}.json', 'w+') as file:
        json.dump(receipt_list, file)

    receipt_items = []

    for item in receipt_list:
        try:
            receipt_query = {
                "query": "query ReceiptDetails($receiptId: String!) {\n    receiptDetails(receiptId: $receiptId) {\n  "
                         "      download {\n    url\n    filename\n}\ndetails {\n    ...on ReceiptDetailsHeader {\n   "
                         "     __typename\niconUrl\ntitle\ncontent\nstoreNo\ndivision\n    }\n    ...on "
                         "ReceiptDetailsTotal {\n        __typename\n        total\n    }\n    ...on "
                         "ReceiptDetailsSavings {\n        __typename\n        savings\n    }\n    ...on "
                         "ReceiptDetailsFooter {\n        __typename\nbarcode {\n    value\n    "
                         "type\n}\ntransactionDetails\nabnAndStore\n    }\n    ...on ReceiptDetailsItems {\n        "
                         "__typename\nheader {\n    ...receiptLineItem\n}\nitems {\n    ...receiptLineItem\n}\n    "
                         "}\n    ...on ReceiptDetailsSummary {\n        __typename\ndiscounts {\n    "
                         "...receiptLineItem\n}\nsummaryItems {\n    ...receiptLineItem\n}\ngst {\n    "
                         "...receiptLineItem\n}\nreceiptTotal {\n    ...receiptLineItem\n}\n    }\n    ...on "
                         "ReceiptDetailsPayments {\n        __typename\npayments {\n    details {\n        text\n    "
                         "}\n    description\n    iconUrl\n    altText\n    amount\n}\n    }\n    ...on "
                         "ReceiptDetailsInfo {\n        __typename\nheader {\n    ...receiptLineItem\n}\ninfo {\n    "
                         "...receiptLineItem\n}\n    }\n    ...on ReceiptDetailsCoupon {\n        "
                         "__typename\nheaderImageUrl\nsections {\n    sectionTitle\n    details\n}\nfooter\nbarcode {"
                         "\n    value\n    type\n}\n    }\n}\n    }\n}\n\nfragment receiptLineItem on "
                         "ReceiptDetailsLineItem {\n    prefixChar\n    description\n    amount\n}",
                "variables": {
                    "receiptId": item['receipt']['receiptId']}}
            bearer_token = f"Bearer {access_token}"
            headers = {"Content-Type": "application/json; charset=utf-8", "authorization": bearer_token,
                       "x-api-key": api_key}
            response = requests.post(receipt_url, headers=headers, json=receipt_query)
            receipt_items.append(response.json())

        except Exception as e:
            print(e)

    with open(f'data/receipt-items-{current_datetime}.json', 'w+') as file:
        json.dump(receipt_items, file)


# def refresh_token(ref_token: str):
def refresh_token():
    with open(token_file, 'r') as f:
        token = json.loads(f.read())
        api_key = token['API_KEY']
        ref_token = token["REFRESH_TOKEN"]

    refresh_header = {"Content-Type": "application/json; charset=utf-8", "x-api-key": api_key}

    refresh_body = {"refreshToken": ref_token}
    refresh_response = requests.post(token_url, headers=refresh_header, json=refresh_body)
    print(refresh_response.json())
    token_data = refresh_response.json()
    token['ACCESS_TOKEN'] = token_data['data']['accessToken']
    token["REFRESH_TOKEN"] = token_data['data']['refreshToken']
    with open(token_file, 'w') as f:
        f.write(json.dumps(token))


def get_list_of_receipts():
    with open(token_file, 'r') as f:
        token = json.loads(f.read())
        api_key = token['API_KEY']
        access_token = token['ACCESS_TOKEN']

    bearer_token = f"Bearer {access_token}"
    headers = {"Content-Type": "application/json; charset=utf-8", "authorization": bearer_token,
               "x-api-key": api_key}
    receipts_query = {
        "query": "query($page: Int) {\n    rewardsActivityFeed(pageNumber: $page) {\n        list {\n    groups {\n   "
                 "     ...on RewardsActivityFeedGroup {\n            __typename\n            id\n            title\n  "
                 "          items {\n                id\n                displayDate\n                description\n   "
                 "             message\n                \n                displayValue\n                iconUrl\n     "
                 "           receipt {\n                    receiptId\n                    analytics {\n              "
                 "          partnerName\n                    }\n                }\n                transactionType\n  "
                 "              actionURL\n            }\n        }\n        ...on RewardsActivityBanner {\n  "
                 "__typename\n  id\n  iconUrl\n  title\n  message\n  messageCta\n  action {\n    url\n    type\n  }\n "
                 " onDismissCoachMark {\n    text\n    anchor\n  }\n  analytics {\n    label\n  }\n}\n    }\n    "
                 "actionableMessage {\n    message {\n    iconUrl\n    title\n    message\n}\nbottomSheet {\n    "
                 "title\n    items {\n        iconUrl\n        text\n    }\n    dismissButtonLabel\n    helpCta {\n   "
                 "     label\n        url\n    }\n}\n}\n    pageInfo {\n    nextPage\n}\n}\nallFilterMessage {\n    "
                 "message {\n    iconUrl\n    title\n    message\n}\nbottomSheet {\n    title\n    items {\n        "
                 "iconUrl\n        text\n    }\n    dismissButtonLabel\n    helpCta {\n        label\n        url\n   "
                 " }\n}\n}\neReceiptsFilterMessage {\n    message {\n    iconUrl\n    title\n    "
                 "message\n}\nbottomSheet {\n    title\n    items {\n        iconUrl\n        text\n    }\n    "
                 "dismissButtonLabel\n    helpCta {\n        label\n        url\n    }\n}\n}\n    }\n    "
                 "pointsBalance: rewardsHomePage {\n    balance {\n        pointsBalance {\n            "
                 "pointsBalance\n            redemptionPercentage\n            displayMessage\n            "
                 "statusMarkUrl\n            showStatusMark\n         }\n    }\n}\n}",
        "variables": {"page": 1}}
    receipts_response = requests.post(receipt_url, headers=headers, json=receipts_query)
    return receipts_response.json()


def get_receipt_by_id(receipt_id):
    with open(token_file, 'r') as f:
        token = json.loads(f.read())
        api_key = token['API_KEY']
        access_token = token['ACCESS_TOKEN']
    try:
        receipt_query = {
            "query": "query ReceiptDetails($receiptId: String!) {\n    receiptDetails(receiptId: $receiptId) {\n      "
                     "  download {\n    url\n    filename\n}\ndetails {\n    ...on ReceiptDetailsHeader {\n        "
                     "__typename\niconUrl\ntitle\ncontent\nstoreNo\ndivision\n    }\n    ...on ReceiptDetailsTotal {"
                     "\n        __typename\n        total\n    }\n    ...on ReceiptDetailsSavings {\n        "
                     "__typename\n        savings\n    }\n    ...on ReceiptDetailsFooter {\n        "
                     "__typename\nbarcode {\n    value\n    type\n}\ntransactionDetails\nabnAndStore\n    }\n    "
                     "...on ReceiptDetailsItems {\n        __typename\nheader {\n    ...receiptLineItem\n}\nitems {\n "
                     "   ...receiptLineItem\n}\n    }\n    ...on ReceiptDetailsSummary {\n        "
                     "__typename\ndiscounts {\n    ...receiptLineItem\n}\nsummaryItems {\n    "
                     "...receiptLineItem\n}\ngst {\n    ...receiptLineItem\n}\nreceiptTotal {\n    "
                     "...receiptLineItem\n}\n    }\n    ...on ReceiptDetailsPayments {\n        __typename\npayments "
                     "{\n    details {\n        text\n    }\n    description\n    iconUrl\n    altText\n    "
                     "amount\n}\n    }\n    ...on ReceiptDetailsInfo {\n        __typename\nheader {\n    "
                     "...receiptLineItem\n}\ninfo {\n    ...receiptLineItem\n}\n    }\n    ...on ReceiptDetailsCoupon "
                     "{\n        __typename\nheaderImageUrl\nsections {\n    sectionTitle\n    "
                     "details\n}\nfooter\nbarcode {\n    value\n    type\n}\n    }\n}\n    }\n}\n\nfragment "
                     "receiptLineItem on ReceiptDetailsLineItem {\n    prefixChar\n    description\n    amount\n}",
            "variables": {
                "receiptId": receipt_id}}
        bearer_token = f"Bearer {access_token}"
        headers = {"Content-Type": "application/json; charset=utf-8", "authorization": bearer_token,
                   "x-api-key": api_key}
        response = requests.post(receipt_url, headers=headers, json=receipt_query)
        return response.json()

    except Exception as e:
        print(e)


def fetch_new_data():
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

    return json.dumps({'status': 'success', 'message': f'{new_receipts} new receipts saved'})

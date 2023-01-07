import dotenv
import json
import db_util
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

receipt_url = 'https://prod.mobile-api.woolworths.com.au/zeus/metis/v1/rewards/graphql'
token_url = 'https://prod.mobile-api.woolworths.com.au/zeus/metis/v1/rewards/token'

def save_raw_json_to_file():
    refresh_token(os.environ.get("REFRESH_TOKEN"))
    res = get_list_of_receipts()

    # get current date and time
    current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")

    receipt_list = db_util.get_receipts_from_response(res)

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
            bearer_token = f"Bearer {os.environ.get('ACCESS_TOKEN')}"
            headers = {"Content-Type": "application/json; charset=utf-8", "authorization": bearer_token,
                       "x-api-key": os.environ.get("API_KEY")}
            response = requests.post(receipt_url, headers=headers, json=receipt_query)
            receipt_items.append(response.json())

        except Exception as e:
            print(e)

    with open(f'data/receipt-items-{current_datetime}.json', 'w+') as file:
        json.dump(receipt_items, file)


def refresh_token(ref_token: str):
    refresh_header = {"Content-Type": "application/json; charset=utf-8", "x-api-key": os.environ.get("API_KEY")}
    refresh_body = {"refreshToken": ref_token}
    refresh_response = requests.post(token_url, headers=refresh_header, json=refresh_body)
    print(refresh_response.json())
    token_data = refresh_response.json()
    os.environ['REFRESH_TOKEN'] = token_data['data']['refreshToken']
    dotenv.set_key('.env', 'REFRESH_TOKEN', os.environ['REFRESH_TOKEN'])
    os.environ['ACCESS_TOKEN'] = token_data['data']['accessToken']
    dotenv.set_key('.env', 'ACCESS_TOKEN', os.environ['ACCESS_TOKEN'])


def get_list_of_receipts():
    bearer_token = f"Bearer {os.environ.get('ACCESS_TOKEN')}"
    headers = {"Content-Type": "application/json; charset=utf-8", "authorization": bearer_token,
               "x-api-key": os.environ.get("API_KEY")}
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
        bearer_token = f"Bearer {os.environ.get('ACCESS_TOKEN')}"
        headers = {"Content-Type": "application/json; charset=utf-8", "authorization": bearer_token,
                   "x-api-key": os.environ.get("API_KEY")}
        response = requests.post(receipt_url, headers=headers, json=receipt_query)
        return response.json()

    except Exception as e:
        print(e)

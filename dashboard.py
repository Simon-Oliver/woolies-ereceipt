from flask import Flask, request, jsonify, render_template
from utils import db_util, download
import subprocess
import json


app = Flask(__name__, template_folder='client/templates', static_folder='client/static')


@app.route('/')
def index():
    data = db_util.get_all_receipts()
    annual_total = format(round(db_util.get_annual_expenses()[0][0], 2), '.2f')
    current_month, last_month = db_util.get_last_two_months()
    return render_template('test.html', data=data, annual_total=annual_total, current_month=current_month,
                           last_month=last_month)


@app.route('/items')
def get_items():
    receipt_id = request.args['id']
    data = db_util.get_items_by_receipt_id(receipt_id)
    return jsonify(data)


@app.route('/products')
def get_products():
    data = db_util.get_products()
    return jsonify(data)


@app.route('/refresh')
def tester():

    message = download.fetch_new_data()

    # test_id = request.args['id']
    # with open('./data/test.json', 'r') as file:
    #     data_string = file.read()
    #
    # json_dict = json.loads(data_string)
    # json_dict['TEST_TOKEN'] = test_id
    #
    # with open('./data/test.json', 'w') as out_file:
    #     out_file.write(json.dumps(json_dict))
    #
    # print('Returning')
    return jsonify(message)


@app.route('/message')
def generate_random():
    return jsonify('Hello World')


if __name__ == '__main__':
    app.run()

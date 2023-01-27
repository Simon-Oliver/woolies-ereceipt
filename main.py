from flask import Flask, request, jsonify, render_template
from utils import db_util, download

app = Flask(__name__, template_folder='client/templates', static_folder='client/static')


@app.route('/')
def index():
    data = db_util.get_all_receipts()
    annual_total = format(round(db_util.get_annual_expenses()[0][0], 2), '.2f')
    current_month, last_month = db_util.get_last_two_months()
    return render_template('dashboard.html', data=data, annual_total=annual_total, current_month=current_month,
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
def refresh():
    message = download.fetch_new_data()
    return jsonify(message)


if __name__ == '__main__':
    app.run()

from flask import Flask, request, jsonify, render_template
import db_util

app = Flask(__name__, template_folder='client/templates', static_folder='client/static')

@app.route('/')
def index():
    data = db_util.get_all_receipts()
    annual_total = round(db_util.get_annual_expenses()[0][0],2)
    return render_template('test.html',data=data, annual_total=annual_total)

@app.route('/items')
def get_items():
    receipt_id = request.args['id']
    data = db_util.get_items_by_receipt_id(receipt_id)
    return jsonify(data)

@app.route('/test')
def console_log():
    print('Logging')
    print(request.args['name'])
    return jsonify('aces')


@app.route('/message')
def generate_random():
    return jsonify('Hello World')

if __name__ == '__main__':
    app.run()

from flask import Flask, request, jsonify, render_template
import db_util

app = Flask(__name__, template_folder='client/templates')

@app.route('/')
def index():
    data = db_util.get_total_expenses_by_month()
    return render_template('test.html',data=data)
@app.route('/test')
def console_log():
    print('Logging')
    print(request.args['name'])
    return "Aces"


@app.route('/message')
def generate_random():
    return jsonify('Hello World')

if __name__ == '__main__':
    app.run()

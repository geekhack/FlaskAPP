from flask import Flask, render_template, request, redirect, url_for,Response,make_response
from pymongo import MongoClient
import pandas as pd
from urllib.parse import quote  # Replaced url_quote with quote
import csv

app = Flask(__name__)

# MongoDB setup
client = MongoClient('127.0.0.1', 27017)
db = client['income_spending']
collection = db['user_data']

# Home route
@app.route('/',methods=['GET',])
def index():
    return render_template('index.html')

# Route to handle form submission
@app.route('/', methods=['POST'])
def submit_data():
    if request.method == 'POST':
        age = int(request.form['age'])
        gender = request.form['gender']
        total_income = float(request.form['total_income'])
        data = request.form
        # Collect expenses from checkboxes and text inputs
        utilities = bool(data.get('utilities',False))
        entertainment = bool(data.get('entertainment',False))
        school_fees = bool(data.get('school_fees',False))
        shopping = bool(data.get('shopping',False))
        healthcare = bool(data.get('healthcare',False))

        expenses = {}

        if utilities:
            expenses['utilities'] = float(data.get('utilities_amt',0))
        if entertainment: 
            expenses['entertainment'] = float(data.get('entertainment_amt',0))
        if school_fees: 
            expenses['school_fees'] = float(data.get('school_fees_amt',0))
        if shopping: 
            expenses['shopping'] = float(data.get('shopping_amt',0))
        if healthcare:
            expenses['healthcare'] = float(data.get('healthcare_amt',0))
        
        # Create user data
        user_data = {
            'age': age,
            'gender': gender,
            'total_income': total_income,
            **expenses
        }
        
        # Insert user data into MongoDB
        collection.insert_one(user_data)
        
        return redirect(url_for('index'))

# Route to export data to CSV and process in Jupyter notebook
@app.route('/export',methods=['GET'])
def export_data():
    # Fetch data from MongoDB
    exported_data = list(collection.find())
    data = pd.DataFrame(exported_data)
    
    # Processing: Calculate total spending
    data['total_spent'] = data[['utilities', 'entertainment', 'school_fees', 'shopping', 'healthcare']].sum(axis=1)
    
    
    response = make_response(data.to_csv( encoding='utf-8', index=False, header=True))
    response.headers["Content-Disposition"] = "attachment; filename=data.csv"
    response.headers["Content-type"] = "text/csv"
    return response

from werkzeug.middleware.proxy_fix import ProxyFix

app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='0.0.0.0')

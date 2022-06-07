import pandas as pd
import pymongo
from flask import Flask, request, render_template
TM = __import__('GRU-LGB')

app = Flask(__name__)

global Model
Model = TM.TwinModel()

client = pymongo.MongoClient("mongodb://localhost:27017/")
global mydb
mydb = client["flaskPython"]
global mycol
mycol = mydb["cows"]
global myquery

lastCol = ""

@app.route('/')
def index():
    return render_template('search.html')

@app.route('/search',  methods=['POST'])
def search():
    global myquery
    if request.method == "POST":
        input = request.form['input']
    
    myquery = { 'CowID': { "$regex": input } }
    data = mycol.find(myquery)
    data.sort("CowID", 1)

    return render_template('table.html', output_data = data)

@app.route('/item', methods=['POST'])
def flask_link():
    if request.method == "POST":
        knowMore = request.form['knowMore']

    myquery = { 'ID': knowMore }
    data = list(mycol.find(myquery))
    return render_template('knowMore.html', knowMoreHTML = data)

@app.route('/predict', methods=['POST'])
def predict():
    id = int(request.form['predict'])
    return render_template('result.html', result = str(Model.GetPredictFromID(id)[0]) )
        
@app.route('/sort', methods=['POST'])
def sort():
    global lastCol
    global myquery

    data = mycol.find(myquery)

    if request.method == "POST":
        col = request.form['col']
    if lastCol == col:
        lastCol = "null"
        data.sort(col, 1)

    else:   
        data.sort(col, -1)
        lastCol = col
    return render_template('table.html', output_data = data)

if __name__ == '__main__':
    #preprocess()
    app.run(debug=True)
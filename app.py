from flask import Flask, render_template, request, redirect
import datetime as dt
from urllib2 import urlopen
from json import load as Jload
import pandas as pd
from bokeh.plotting import figure, output_file, save
import numpy as np

app = Flask(__name__)

@app.route('/')
def main():
  return redirect('/index')

@app.route('/index')
def index():
  return render_template('index.html')

@app.route('/get_data', methods=['POST'])
def get_data():
    data = ExtractData(request.form['ticker'])
    graph_file = BuildGraph(data, request.form['ticker'])
    if graph_file:
        return render_template(graph_file)
    return 'ERROR: Data cannot be extracted. Check the ticker or try again later'


def BuildGraph(data, tick):
    if data.empty:
        return []
    output_file("./templates/graph.html", title='Closing prices')
    p = figure(
            tools="pan,box_zoom,reset,save", title='Closing price for last month',
            x_axis_label='Date', y_axis_label='Closing Price',
            x_axis_type='datetime'
            )
    try:
        dates = np.array(data['Date'], dtype=np.datetime64)
        p.line(dates, data['Close'], legend=tick)
        save(p)
        name = 'graph.html'
    except:
        name = ''
    return name


def ExtractData(ticker):
    days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    today = dt.date.today()
    nday = today.day
    nyear = today.year
    nmonth = today.month - 1
    if not nmonth:
        nmonth = 12
        nyear = nyear - 1
    if nday > days[nmonth]:
        nday = days[nmonth]
    start = '%d-%d-%d'%(nyear, nmonth, nday)
    stop = '%d-%d-%d'%(today.year, today.month, today.day)
    url = 'https://www.quandl.com/api/v3/datasets/WIKI/%s.json?start_date=%s&end_date=%s'%(ticker, start, stop)
    try:
        data = Jload(urlopen(url))['dataset']
        data = pd.DataFrame(data['data'], columns=data['column_names'])
    except:
        data = pd.DataFrame([])
    return data
    


if __name__ == '__main__':
  app.run(debug=True)

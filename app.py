#!/usr/bin/env python3
from flask import Flask, render_template, request, redirect
import Quandl
from bokeh.plotting import figure, show
from bokeh.models.sources import ColumnDataSource
from bokeh.embed import components
from bokeh.palettes import brewer
import pandas as pd
import itertools

app = Flask(__name__)

API_KEY = '1AMNY3TPnpsFSw6ejs7D'

@app.route('/')
def main():
  return redirect('/index')

@app.route('/index')
def index():
  return render_template('index.html')


@app.route('/plot', methods=['POST'])
def handle_input():
    tickers = request.form['ticker'].split()
    if len(tickers)==1:
        return redirect('/plot/'+tickers[0])
    else:
        stock_plot = gen_stock_plot("Stock Closing Price vs Time")
        not_found_list = []
        colours = get_colours(len(tickers))
        for t, c in zip(tickers, colours):
            try:
                _plot_stock(t, stock_plot, colour=c)
            except Quandl.Quandl.DatasetNotFound as e:
                not_founf_list.append(t)
        script, div = components(stock_plot)
        return render_template('graph.html', script=script, div=div,
                notfoundlist=", ".join(not_found_list))

@app.route('/plot/<ticker>')
def plot_stock(ticker):
    stock_plot = gen_stock_plot(ticker)
    try:
        _plot_stock(ticker, stock_plot)
    except Quandl.Quandl.DatasetNotFound as e:
        return render_template('graph.html', script="", div="Data set not\
                found: %s"%(ticker))

    script, div = components(stock_plot)
    return render_template('graph.html', script=script, div=div)

def gen_stock_plot(title):
    stock_plot = figure(width=1024,height=600,x_axis_type="datetime",
            title=title)
    stock_plot.yaxis.axis_label = "Closing Price"
    stock_plot.xaxis.axis_label = "Date"
    return(stock_plot)


def _plot_stock(ticker, plot, colour='blue'):
    data = Quandl.get('WIKI/'+ticker+'.4', authtoken=API_KEY)
    plot.line(data.index,data['Close'],legend=ticker,color=colour)

def get_colours(num):
    if num<3:
        return brewer["Spectral"][3][:num]
    elif num>11:
        return itertools.chain(brewer["Spectral"][11])
    else:
        return brewer["Spectral"][num]


if __name__ == '__main__':
  app.run(port=33507, debug=True)

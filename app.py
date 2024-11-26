from flask import Flask, render_template, request
from tvDatafeed import TvDatafeed, Interval
import pandas as pd
import plotly.graph_objs as go
import plotly
import json
from datetime import datetime, timedelta

app = Flask(__name__)

# Initialize TradingView DataFeed
tv = TvDatafeed()

@app.route('/', methods=['GET', 'POST'])
def index():
    # Initialize default values
    default_symbol = ''
    default_interval = '1d'
    default_start_date = ''
    default_end_date = ''
    graphJSON = None
    error = None

    if request.method == 'POST':
        # Get form inputs
        default_symbol = request.form['symbol'].upper()
        default_interval = request.form['interval']
        default_start_date = request.form['start_date']
        default_end_date = request.form['end_date']
        
        try:
            # Convert interval to TvDatafeed Interval enum
            interval_map = {
                '1m': Interval.in_1_minute,
                '5m': Interval.in_5_minute,
                '15m': Interval.in_15_minute,
                '30m': Interval.in_30_minute,
                '1h': Interval.in_1_hour,
                '4h': Interval.in_4_hour,
                '1d': Interval.in_daily
            }
            selected_interval = interval_map.get(default_interval, Interval.in_daily)
            
            # Parse date range
            start_date = datetime.strptime(default_start_date, '%Y-%m-%d')
            end_date = datetime.strptime(default_end_date, '%Y-%m-%d')
            
            # Fetch historical data. #Exchange is set to Binance, but this can be changed to any exchange like NSE/BSE and it will fetch stock prices
            data = tv.get_hist(symbol=default_symbol, exchange='BINANCE', interval=selected_interval, n_bars= 1000) #n_bars is the number of datapoints, max allowed is 5000
            
            # Filter data based on date range
            filtered_data = data[(data.index >= start_date) & (data.index <= end_date)]
            
            # Print date-wise values to console for debugging if required
            #print(f"\nDate-wise {default_symbol} Data between {start_date.date()} and {end_date.date()}:")
            #print("-" * 50)
            #for index, row in filtered_data.iterrows():
            #    print(f"Date: {index.date()}, Open: {row['open']}, High: {row['high']}, Low: {row['low']}, Close: {row['close']}, Volume: {row['volume']}")
            #print("-" * 50)
            
            # Create Plotly candlestick chart
            fig = go.Figure(data=[go.Candlestick(x=filtered_data.index,
                                                  open=filtered_data['open'],
                                                  high=filtered_data['high'],
                                                  low=filtered_data['low'],
                                                  close=filtered_data['close'])])
            
            # Customize layout
            fig.update_layout(
                title=f'{default_symbol} Candlestick Chart',
                yaxis_title='Price',
                xaxis_title='Date',
                template='plotly_white',
                height=600,
                margin=dict(l=50, r=50, t=50, b=50)
            )
            
            # Convert plot to JSON
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        except Exception as e:
            error = str(e)
    
    return render_template('index.html', 
                           symbol=default_symbol, 
                           interval=default_interval, 
                           start_date=default_start_date, 
                           end_date=default_end_date, 
                           graphJSON=graphJSON, 
                           error=error)

if __name__ == '__main__':
    app.run(debug=True, port=3000)
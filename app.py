from flask import Flask, render_template, request, redirect, url_for
from main import (
    get_stock_data,
    calculate_moving_averages,
    generate_signals,
    calculate_confidence,
    DEFAULT_TICKERS, # Now importing a LIST of default tickers
    DEFAULT_START_DATE,
    DEFAULT_END_DATE,
    SHORT_MA_WINDOW,
    LONG_MA_WINDOW
)

app = Flask(__name__)

@app.route('/')
def index():
    # Get tickers from request arguments, or use defaults
    tickers_param = request.args.get('tickers', ','.join(DEFAULT_TICKERS))
    tickers_to_scan = [t.strip().upper() for t in tickers_param.split(',') if t.strip()]

    start_date = DEFAULT_START_DATE
    end_date = DEFAULT_END_DATE

    all_ticker_signals = [] # List to hold structured signals for all tickers

    for ticker_symbol in tickers_to_scan:
        print(f"Analyzing {ticker_symbol}...")
        stock_data = get_stock_data(ticker_symbol, start_date, end_date)

        if stock_data is not None and not stock_data.empty:
            stock_data = calculate_moving_averages(stock_data, SHORT_MA_WINDOW, LONG_MA_WINDOW)

            # Ensure MAs have enough non-NaN values for signal generation
            if stock_data is not None and not stock_data[['short_ma', 'long_ma']].isnull().all().any():
                latest_signal_type, latest_data_point = generate_signals(stock_data)

                # Calculate confidence based on the latest data point and signal type
                confidence = calculate_confidence(stock_data, latest_data_point, latest_signal_type)

                all_ticker_signals.append({
                    'ticker': ticker_symbol,
                    'date': latest_data_point.name.strftime('%Y-%m-%d') if latest_data_point.name else 'N/A', # Use .name for index
                    'type': latest_signal_type,
                    'price': f"{latest_data_point['Close']:.2f}",
                    'short_ma': f"{latest_data_point['short_ma']:.2f}",
                    'long_ma': f"{latest_data_point['long_ma']:.2f}",
                    'confidence': confidence
                })
            else:
                all_ticker_signals.append({
                    'ticker': ticker_symbol,
                    'date': 'N/A',
                    'type': 'N/A (Insufficient Data)',
                    'price': 'N/A',
                    'short_ma': 'N/A',
                    'long_ma': 'N/A',
                    'confidence': 'Low'
                })
        else:
            all_ticker_signals.append({
                'ticker': ticker_symbol,
                'date': 'N/A',
                'type': 'N/A (No Data)',
                'price': 'N/A',
                'short_ma': 'N/A',
                'long_ma': 'N/A',
                'confidence': 'Very Low'
            })

    # Sort signals by ticker for consistent display
    all_ticker_signals.sort(key=lambda x: x['ticker'])

    return render_template('index.html',
                           tickers_to_scan=tickers_to_scan, # Pass the list of tickers
                           signals=all_ticker_signals,
                           short_window=SHORT_MA_WINDOW,
                           long_window=LONG_MA_WINDOW,
                           default_tickers_string=','.join(DEFAULT_TICKERS)) # For pre-filling input

@app.route('/scan', methods=['POST'])
def scan_tickers():
    tickers_input = request.form['tickers']
    return redirect(url_for('index', tickers=tickers_input))

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Assuming these are the paths to your CSV files
df_1h = pd.read_csv('1h_Crypto_Monitor_List.csv')
df_1d = pd.read_csv('1d_Crypto_Monitor_List.csv')
df_1w = pd.read_csv('1w_Crypto_Monitor_List.csv')

@app.route('/', methods=['GET'])
def index():
    # Retrieve sorting preferences from query parameters
    sort_by_symbol = request.args.get('sort_by_symbol', 'no')  # Default to not sorting by symbol
    sort_order = request.args.get('sort_order', 'asc') == 'asc'  # Default sort order is ascending

    columns_to_keep = ['Date', 'Category', 'Symbol', 'Signal', 'Extreme Signal']

    # Define a lambda to apply sorting logic based on parameters
    sort_logic = lambda df: df.sort_values(by='Symbol', ascending=sort_order) if sort_by_symbol == 'yes' else df.sort_values(by='Date', ascending=False)
    
    # Apply filtering and sorting based on parameters
    data_1h = sort_logic(df_1h[df_1h['Signal'] != 'Neutral'][columns_to_keep]).to_html(index=False)
    data_1d = sort_logic(df_1d[df_1d['Signal'] != 'Neutral'][columns_to_keep]).to_html(index=False)
    data_1w = sort_logic(df_1w[df_1w['Signal'] != 'Neutral'][columns_to_keep]).to_html(index=False)

    tables_with_titles = [
        {"title": "3 Hour Signal", "data_html": data_1h},
        {"title": "Daily Signal", "data_html": data_1d},
        {"title": "Weekly Signal", "data_html": data_1w}
    ]

    return render_template('index.html', tables_with_titles=tables_with_titles, sort_by_symbol=sort_by_symbol)

if __name__ == '__main__':
    app.run(debug=True)
print("Done")
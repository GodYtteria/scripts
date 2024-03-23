import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd

# Load the CSV files
daily_file_path = '1d_Crypto_Monitor_List.csv'  # Daily data file path
hourly_file_path = '1h_Crypto_Monitor_List.csv'  # Hourly data file path
weekly_file_path = '1w_Crypto_Monitor_List.csv'  # Weekly data file path

daily_data = pd.read_csv(daily_file_path)
hourly_data = pd.read_csv(hourly_file_path)
weekly_data = pd.read_csv(weekly_file_path)

# Convert 'Date' column to datetime if not already in datetime format
daily_data['Date'] = pd.to_datetime(daily_data['Date'])
hourly_data['Date'] = pd.to_datetime(hourly_data['Date'])
weekly_data['Date'] = pd.to_datetime(weekly_data['Date'])

# Sort the data by date
daily_data.sort_values('Date', inplace=True)
hourly_data.sort_values('Date', inplace=True)
weekly_data.sort_values('Date', inplace=True)

# Get unique symbols
symbols = daily_data['Symbol'].unique()

# Initialize the Dash app
app = dash.Dash(__name__)

def add_signal_markers(fig, data):
    strong_buy_signals = data[data['Signal'] == 'Buy']
    strong_sell_signals = data[data['Signal'] == 'Sell']
    
    fig.add_trace(go.Scatter(x=strong_buy_signals['Date'], y=strong_buy_signals['CLOSE'], mode='markers', name='Buy', marker=dict(color='green', symbol='x'), showlegend=True))
    fig.add_trace(go.Scatter(x=strong_sell_signals['Date'], y=strong_sell_signals['CLOSE'], mode='markers', name='Sell', marker=dict(color='red', symbol='x'), showlegend=True))

# App layout
app.layout = html.Div(children=[
    html.H1(children='Cryptocurrency Data Visualization'),
    
    dcc.Dropdown(
        id='symbol-dropdown',
        options=[{'label': symbol, 'value': symbol} for symbol in symbols],
        value=symbols[0]  # Default value
    ),
    
    dcc.Dropdown(
        id='data-dropdown',
        options=[
            {'label': 'Hourly Data', 'value': 'hourly'},
            {'label': 'Daily Data', 'value': 'daily'}, 
            {'label': 'Weekly Data', 'value': 'weekly'}
        ],
        value='hourly'  # Default value
    ),
    
    dcc.Graph(
        id='crypto-graph'
    )
])

# Callback to update the graph based on the selected dropdown options
@app.callback(
    Output('crypto-graph', 'figure'),
    [Input('symbol-dropdown', 'value'),
     Input('data-dropdown', 'value')]
)
def update_graph(selected_symbol, selected_data):
    if selected_data == 'hourly':
        data = hourly_data[hourly_data['Symbol'] == selected_symbol]
    elif selected_data == 'daily':
        data = daily_data[daily_data['Symbol'] == selected_symbol]
    elif selected_data == 'weekly':
        data = weekly_data[weekly_data['Symbol'] == selected_symbol]
    
    # Create the plot
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=data['Date'], y=data['OPEN'], mode='lines', name='Open'))
    fig.add_trace(go.Scatter(x=data['Date'], y=data['HIGH'], mode='lines', name='High'))
    fig.add_trace(go.Scatter(x=data['Date'], y=data['LOW'], mode='lines', name='Low'))
    fig.add_trace(go.Scatter(x=data['Date'], y=data['CLOSE'], mode='lines', name='Close'))
    
    # Add signal markers
    add_signal_markers(fig, data)
    
    fig.update_layout(title=f'{selected_symbol} Cryptocurrency Prices', xaxis_title='Date', yaxis_title='Price in USDT', height=800, margin=dict(t=0))  # Set height and remove top margin
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

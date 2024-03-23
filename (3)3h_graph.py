import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd

# Load the CSV file
file_path = '1h_Crypto_Monitor_List.csv'  # Make sure to update this path
data = pd.read_csv(file_path)
data['Date'] = pd.to_datetime(data['Date'])  # Convert 'Date' column to datetime if not already in datetime format
data.sort_values('Date', inplace=True)  # Sort the data by date

# Initialize the Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div(children=[
    html.H1(children='Cryptocurrency Data Visualization'),
    
    dcc.Dropdown(
        id='symbol-dropdown',
        options=[{'label': i, 'value': i} for i in data['Symbol'].unique()],
        value='BTC/USDT'  # Default value
    ),
    
    dcc.Graph(
        id='crypto-graph',
        config={'displayModeBar': False}  # Hide the plotly modebar
    )
])

# Callback to update the graph based on the selected symbol
@app.callback(
    Output('crypto-graph', 'figure'),
    [Input('symbol-dropdown', 'value')]
)
def update_graph(selected_symbol):
    filtered_data = data[data['Symbol'] == selected_symbol]
    
    # Create the plot
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=filtered_data['Date'], y=filtered_data['OPEN'], mode='lines', name='Open'))
    fig.add_trace(go.Scatter(x=filtered_data['Date'], y=filtered_data['HIGH'], mode='lines', name='High'))
    fig.add_trace(go.Scatter(x=filtered_data['Date'], y=filtered_data['LOW'], mode='lines', name='Low'))
    fig.add_trace(go.Scatter(x=filtered_data['Date'], y=filtered_data['CLOSE'], mode='lines', name='Close'))
    
    fig.update_layout(title='Cryptocurrency Prices', xaxis_title='Date', yaxis_title='Price in USDT', height=800)  # Set height here
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
print("Done")
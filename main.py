from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine
import numpy as np

engine = create_engine("mysql+mysqlconnector://admin:Harish1998@database-2-instance-1.c5egaggaqrm3.us-east-2.rds.amazonaws.com/stocks_db")
data = pd.read_sql("SELECT s.name, cs.symbol, cs.date, cs.closing_prices, cs.change_value FROM change_stock_data cs inner join symbols s on s.symbol=cs.symbol", engine)
# data

# convert closing_prices to numbers
data['closing_prices'] = data['closing_prices'].astype(float)

# Convert dataframe into a dataframe with columns date, symbols
pivot_df = pd.pivot_table(data, index='date', columns='symbol', values='closing_prices', aggfunc='first')
pivot_df.reset_index(inplace=True)
# Rename the newly added column to a desired name if needed
pivot_df.rename(columns={'index': 'date'}, inplace=True)

change_pivot = pd.pivot_table(data, index='date', columns='symbol', values='change_value', aggfunc='first')

# pivot_df.columns = ['date'] + list(pivot_df.columns)
print(pivot_df.columns)

print(pivot_df.head())

symbols = list(set(data["symbol"]))
# print(symbols)

app = Dash(__name__)
app.title = 'Stock Screener'

app.layout = html.Div([
    html.H1('Stock Screener'),
    html.P("Select stock:"),
    dcc.Dropdown(
            id="ticker",
            options=symbols,
            value=symbols[0],
            clearable=False,
        ),
    dcc.Graph(id="time-series-chart"),
    dcc.Graph(id="change-chart"),
])


@app.callback(
    Output("time-series-chart", "figure"),
    Input("ticker", "value"))
def display_time_series(ticker):
    df = pivot_df # replace with your own data source
    fig = px.line(df, x='date', y=ticker, title="Timeseries Plot", width=1800, height=800)
    fig.update_xaxes(rangeslider_visible=True, rangeselector=dict(
        buttons=list([
            dict(count=1, label="1m", step="month", stepmode="backward"),
            dict(count=6, label="6m", step="month", stepmode="backward"),
            dict(count=1, label="YTD", step="year", stepmode="todate"),
            dict(count=1, label="1y", step="year", stepmode="backward"),
            dict(step="all")
        ])))
    return fig

@app.callback(
    Output("change-chart", "figure"),
    Input("ticker", "value"))
def change_chart(ticker):
    df = change_pivot
    fig = px.bar(df, y=ticker, x=df.index, text_auto='.2s', title="%Change Data", width=1800, height=800)
    fig.update_xaxes(rangeslider_visible=True, rangeselector=dict(
        buttons=list([
            dict(count=1, label="1m", step="month", stepmode="backward"),
            dict(count=6, label="6m", step="month", stepmode="backward"),
            dict(count=1, label="YTD", step="year", stepmode="todate"),
            dict(count=1, label="1y", step="year", stepmode="backward"),
            dict(step="all")
        ])))
    fig.update_yaxes(
        autorange=True,
        fixedrange=False
    )
    color = np.where(df[ticker] < 0, 'red', 'green')
    # COLOR
    fig.update_traces(marker_color=color)
    return fig

app.run_server(debug=True)

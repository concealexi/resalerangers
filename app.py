import dash 
from dash import html, dcc, register_page, callback, Input, Output
from dash import Dash, page_container
import dash_table

external_stylesheets = [
    "https://fonts.googleapis.com/css2?family=Inter&display=swap",
    "https://unpkg.com/modern-css-reset/dist/reset.min.css"
]

app = Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    external_stylesheets=external_stylesheets
)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='manual-store', storage_type='session'),
    dcc.Store(id='guru-store', storage_type='session'),
    dcc.Store(id='user-filter-store', storage_type='session'),
    dcc.RadioItems(id='price-trend-toggle', style={'display': 'none'}),
    dcc.Graph(id='price-bar-chart', style={'display': 'none'}),
    html.Div(id='summary-stats', style={'display': 'none'}),
    dash_table.DataTable(id='transaction-table', columns=[], data=[], style_table={'display': 'none'}),
    page_container,
], style={
    'backgroundColor': 'white'
})

if __name__ == '__main__':
    app.run_server(debug=True)
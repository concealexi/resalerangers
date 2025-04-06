import dash 
from dash import html, dcc, register_page, callback, Input, Output
from dash import Dash, page_container

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
    page_container,
], style={
    'backgroundColor': 'white'
})

if __name__ == '__main__':
    app.run_server(debug=True)
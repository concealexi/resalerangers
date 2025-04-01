import dash 
from dash import html, dcc, register_page, callback, Input, Output

from dash import Dash, html, dcc, page_container

external_stylesheets = [
    "https://fonts.googleapis.com/css2?family=Roboto&display=swap",
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
    dcc.Link(
    html.H1("Resale Rangers", style={
        'color': 'white',
        'fontFamily': 'Roboto'
    }),
        href = "/",
        style={'textDecoration': 'none'}
    ),
    page_container,
], style={
    'backgroundColor': '#ff963b'
})

if __name__ == '__main__':
    app.run_server(debug=True)


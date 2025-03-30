from dash import html, register_page

register_page(__name__, path="/page-3")

layout = html.Div([
    html.H2("Page 3"),
    html.P("You got here from the button! 🎉")
])

import dash 
from dash import html, dcc, Input, Output, callback, register_page
import joblib
from models.model_tuning import conformal_predict

register_page(__name__, path="/page-4")

model_package = joblib.load("models/final_model.pkl")
model = model_package['model']
q_value = model_package['q_value']

layout = html.Div(
    children=[
        # Back link
        html.Div(
            dcc.Link("< Back to Selection", href="/input-specific-dummy", style={
                'fontFamily': 'Inter, sans-serif',
                'fontSize': '14px',
                'color': 'black',
                'textDecoration': 'none'
            }),
            style={'margin': '20px'}
        ),

        # Prediction Title & Price
        html.Div([
            html.Div(id="prediction-title", style={
                "fontSize": "20px",
                "fontWeight": "bold",
                "fontFamily": "Inter, sans-serif",
                "marginBottom": "10px"
            }),

            html.Div(id="price-section", style={
                "marginBottom": "30px",
                "fontFamily": "Inter, sans-serif"
            })
        ], style={
            "maxWidth": "1000px",
            "margin": "0 auto",
            "textAlign": "left",
            "paddingLeft": "20px"
        }),
        # Price Trends Section
        html.Div([
            html.H4("Price trends for this property", style={"fontFamily": "Inter, sans-serif"}),
            html.P(id="price-trend-text", style={"fontFamily": "Inter, sans-serif"}),

            html.Div([
                html.Button("Within 1km", id="1km-btn", n_clicks=0, style={
                    "marginRight": "10px",
                    "border": "none",
                    "padding": "8px 16px",
                    "borderRadius": "20px",
                    "backgroundColor": "#eee",
                    "fontFamily": "Inter, sans-serif"
                }),
                html.Button("Your block", id="block-btn", n_clicks=0, style={
                    "backgroundColor": "#800020",
                    "color": "white",
                    "border": "none",
                    "padding": "8px 16px",
                    "borderRadius": "20px",
                    "fontFamily": "Inter, sans-serif"
                })
            ], style={"marginBottom": "10px"}),

            html.Div([
                dcc.Graph(id="price-bar-chart", figure={}, config={'displayModeBar': False})
            ], style={"flex": "1"})
        ], style={"margin": "0 auto", "maxWidth": "1000px", "padding": "20px"}),

        # Summary Card and Chart Side by Side
        html.Div([
            html.Div([
                html.H4("Within the last year", style={"fontFamily": "Inter, sans-serif"}),
                html.P("Average Price", style={"fontWeight": "bold", "fontFamily": "Inter, sans-serif"}),
                html.H3("$300,000", style={"fontFamily": "Inter, sans-serif"}),
                html.P("Highest Sold", style={"fontFamily": "Inter, sans-serif"}),
                html.H4("$500,000  Mar 2024", style={"fontFamily": "Inter, sans-serif"}),
                html.P("Lowest Sold", style={"fontFamily": "Inter, sans-serif"}),
                html.H4("$100,000  Mar 2024", style={"fontFamily": "Inter, sans-serif"})
            ], style={
                "border": "1px solid lightgray",
                "padding": "20px",
                "borderRadius": "10px",
                "width": "300px",
                "fontFamily": "Inter, sans-serif",
                "marginTop": "20px"
            })
        ], style={"margin": "0 auto", "maxWidth": "1000px"}),

        # Recent Transactions
        html.Div([
            html.H4("Recent Transactions", style={"fontFamily": "Inter, sans-serif"}),
            html.P(id="recent-transactions-label", style={"fontFamily": "Inter, sans-serif"}),

            html.Table([
                html.Thead(html.Tr([html.Th("Month"), html.Th("Price"), html.Th("Floor Level")])),
                html.Tbody([
                    html.Tr([html.Td("—"), html.Td("—"), html.Td("—")])
                ])
            ], style={"border": "1px solid gray", "width": "100%", "marginTop": "10px"})
        ], style={"maxWidth": "1000px", "margin": "0 auto", "marginTop": "40px"}),

        # Property details
        html.Div([
            html.H4("Property details", style={"fontFamily": "Inter, sans-serif"}),
            html.Ul([
                html.Li("Nearest MRT: [dist_mrt], [dist]"),
                html.Li("Nearest Primary Schools (within 2km): [school list]"),
                html.Li("Nearest Hawker Center: [hawker], [dist]"),
                html.Li("Distance to Central Business District: [dist]"),
            ], style={"fontFamily": "Inter, sans-serif"}),

            html.Img(
                src="https://maps.googleapis.com/maps/api/staticmap?center=Ang+Mo+Kio,Singapore&zoom=15&size=600x300",
                style={"marginTop": "10px", "border": "1px solid #ccc"}
            )
        ], style={"maxWidth": "1000px", "margin": "0 auto", "marginTop": "40px", "paddingBottom": "40px"})
    ],
    style={"backgroundColor": "white", "padding": "20px"}
)

# Main callback — auto trigger on page load based on `manual-store`
@callback(
    Output("prediction-title", "children"),
    Output("price-section", "children"),
    Output("price-trend-text", "children"),
    Output("recent-transactions-label", "children"),
    Input("manual-store", "data"),
    Input("guru-store", "data")
)

def display_prediction(manual_data, guru_data):
    data = manual_data if manual_data else guru_data

    if data:
        try:
            input_vector = data.get("input_vector", [])[0]
            flat_type = data.get("flat_type_input", "[flat type]")
            address = data.get("address", "[address]")

            # Prediction using conformal method
            y_pred, y_lower, y_upper = conformal_predict(model, input_vector, q_value)

            return (
                f"A {flat_type} at {address} is predicted to be",
                html.Div([
                    html.H1(f"${int(y_pred[0]):,}", style={"color": "#800020", "font-size": "48px"}),
                    html.P(f"With a plausible range of ${int(y_lower[0]):,} to ${int(y_upper[0]):,}",
                           style={"font-size": "18px"})
                ]),
                f"Based on other {flat_type} sales",
                f"Based on other {flat_type} at [town] within the last 2 years"
            )

        except Exception as e:
            return "Error occurred", html.Div(f"Prediction failed: {e}"), "", ""

    return "", "", "", ""

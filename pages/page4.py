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

            # Segmented Toggle
            html.Div(
                dcc.RadioItems(
                    id='price-trend-toggle',
                    options=[
                        {'label': 'Within 1km', 'value': '1km'},
                        {'label': 'Your block', 'value': 'block'}
                    ],
                    value='block',
                    inline=True,
                    className='mode-toggle-container',
                    labelClassName='mode-toggle-label',
                    inputClassName='mode-toggle-input'
                ),
                style={'marginBottom': '10px'}
            ),

            # Chart and Summary Card Side by Side (Aligned Heights, 6.5:3.5)
            html.Div([
                # Bar Chart (6.5/10 width)
                html.Div([
                    html.Div([
                        dcc.Graph(
                            id="price-bar-chart",
                            figure={},
                            config={'displayModeBar': False},
                            style={"height": "100%"}
                        )
                    ], style={
                        "border": "1px solid lightgray",
                        "padding": "20px",
                        "borderRadius": "10px",
                        "backgroundColor": "white",
                        "width": "100%",
                        "height": "100%"
                    })
                ], style={
                    "flex": "7.5",
                    "height": "350px",
                    "display": "flex"
                }),

                # Summary Card (3.5/10 width)
                html.Div([
                    html.Div([
                        html.H4("Within the last year", style={
                            "fontFamily": "Inter, sans-serif",
                            "fontWeight": "700",
                            "marginBottom": "20px"
                        }),
                        html.P("Average Price", style={
                            "fontFamily": "Inter, sans-serif",
                            "fontStyle": "italic",
                            "marginBottom": "0"
                        }),
                        html.H3("$300,000", style={
                            "fontFamily": "Inter, sans-serif",
                            "fontWeight": "700",
                            "marginTop": "5px"
                        }),
                        html.P("Highest Sold", style={"fontFamily": "Inter, sans-serif", "marginBottom": "0", "marginTop": "20px"}),
                        html.Div([
                            html.H4("$500,000", style={
                                "display": "inline-block",
                                "fontFamily": "Inter, sans-serif",
                                "fontWeight": "700",
                                "marginRight": "8px"
                            }),
                            html.Span("Mar 2024", style={"color": "#888", "fontFamily": "Inter, sans-serif"})
                        ]),
                        html.P("Lowest Sold", style={"fontFamily": "Inter, sans-serif", "marginBottom": "0", "marginTop": "20px"}),
                        html.Div([
                            html.H4("$100,000", style={
                                "display": "inline-block",
                                "fontFamily": "Inter, sans-serif",
                                "fontWeight": "700",
                                "marginRight": "8px"
                            }),
                            html.Span("Mar 2024", style={"color": "#888", "fontFamily": "Inter, sans-serif"})
                        ])
                    ], style={
                        "border": "1px solid lightgray",
                        "padding": "20px",
                        "borderRadius": "10px",
                        "fontFamily": "Inter, sans-serif",
                        "backgroundColor": "#fff",
                        "flex": "1",
                        "height": "100%"
                    })
                ], style={
                    "flex": "2.5",
                    "height": "350px",
                    "display": "flex"
                })
            ], style={
                "display": "flex",
                "maxWidth": "1000px",
                "margin": "0 auto",
                "gap": "20px",
                "marginTop": "20px"
            })
        ], style={"margin": "0 auto", "maxWidth": "1000px", "padding": "20px"}),

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

# Prediction text on page load
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

# Toggle callback for bar chart
@callback(
    Output("price-bar-chart", "figure"),
    Input("price-trend-toggle", "value")
)
def update_chart_based_on_toggle(toggle_value):
    y_values = [100, 200, 300] if toggle_value == "1km" else [150, 250, 350]
    label = "1km" if toggle_value == "1km" else "Your Block"

    return {
        "data": [{
            "x": [1, 2, 3],
            "y": y_values,
            "type": "bar",
            "name": label,
            "marker": {"color": "#800020"}
        }],
        "layout": {
            "title": None,
            "autosize": True,
            "height": 350,
            "margin": {
                "l": 40, "r": 10, "t": 10, "b": 40
            },
            "xaxis": {"title": None},
            "yaxis": {"title": None},
            "paper_bgcolor": "white",
            "plot_bgcolor": "white"
        }
    }
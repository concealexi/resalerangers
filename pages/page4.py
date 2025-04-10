import dash
from dash import html, dcc, Input, Output, callback, register_page
import joblib
import pandas as pd
from models.model_tuning import conformal_predict
from functions.get_transactions import get_transactions, get_block_transactions  

register_page(__name__, path="/page-4")

model_package = joblib.load("models/final_model.pkl")
model = model_package['model']
q_value = model_package['q_value']

layout = html.Div(
    children=[
        html.Div(
            dcc.Link("< Back to Selection", href="/input-specific-dummy", style={
                'fontFamily': 'Inter, sans-serif',
                'fontSize': '14px',
                'color': 'black',
                'textDecoration': 'none'
            }),
            style={'margin': '20px'}
        ),

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

        html.Div([
            html.H4("Price trends for this property", style={"fontFamily": "Inter, sans-serif"}),
            html.P(id="price-trend-text", style={"fontFamily": "Inter, sans-serif"}),
            html.Div(
                dcc.RadioItems(
                    id='price-trend-toggle',
                    options=[
                        {'label': 'Within 1km', 'value': '1km'},
                        {'label': 'Your block', 'value': 'block'}
                    ],
                    value='1km',
                    inline=True,
                    className='mode-toggle-container',
                    labelClassName='mode-toggle-label',
                    inputClassName='mode-toggle-input'
                ),
                style={'marginBottom': '10px'}
            ),

            html.Div([
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
                            "padding": "20px 20px 30px 20px",  # top right bottom left
                            "borderRadius": "10px",
                            "backgroundColor": "white",
                            "width": "100%",
                            "height": "100%"
                        })
                ], style={"flex": "7.5", "height": "375px", "display": "flex"}),

                html.Div([
                    html.Div(id="summary-stats", style={
                        "border": "1px solid lightgray",
                        "padding": "20px",
                        "borderRadius": "10px",
                        "fontFamily": "Inter, sans-serif",
                        "backgroundColor": "#fff",
                        "flex": "1",
                        "height": "100%"
                    })
                ], style={"flex": "2.5", "height": "375px", "display": "flex"})
            ], style={
                "display": "flex",
                "maxWidth": "1000px",
                "margin": "0 auto",
                "gap": "20px",
                "marginTop": "20px"
            })
        ], style={"margin": "0 auto", "maxWidth": "1000px", "padding": "20px"}),

        html.Div([
            html.H4("Recent Transactions", style={"fontFamily": "Inter, sans-serif"}),
            html.P(id="recent-transactions-label", style={"fontFamily": "Inter, sans-serif"}),
            html.Table([
                html.Thead(html.Tr([html.Th("Month"), html.Th("Price"), html.Th("Floor Level")])),
                html.Tbody([html.Tr([html.Td("—"), html.Td("—"), html.Td("—")])])
            ], style={"border": "1px solid gray", "width": "100%", "marginTop": "10px"})
        ], style={"maxWidth": "1000px", "margin": "0 auto", "marginTop": "40px"}),

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

@callback(
    Output("price-bar-chart", "figure"),
    Output("summary-stats", "children"),
    Input("price-trend-toggle", "value"),
    Input("manual-store", "data"),
    Input("guru-store", "data")
)
def update_chart_and_stats(toggle_value, manual_data, guru_data):
    data = manual_data if manual_data else guru_data
    if not data:
        return {}, "No input"

    postal = data.get("postal")
    flat_type = data.get("flat_type")

    try:
        if toggle_value == "1km":
            _, recent_year = get_transactions(postal, flat_type)
        else:
            _, recent_year = get_block_transactions(postal, flat_type)

        # Chart
        df_grouped = recent_year.copy()
        df_grouped['quarter'] = pd.to_datetime(df_grouped['month']).dt.to_period('Q').astype(str)
        bar_df = df_grouped.groupby('quarter')['adjusted_resale_price'].mean().reset_index()
        fig = {
            "data": [{
                "x": bar_df['quarter'],
                "y": bar_df['adjusted_resale_price'],
                "type": "bar",
                "marker": {"color": "#800020"}
            }],
            "layout": {
                "title": None,
                "autosize": True,
                "height": 350,
                "margin": {"l": 40, "r": 10, "t": 10, "b": 40},
                "xaxis": {"title": None},
                "yaxis": {"title": None},
                "paper_bgcolor": "white",
                "plot_bgcolor": "white"
            }
        }

        # Stats
        avg_price = round(recent_year['adjusted_resale_price'].mean())
        max_row = recent_year.loc[recent_year['adjusted_resale_price'].idxmax()]
        min_row = recent_year.loc[recent_year['adjusted_resale_price'].idxmin()]
        max_month = pd.to_datetime(max_row['month']).strftime("%b %Y")
        min_month = pd.to_datetime(min_row['month']).strftime("%b %Y")

        stats_html = html.Div([
            html.H4("Within the last year", style={"fontWeight": "700", "marginBottom": "20px"}),
            html.P("Average Price", style={"fontStyle": "italic", "marginBottom": "0"}),
            html.H3(f"${avg_price:,}", style={"fontWeight": "700", "marginTop": "5px"}),
            html.P("Highest Sold", style={"marginBottom": "0", "marginTop": "20px"}),
            html.Div([
                html.H4(f"${int(max_row['adjusted_resale_price']):,}", style={"display": "inline-block", "marginRight": "8px"}),
                html.Span(max_month, style={"color": "#888"})
            ]),
            html.P("Lowest Sold", style={"marginBottom": "0", "marginTop": "20px"}),
            html.Div([
                html.H4(f"${int(min_row['adjusted_resale_price']):,}", style={"display": "inline-block", "marginRight": "8px"}),
                html.Span(min_month, style={"color": "#888"})
            ])
        ])
        return fig, stats_html

    except Exception as e:
        return {}, html.Div(f"Error loading data: {str(e)}")

import dash
from dash import html, dcc, Input, Output, State, callback, register_page, ctx, dash_table
from dash.exceptions import PreventUpdate
import dash_leaflet as dl
import joblib
import xgboost as xgb
import pandas as pd
from models.model_tuning import conformal_predict
from functions.get_transactions import get_transactions, get_block_transactions
from functions.input_for_model import get_all_nearest_amenities  # assuming it's in functions

register_page(__name__, path="/output-specific")

# model_package = joblib.load("models/final_model.pkl")
# model = model_package['model']
# q_value = model_package['q_value']

bst = xgb.Booster()
bst.load_model("models/xgb_model.bin")

with open("models/q_value.txt", "r") as f:
    q_value = float(f.read())
# Now 'bst' is your loaded XGBoost model used for prediction.
model = bst


layout = html.Div([
    html.Div(dcc.Link("< Back to Selection", href="/input-specific", style={
        'fontFamily': 'Inter, sans-serif', 'fontSize': '14px',
        'color': 'black', 'textDecoration': 'none'}), style={'margin': '20px'}),

    html.Div([
        html.Div(id="prediction-title", style={"fontSize": "20px", "fontWeight": "bold",
                                               "fontFamily": "Inter, sans-serif", "marginBottom": "10px"}),
        html.Div(id="price-section", style={"marginBottom": "30px", "fontFamily": "Inter, sans-serif"})
    ], style={"maxWidth": "1000px", "margin": "0 auto", "textAlign": "left"}),

    # Price Trends Section
    html.Div([
        html.H4("Price trends for this property", style={"fontFamily": "Inter, sans-serif", "fontSize": '18px'}),
        html.P(id="price-trend-text", style={"fontFamily": "Inter, sans-serif"}),
        dcc.RadioItems(id='price-trend-toggle',
            options=[{'label': 'Within 1km', 'value': '1km'}, {'label': 'Your block', 'value': 'block'}],
            value='1km', inline=True, className='mode-toggle-container',
            labelClassName='mode-toggle-label', inputClassName='mode-toggle-input'),
        html.Div([
            html.Div([
                html.Div([
                    dcc.Graph(id="price-bar-chart", config={'displayModeBar': False}, style={"height": "100%"})
                ], style={"border": "1px solid lightgray", "padding": "20px 20px 30px 20px",
                          "borderRadius": "10px", "backgroundColor": "white", "width": "100%", "height": "100%"})
            ], style={"flex": "7.5", "height": "375px", "display": "flex"}),

            html.Div([
                html.Div(id="summary-stats", style={"border": "1px solid lightgray", "padding": "20px",
                                                    "borderRadius": "10px", "fontFamily": "Inter, sans-serif",
                                                    "backgroundColor": "#fff", "flex": "1", "height": "100%"})
            ], style={"flex": "2.5", "height": "375px", "display": "flex"})
        ], style={"display": "flex", "maxWidth": "1000px", "margin": "0 auto",
                  "gap": "20px", "marginTop": "20px"})
    ], style={"margin": "0 auto", "maxWidth": "1000px"}),

    # Recent Transactions Table
    html.Div([
        html.H4("Recent Transactions", style={"fontFamily": "Inter, sans-serif", "fontSize": '18px'}),
        html.Div(id='recent-transactions-label', style={"fontFamily": "Inter, sans-serif"}),
        dash_table.DataTable(
            id='transaction-table',
            columns=[
                {'name': 'Month', 'id': 'month'},
                {'name': 'Address', 'id': 'address'},
                {'name': 'Storey', 'id': 'storey_range'},
                {'name': 'Price', 'id': 'adjusted_resale_price'}
            ],
            style_cell={
                'fontFamily': 'Inter, sans-serif',
                'textAlign': 'left',
                'padding': '16px',
                'border': 'none',
                'fontSize': '15px',
                'backgroundColor': '#f9f9f9',
            },
            style_header={
                'backgroundColor': '#ffffff',
                'fontWeight': 'bold',
                'borderBottom': '2px solid #dddddd',
                'fontSize': '16px',
            },
            style_table={
                'width': '100%',
                'marginTop': '10px',
                'borderCollapse': 'separate',
                'borderSpacing': '0 8px'
            },
            cell_selectable=True,
        )
    ], style={"maxWidth": "1000px", "margin": "0 auto", "marginTop": "40px"}),

    # Property details (with SVG icons + map beside)
    html.Div([

        # Combine header and amenities into a single left column
        html.Div([  
            html.H4("Property details", style={
                "fontFamily": "Inter, sans-serif",
                "fontSize": '18px',
                "marginBottom": "16px",
                "marginTop": '50px'
            }),
            html.Div(id='amenities-list', style={
                "fontFamily": "Inter, sans-serif",
                "flex": "1",
                "overflow": "hidden",
                "display": "flex",
                "flexDirection": "column",
                "justifyContent": "space-between",
            })
        ], style={
            "flex": "1",
            "height": "340px",  # match the map height
            "display": "flex",
            "flexDirection": "column",
            "justifyContent": "space-between"
        }),

        # Map
        dl.Map(id='selected-map',
            center=[1.3521, 103.8198],
            zoom=16,
            children=[
                dl.TileLayer(
                    url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
                    attribution='&copy; <a href="https://carto.com/">CartoDB</a>'
                ),
                dl.LayerGroup(id='selected-marker')
            ],
            style={
                "width": "100%",
                "maxWidth": "420px",
                "height": "315px",
                "borderRadius": "12px",
                "boxShadow": "0px 0px 12px rgba(0,0,0,0.15)",
                "border": "1px solid #ddd",
                'marginTop': '50px'
            }
        )

    ], style={
        "display": "flex",
        "marginTop": "60px",
        "alignItems": "flex-start",
        "gap": "40px",
        "maxWidth": "1000px",
        "margin": "0 auto",
        "paddingBottom": "40px"
    })
], style={"backgroundColor": "white", "padding": "20px"})


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
                f"A {flat_type} HDB at {address} is predicted to be",
                html.Div([
                    html.H1(f"${int(y_pred[0]):,}", style={"color": "#7F0019", "font-size": "48px"}),
                    html.P(f"With a plausible range of ${int(y_lower[0]):,} to ${int(y_upper[0]):,}",
                           style={"font-size": "18px"})
                ]),
                f"Based on other {flat_type} sales",
                f"Based on the closest {flat_type} HDB to your selection within the last 2 years"
            )
        except Exception as e:
            return "Error occurred", html.Div(f"Prediction failed: {e}"), "", ""

    return "", "", "", ""

stored_records = {}
@callback(
    Output("price-bar-chart", "figure"),
    Output("summary-stats", "children"),
    Output("transaction-table", "data"),
    Output("transaction-table", "active_cell"),  # <-- NEW
    Input("price-trend-toggle", "value"),
    Input("manual-store", "data"),
    Input("guru-store", "data")
)
def update_chart(toggle_value, manual_data, guru_data):
    data = manual_data if manual_data else guru_data
    if not data:
        raise PreventUpdate

    postal = data.get("postal")
    flat_type = data.get("flat_type")

    if toggle_value == "1km":
        top3, recent_year, full = get_transactions(postal, flat_type)
    else:
        top3, recent_year, full = get_block_transactions(postal, flat_type)

    stored_records['full'] = full.to_dict('records')  # Used for row click
    bar_df = recent_year.copy()
    bar_df['quarter'] = pd.to_datetime(bar_df['month']).dt.to_period('Q').astype(str)
    chart_data = (
        bar_df.groupby('quarter')
        .agg(adjusted_resale_price=('adjusted_resale_price', 'mean'),
            units_sold=('adjusted_resale_price', 'count'))
        .reset_index()
        .sort_values('quarter')
        .tail(4)
    )
    chart_data['quarter'] = chart_data['quarter'].str.replace(r'(\d{4})Q(\d)', r'Q\2 \1', regex=True)

    fig = {
        "data": [{
            "x": chart_data['quarter'],
            "y": chart_data['adjusted_resale_price'],
            "customdata": chart_data['units_sold'],
            "type": "bar",
            "marker": {"color": "#7F0019"},
            "hovertemplate": (
                "In %{x}<br>" +
                "%{customdata} units sold<br>" +
                "Average: $%{y:,.0f}<extra></extra>"
            )
        }],
        "layout": {
            "title": None,
            "autosize": True,
            "height": 350,
            "margin": {"l": 40, "r": 10, "t": 10, "b": 40},
            "xaxis": {"title": None},
            "yaxis": {"title": None},
            "paper_bgcolor": "white",
            "plot_bgcolor": "white",
            "hoverlabel": {
                "font": {
                    "family": "Inter, sans-serif",
                    "size": 14,
                    "color": "#333"
                },
                "bgcolor": "white",
                "bordercolor": "#ddd",
                "align": "left"
            }
        }
    }
    if recent_year.empty:
        return dash.no_update  # or other fallback values
    max_row = recent_year.loc[recent_year['adjusted_resale_price'].idxmax()]
    min_row = recent_year.loc[recent_year['adjusted_resale_price'].idxmin()]
    avg_price = round(recent_year['adjusted_resale_price'].mean())

    stats_html = html.Div([
        html.H4("Within the last year", style={"fontWeight": "700", "marginBottom": "15px"}),
        html.P("Average Price", style={"fontWeight": "700", "marginBottom": "0"}),
        html.H3(f"${avg_price:,}", style={"fontWeight": "700", "marginTop": "5px"}),
        html.P("Highest Sold", style={"fontWeight": "700", "marginBottom": "0", "marginTop": "20px"}),
        html.Div([
        html.H4(f"${int(max_row['adjusted_resale_price']):,}", style={"marginBottom": "2px"}),
        html.Div(max_row['address'], style={"color": "black", "fontSize": "13px", "marginBottom": "2px"}),
        html.Div(pd.to_datetime(max_row['month']).strftime("%b %Y"), style={"color": "#000", "fontSize": "14px"})]),
        html.P("Lowest Sold", style={"fontWeight": "700", "marginBottom": "0", "marginTop": "20px"}),
        html.Div([
        html.H4(f"${int(min_row['adjusted_resale_price']):,}", style={"marginBottom": "2px"}),
        html.Div(min_row['address'], style={"color": "black", "fontSize": "13px", "marginBottom": "2px"}),
        html.Div(pd.to_datetime(min_row['month']).strftime("%b %Y"), style={"color": "#000", "fontSize": "14px"})])
    ])

    return fig, stats_html, top3.to_dict('records'), {"row": 0, "column": 0, "column_id": "month"}

@callback(
    Output("amenities-list", "children"),
    Output("selected-marker", "children"),
    Output("selected-map", "center"),
    Input("transaction-table", "active_cell")
)
def update_amenities_and_map(active_cell):
    if not active_cell:
        raise PreventUpdate

    row_idx = active_cell['row']
    full = stored_records.get('full', [])

    if not full or row_idx >= len(full):
        raise PreventUpdate

    full_row = full[row_idx]
    lat = full_row.get('latitude')
    lon = full_row.get('longitude')

    if lat is None or lon is None or pd.isna(lat) or pd.isna(lon):
        return [html.Div("No geolocation data available for this transaction.")], [], [1.3521, 103.8198]

    coord_row = {
        "latitude": float(lat),
        "longitude": float(lon)
    }

    nearest = get_all_nearest_amenities(coord_row)

    def make_amenity(icon, title, value):
        return html.Div([
            html.Img(src=f"/assets/{icon}", style={
                "width": "45px", "height": "45px", "marginRight": "12px", "flexShrink": "0", "marginTop": "2px"
            }),
            html.Div([
                html.Div(title, style={
                    "fontWeight": "600", "fontSize": "15px", "marginBottom": "2px"
                }),
                html.Div(value, style={
                    "fontSize": "14px", "color": "#333"
                })
            ])
        ], style={
            "display": "flex", "alignItems": "flex-start", "marginBottom": "20px"
        })

    amenities = [
        make_amenity("mrt.svg", "Nearest MRT",
                     f"{nearest['nearest_mrt']['name']}, {nearest['nearest_mrt']['distance_km']} km"),
        make_amenity("edu.svg", "Nearest Primary Schools (within 2km)",
                     f"{nearest['nearest_school']['name']}, {nearest['nearest_school']['distance_km']} km"),
        make_amenity("utensil.svg", "Nearest Hawker Center",
                     f"{nearest['nearest_foodcourt']['name']}, {nearest['nearest_foodcourt']['distance_km']} km"),
        make_amenity("city.svg", "Distance to Central Business District",
                     f"{nearest['distance_to_cbd']} km")
    ]

    marker = dl.Marker(position=[lat, lon], children=dl.Tooltip("🏠 Selected Property"))

    return amenities, [marker], [lat, lon]


@callback(
    Output('transaction-table', 'style_data_conditional'),
    Input('transaction-table', 'active_cell')
)
def style_active_row(active_cell):
    # Base zebra-striping for all rows
    style = [
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': '#fcfcfc',
        },
        {
            'if': {'row_index': 'even'},
            'backgroundColor': '#f9f9f9',
        }
    ]

    # Add selected row style
    if active_cell:
        row_idx = active_cell['row']
        style.append({
            'if': {'row_index': row_idx},
            'backgroundColor': '#7F0019',
            'color': 'white',
            'borderTop': '2px solid #dddddd'
        })

    return style


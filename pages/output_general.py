from dash import html, callback, Output, Input, State, register_page, dcc, dash_table, no_update
import dash
import pandas as pd
from geopy.distance import geodesic
import dash_leaflet as dl
import dash_leaflet.express as dlx
import plotly.express as px
from datetime import datetime


register_page(__name__, path="/output-general")

# Constants
CBD_COORDS = (1.287953, 103.851784)

# Load data
hdb_df = pd.read_csv("dataset/hdb_final_dataset.csv", dtype={"postal_code": str})
hdb_info = pd.read_csv("dataset/hdb_informations.csv", dtype={"postal_code": str})
schools_df = pd.read_csv("dataset/all_primary_schools.csv")
mrt_df = pd.read_csv("dataset/mrt_stations.csv")
hawker_df = pd.read_csv("dataset/hawkercentercoord.csv")


# Merge data
hdb_df['postal_code'] = hdb_df['postal_code'].astype(str).str.zfill(6)
hdb_info['postal_code'] = hdb_info['postal_code'].astype(str).str.zfill(6)
hdb_df = pd.merge(hdb_df, hdb_info[['postal_code', 'max_floor_lvl']], on='postal_code', how='left')
hdb_df = hdb_df[hdb_df['max_floor_lvl'].notna()]


layout = html.Div([
    html.Div([  # ⬅️ NEW outer container starts here

        dcc.Location(id='url'),
        dcc.Store(id='map-center-store', storage_type='memory'),

        html.H2("Your Selected Filters", style={
            'fontFamily': 'Inter, sans-serif', 'textAlign': 'left'
        }),

        html.Div(id='filter-summary', style={
            'width': '80%', 'margin': 'auto', 'marginBottom': '20px'
        }),

        html.Div(id='bar-chart-section', children=[
            html.H2("Price trends for properties in the area", style={
                'textAlign': 'left', 'fontFamily': 'Inter, sans-serif', 'marginTop': '30px'
            }),
            html.P(id='bar-chart-subtitle', style={
                'textAlign': 'left', 'fontFamily': 'Inter, sans-serif',
                'fontSize': '16px', 'marginBottom': '10px'
            }),
            html.Div(id='bar-chart-subtitle', style={
                'marginBottom': '10px', 'textAlign': 'left',
                'fontFamily': 'Inter, sans-serif', 'fontSize': '16px'
            }),
        ]),

        html.Div([
            html.H4("Select which summary to view:", style={
                'fontFamily': 'Inter, sans-serif', 'marginBottom': '20px'
            }),
            dcc.RadioItems(
                id='summary-toggle',
                options=[],  # populated dynamically via callback
                value='town1',
                inline=True,
                className='mode-toggle-container',
                labelClassName='mode-toggle-label',
                inputClassName='mode-toggle-input'
            )
        ], style={
            'textAlign': 'left', 'marginTop': '20px',
            'marginBottom': '20px', 'fontFamily': 'Inter, sans-serif'
        }),

        html.Div([
            html.Div([
                dcc.Graph(id="quarterly-bar-chart", config={'displayModeBar': False}, style={"height": "100%", "width": "100%"})
            ], style={
                "flex": "7",
                "border": "1px solid lightgray",
                "padding": "20px",
                "borderRadius": "10px",
                "backgroundColor": "white",
                "height": "425px",
                "boxSizing": "border-box"
            }),

            html.Div(id="price-summary-container", style={
                "flex": "3",
                "border": "1px solid lightgray",
                "padding": "20px",
                "borderRadius": "10px",
                "fontFamily": "Inter, sans-serif",
                "backgroundColor": "#fff",
                "height": "425px",
                "boxSizing": "border-box"
            })
        ], style={
            "display": "flex",
            "gap": "20px",
            "maxWidth": "1000px",
            "margin": "0 auto",
            "marginTop": "20px",
            "alignItems": "stretch"
        }),

        html.Div([
            html.H3("Recent Transactions by Town", style={
                'textAlign': 'left',
                'fontFamily': 'Inter, sans-serif',
                'fontSize': '28px',
                'marginTop': '40px',
                'marginBottom': '8px'
            }),
            html.P("For properties that match your selected filters", style={
                'textAlign': 'left',
                'fontFamily': 'Inter, sans-serif',
                'fontSize': '16px',
                'color': '#555',
                'marginBottom': '30px'
            }),

            html.Div([
                html.Div([
                    html.H4(id='town1-name', style={
                        'fontWeight': 'bold',
                        'textAlign': 'left',
                        'fontSize': '20px',
                        'fontFamily': 'Inter, sans-serif',
                        'marginBottom': '10px'
                    }),
                    html.Div(id='filter-table-town1')
                ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),

                html.Div([
                    html.H4(id='town2-name', style={
                        'fontWeight': 'bold',
                        'textAlign': 'left',
                        'fontSize': '20px',
                        'fontFamily': 'Inter, sans-serif',
                        'marginBottom': '10px'
                    }),
                    html.Div(id='filter-table-town2')
                ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginLeft': '4%'})
            ])
        ]),

        dcc.Store(id='selected-postal-store'),
        dcc.Store(id='selected-postal-store-town2'),

        html.Hr(),

        html.Div([
            html.Div(id='property-details', style={'flex': '1', 'marginRight': '10px'}),
            html.Div(id='property-details-town2', style={'flex': '1', 'marginLeft': '10px'})
        ], style={
            'display': 'flex',
            'flexDirection': 'row',
            'justifyContent': 'center',
            'alignItems': 'flex-start',
            'width': '100%',
            'gap': '20px',
            'marginTop': '30px'
        }),

        html.Div([
            html.H3("🗺️ Map of Nearby Amenities", style={
                'textAlign': 'center',
                'marginTop': '40px',
                'fontFamily': 'Inter, sans-serif'
            }),
            html.Div([
                html.Div([
                    dl.Map(id='amenity-map',
                           center=[1.287953, 103.851784],
                           zoom=15,
                           children=[
                               dl.TileLayer(url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
                                            attribution='&copy; <a href="https://carto.com/">CartoDB</a>'),
                               dl.LayerGroup(id='map-markers')
                           ],
                           style={'width': '100%', 'height': '400px'})
                ], style={'flex': '1', 'marginRight': '10px'}),

                html.Div([
                    dl.Map(id='amenity-map-town2',
                           center=[1.287953, 103.851784],
                           zoom=15,
                           children=[
                               dl.TileLayer(url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
                                            attribution='&copy; <a href="https://carto.com/">CartoDB</a>'),
                               dl.LayerGroup(id='map-markers-town2')
                           ],
                           style={'width': '100%', 'height': '400px'})
                ], style={'flex': '1', 'marginLeft': '10px'})
            ], style={
                'display': 'flex', 'gap': '20px',
                'width': '100%'
            })
        ], style={'marginTop': '30px'})

    ], style={  # 👈 NEW OUTER CONTAINER STYLE
        'maxWidth': '1000px',
        'margin': '0 auto'
    })
])




# Utility function
def get_all_nearest_amenities(postal_code, hdb_amenities_dist_with_postal, all_primary_schools, mrt_stations, hawkercentrecoord):
    coord_row = hdb_amenities_dist_with_postal[hdb_amenities_dist_with_postal['postal_code'] == postal_code]
    if coord_row.empty:
        return None

    hdb_coords = (coord_row.iloc[0]['latitude'], coord_row.iloc[0]['longitude'])

    def nearest_amenity(df, name_col, lat_col='latitude', lon_col='longitude'):
        nearest = None
        min_dist = float('inf')
        for row in df.itertuples(index=False):
            coords = (getattr(row, lat_col), getattr(row, lon_col))
            dist = geodesic(hdb_coords, coords).km
            if dist < min_dist:
                nearest = (getattr(row, name_col), round(dist, 2))
                min_dist = dist
        return nearest

    school = nearest_amenity(all_primary_schools, 'SchoolName')
    mrt = nearest_amenity(mrt_stations, 'station_name')
    hawker = nearest_amenity(hawkercentrecoord, 'hc_name')
    cbd_dist = round(geodesic(hdb_coords, CBD_COORDS).km, 2)

    return {
        'school': school,
        'mrt': mrt,
        'hawker': hawker,
        'cbd_dist': cbd_dist,
        'address': coord_row.iloc[0]['address']
    }

@callback(
    Output('quarterly-bar-chart', 'figure'),
    Output('price-summary-container', 'children'),
    Output('bar-chart-subtitle', 'children'),
    Output('filter-summary', 'children'),
    Input('user-filter-store', 'data'),
    Input('summary-toggle', 'value')
)
def update_quarterly_chart(filter_data, summary_toggle):
    df = hdb_df.copy()
    if not filter_data:
        raise dash.exceptions.PreventUpdate

    town = filter_data.get('town1')
    town2 = filter_data.get('town2')
    flat_type = filter_data.get('flat_type')
    floor_level = filter_data.get('floor_level')
    lease = filter_data.get('remaining_lease')
    max_mrt = filter_data.get('max_dist_mrt')
    max_sch = filter_data.get('max_dist_school')
    flat_type_col = f"flat_type_{flat_type}"

    df1 = df[(df['town'] == town) & (df[flat_type_col] == 1)].copy()
    df2 = df[(df['town'] == town2) & (df[flat_type_col] == 1)].copy()

    for dfx in [df1, df2]:
        dfx['storey_median'] = pd.to_numeric(dfx['storey_median'], errors='coerce')
        dfx['low_threshold'] = (dfx['max_floor_lvl'] * 0.25).round()
        dfx['high_threshold'] = (dfx['max_floor_lvl'] * 0.75).round()

        def classify_floor(row):
            if pd.isna(row['storey_median']) or pd.isna(row['max_floor_lvl']):
                return None
            if row['storey_median'] <= row['low_threshold']:
                return "Low"
            elif row['storey_median'] > row['high_threshold']:
                return "High"
            else:
                return "Medium"

        dfx['floor_category'] = dfx.apply(classify_floor, axis=1)

    if floor_level:
        df1 = df1[df1['floor_category'] == floor_level]
        df2 = df2[df2['floor_category'] == floor_level]
    if lease:
        df1 = df1[df1['remaining_lease'] >= lease]
        df2 = df2[df2['remaining_lease'] >= lease]
    if max_mrt:
        df1 = df1[df1['min_dist_mrt'] <= max_mrt]
        df2 = df2[df2['min_dist_mrt'] <= max_mrt]
    if max_sch:
        df1 = df1[df1['min_dist_sch'] <= max_sch]
        df2 = df2[df2['min_dist_sch'] <= max_sch]

    months = [f"{y}-{m:02d}" for y in [2024, 2025] for m in range(1, 13)]
    months = months[3:15]  # Apr 2024 to Mar 2025
    month_to_q = {m: f"Q{((int(m[5:7]) - 1) // 3) + 1} {m[:4]}" for m in months}
    df1 = df1[df1['month'].isin(months)]
    df2 = df2[df2['month'].isin(months)]
    df1['Quarter'] = df1['month'].map(month_to_q)
    df2['Quarter'] = df2['month'].map(month_to_q)

    def compute_q_avg(df, town_label):
        quarters = ['Q2 2024', 'Q3 2024', 'Q4 2024', 'Q1 2025']
        if df.empty:
            return pd.DataFrame({
                'Quarter': quarters,
                'adjusted_resale_price': [0] * len(quarters),
                'Town': [town_label] * len(quarters)
            }), None
        else:
            q_avg = df.groupby('Quarter')['adjusted_resale_price'].mean().fillna(0).round().reset_index()
            q_avg['Quarter'] = pd.Categorical(q_avg['Quarter'], quarters, ordered=True)
            q_avg = q_avg.sort_values('Quarter')
            q_avg['Town'] = town_label
            return q_avg, df

    q_avg1, df1_valid = compute_q_avg(df1, town.title())
    q_avg2, df2_valid = compute_q_avg(df2, town2.title())
    combined_avg = pd.concat([q_avg1, q_avg2])

    # Fallback values if town/town2 are None
    town_display = (town or "Town 1").title()
    town2_display = (town2 or "Town 2").title()

    color_map = {
        town_display: "#7F0019",    # dark red
        town2_display: "#e6ab2d"    # mustard yellow
    }

    combined_avg['Town'] = combined_avg['Town'].replace({
        town.title(): town_display,
        town2.title(): town2_display
    })

    fig = px.bar(
        combined_avg,
        x='Quarter',
        y='adjusted_resale_price',
        color='Town',
        color_discrete_map=color_map,
        barmode='group',
        labels={'adjusted_resale_price': 'Avg Price (SGD)'},
        width = 700,
        height = 400
    )

    fig.update_traces(width=0.3)
    fig.update_layout(
        margin=dict(l=10, r=10, t=20, b=20),  # tight bottom
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y= -0.17,
            xanchor="center",
            x=0.5,
            font=dict(size=13)
        ),
        yaxis=dict(
            title="",
            tickformat=",",
            showgrid=True,
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='lightgray',
            gridcolor="lightgray",
            gridwidth=1
        ),
        xaxis=dict(
            title="",
            showgrid=False
        ),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        title=None
    )

    def build_summary(df, town_name):
        if df is None or df.empty:
            return html.Div("No data available.")

        avg = int(df['adjusted_resale_price'].mean())
        max_row = df.loc[df['adjusted_resale_price'].idxmax()]
        min_row = df.loc[df['adjusted_resale_price'].idxmin()]
        max_month = datetime.strptime(max_row['month'], "%Y-%m").strftime("%b %Y")
        min_month = datetime.strptime(min_row['month'], "%Y-%m").strftime("%b %Y")

        return html.Div([
            html.H2(town_name, style={"fontWeight": "bold", "fontSize": "22px", "marginBottom": "10px"}),

            html.H3("Within the last year", style={"fontWeight": "bold", "fontSize": "16px", "marginBottom": "10px"}),

            html.Div("Average Price", style={"fontStyle": "italic", "fontSize": "16px", "fontWeight": "bold"}),
            html.Div(f"${avg:,}", style={"fontSize": "20px", "fontWeight": "bold", "marginBottom": "25px"}),

            html.Div("Highest Sold", style={"fontSize": "15px", "fontWeight": "bold"}),
            html.Div([
                html.Span(f"${int(max_row['adjusted_resale_price']):,}", style={"fontSize": "16px", "fontWeight": "bold"}),
                html.Span(f"  {max_month}", style={"fontSize": "14px", "marginLeft": "6px"})
            ], style={"fontSize": "15px"}),
            html.Div(f"{max_row['address']}", style={"fontSize": "13px", "fontStyle": "italic", "marginBottom": "20px"}),

            html.Div("Lowest Sold", style={"fontSize": "15px", "fontWeight": "bold"}),
            html.Div([
                html.Span(f"${int(min_row['adjusted_resale_price']):,}", style={"fontSize": "16px", "fontWeight": "bold"}),
                html.Span(f"  {min_month}", style={"fontSize": "14px", "marginLeft": "6px"})
            ], style={"fontSize": "15px"}),
            html.Div(f"{min_row['address']}", style={"fontSize": "13px", "fontStyle": "italic"})
        ], style={
            "padding": "20px",
            "fontFamily": "Inter, sans-serif"
        })

    summary1 = build_summary(df1_valid, town.title())
    summary2 = build_summary(df2_valid, town2.title())

    subtitle = f"Based on flats in {town.title()} and {town2.title()} with {flat_type.title()} flat type and same amenity features"
    summary_filters = html.Ul([
        html.Li(f"🏙️ Town 1: {town}"),
        html.Li(f"🏙️ Town 2: {town2}") if town2 else None,
        html.Li(f"🏠 Flat Type: {flat_type}"),
        html.Li(f"📏 Floor Level: {floor_level}"),
        html.Li(f"🕒 Min Lease: {lease} years") if lease else None,
        html.Li(f"🚇 Max Distance to MRT: {max_mrt} km") if max_mrt else None,
        html.Li(f"🏫 Max Distance to School: {max_sch} km") if max_sch else None
    ])

    selected_summary = summary1 if summary_toggle == 'town1' else summary2

    return fig, selected_summary, subtitle, summary_filters

# Callback to filter and display table
@callback(
    Output('filter-table-town1', 'children'),
    Output('selected-postal-store', 'data'),
    Input('user-filter-store', 'data'),
    Input('url', 'pathname'),
)
def update_table(filter_data, pathname):
    if pathname != "/output-general" or not filter_data:
        return html.Div("No data."), None

    town = filter_data.get('town1')
    flat_type = filter_data.get('flat_type')
    floor_level = filter_data.get('floor_level')
    lease = filter_data.get('remaining_lease')
    max_mrt = filter_data.get('max_dist_mrt')
    max_sch = filter_data.get('max_dist_school')
    flat_type_col = f"flat_type_{flat_type}"

    df = hdb_df[
        (hdb_df['town'] == town) &
        (hdb_df[flat_type_col] == 1)
    ]

    # Floor level filter logic
    def extract_level_range(median_str):
        try:
            start, end = median_str.split(" TO ")
            return pd.Series([int(start), int(end)])
        except:
            return pd.Series([None, None])

        # Ensure storey_median is numeric
    df['storey_median'] = pd.to_numeric(df['storey_median'], errors='coerce')

    # Compute thresholds
    df['low_threshold'] = (df['max_floor_lvl'] * 0.25).round()
    df['high_threshold'] = (df['max_floor_lvl'] * 0.75).round()

    # Classify floor level
    def classify_floor(row):
        if pd.isna(row['storey_median']) or pd.isna(row['max_floor_lvl']):
            return None
        if row['storey_median'] <= row['low_threshold']:
            return "Low"
        elif row['storey_median'] > row['high_threshold']:
            return "High"
        else:
            return "Medium"

    df['floor_category'] = df.apply(classify_floor, axis=1)

    # Filter
    if floor_level:
        df = df[df['floor_category'] == floor_level]

    if lease:
        df = df[df['remaining_lease'] >= lease]
    if max_mrt:
        df = df[df['min_dist_mrt'] <= max_mrt]
    if max_sch:
        df = df[df['min_dist_sch'] <= max_sch]

    df['address'] = df['block'].astype(str).str.strip() + " " + df['street_name'].str.title()
    df['Distance to MRT (km)'] = df['min_dist_mrt'].round(2)
    df['Distance to School (km)'] = df['min_dist_sch'].round(2)

    table_df = df[['month', 'address', 'adjusted_resale_price', 'postal_code']].rename(columns={
        'month': 'Month',
        'address': 'Address',
        'adjusted_resale_price': 'Price',
        'postal_code': 'postal_code'  # retain this for data but hide it from view
    })

    if table_df.empty:
        return html.Div("No results."), None


    return dash_table.DataTable(
        id='transaction-table-town1',
        columns=[{"name": i, "id": i} for i in table_df.columns if i != "postal_code"],
        data=table_df.to_dict('records'),
        cell_selectable=True,
        active_cell=None,
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
        style_data_conditional=[{
            'if': {'column_id': 'postal_code'},
            'display': 'none'
        }],
        style_table={
            'width': '100%',
            'marginTop': '10px',
            'borderCollapse': 'separate',
            'borderSpacing': '0 8px'
        },
        page_size=10
    ), table_df.to_dict('records')


@callback(
    Output('filter-table-town2', 'children'),
    Output('selected-postal-store-town2', 'data'),
    Input('user-filter-store', 'data'),
    Input('url', 'pathname'),
)
def update_table_town2(filter_data, pathname):
    if pathname != "/output-general" or not filter_data or not filter_data.get("town2"):
        return html.Div("No data."), None

    town2 = filter_data.get('town2')
    flat_type = filter_data.get('flat_type')
    floor_level = filter_data.get('floor_level')
    lease = filter_data.get('remaining_lease')
    max_mrt = filter_data.get('max_dist_mrt')
    max_sch = filter_data.get('max_dist_school')
    flat_type_col = f"flat_type_{flat_type}"

    df = hdb_df[
        (hdb_df['town'] == town2) &
        (hdb_df[flat_type_col] == 1)
    ]

    df['storey_median'] = pd.to_numeric(df['storey_median'], errors='coerce')
    df['low_threshold'] = (df['max_floor_lvl'] * 0.25).round()
    df['high_threshold'] = (df['max_floor_lvl'] * 0.75).round()

    def classify_floor(row):
        if pd.isna(row['storey_median']) or pd.isna(row['max_floor_lvl']):
            return None
        if row['storey_median'] <= row['low_threshold']:
            return "Low"
        elif row['storey_median'] > row['high_threshold']:
            return "High"
        else:
            return "Medium"

    df['floor_category'] = df.apply(classify_floor, axis=1)

    if floor_level:
        df = df[df['floor_category'] == floor_level]
    if lease:
        df = df[df['remaining_lease'] >= lease]
    if max_mrt:
        df = df[df['min_dist_mrt'] <= max_mrt]
    if max_sch:
        df = df[df['min_dist_sch'] <= max_sch]

    df['address'] = df['block'].astype(str).str.strip() + " " + df['street_name'].str.title()
    df['Distance to MRT (km)'] = df['min_dist_mrt'].round(2)
    df['Distance to School (km)'] = df['min_dist_sch'].round(2)

    table_df = df[['month', 'address', 'adjusted_resale_price', 'postal_code']].rename(columns={
        'month': 'Month',
        'address': 'Address',
        'adjusted_resale_price': 'Price',
        'postal_code': 'postal_code'  # retain this for data but hide it from view
    })

    if table_df.empty:
        return html.Div("No results."), None

    return dash_table.DataTable(
        id='transaction-table-town2',  # or 'transaction-table-town2'
        columns=[{"name": i, "id": i} for i in table_df.columns if i != "postal_code"],
        data=table_df.to_dict('records'),
        cell_selectable=True,
        active_cell=None,
        style_cell={
            'fontFamily': 'Inter, sans-serif',
            'textAlign': 'left',
            'padding': '16px',
            'border': 'none',
            'fontSize': '15px',
            'backgroundColor': '#f9f9f9',
        },
        style_data_conditional=[{
            'if': {'column_id': 'postal_code'},
            'display': 'none'
        }],
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
        selected_rows=[],
        page_size=10
    ), table_df.to_dict('records')


# Callback to update details on click
@callback(
    Output('property-details', 'children'),
    Input('transaction-table-town1', 'active_cell'),
    State('transaction-table-town1', 'data')
)
def display_details(active_cell, table_data):
    if not active_cell or not table_data:
        return ""

    row_idx = active_cell['row']
    row = table_data[row_idx]
    postal = row['postal_code']
    result = get_all_nearest_amenities(postal, hdb_df, schools_df, mrt_df, hawker_df)

    if result is None:
        return html.Div("⚠️ Unable to retrieve details.")

    return html.Div([
        html.H4("🏠 Property details", style={'marginBottom': '20px'}),
        html.P(f"📍 {result['address']}"),
        html.P(f"🚇 Nearest MRT: {result['mrt'][0]} ({result['mrt'][1]} km)"),
        html.P(f"🎓 Nearest School: {result['school'][0]} ({result['school'][1]} km)"),
        html.P(f"🍜 Nearest Hawker Center: {result['hawker'][0]} ({result['hawker'][1]} km)"),
        html.P(f"🏙️ Distance to CBD: {result['cbd_dist']} km"),

    ], style={
        "border": "1px solid lightgray",
        "padding": "20px",
        "borderRadius": "10px",
        "backgroundColor": "white",
        "fontFamily": "Inter, sans-serif",
        "width": "100%",
        "boxSizing": "border-box"
    })


@callback(
    Output('property-details-town2', 'children'),
    Input('transaction-table-town2', 'active_cell'),
    State('transaction-table-town2', 'data')
)
def display_details_town2(active_cell, table_data):
    if not active_cell or not table_data:
        return ""

    row_idx = active_cell['row']
    row = table_data[row_idx]
    postal = row['postal_code']
    result = get_all_nearest_amenities(postal, hdb_df, schools_df, mrt_df, hawker_df)

    if result is None:
        return html.Div("⚠️ Unable to retrieve details.")

    return html.Div([
        html.H4("🏠 Property details (Town 2)", style={'marginBottom': '20px'}),
        html.P(f"📍 {result['address']}"),
        html.P(f"🚇 Nearest MRT: {result['mrt'][0]} ({result['mrt'][1]} km)"),
        html.P(f"🎓 Nearest School: {result['school'][0]} ({result['school'][1]} km)"),
        html.P(f"🍜 Nearest Hawker Center: {result['hawker'][0]} ({result['hawker'][1]} km)"),
        html.P(f"🏙️ Distance to CBD: {result['cbd_dist']} km"),
    ], style={
        "border": "1px solid lightgray",
        "padding": "20px",
        "borderRadius": "10px",
        "backgroundColor": "white",
        "fontFamily": "Inter, sans-serif",
        "width": "100%",
        "boxSizing": "border-box"
    })



@callback(
    Output('map-markers', 'children'),
    Output('amenity-map', 'center'),
    Input('transaction-table-town1', 'selected_rows'),
    State('transaction-table-town1', 'data')
)
def update_map_and_center(selected_rows, table_data):
    if not selected_rows or not table_data:
        raise dash.exceptions.PreventUpdate

    selected_row = table_data[selected_rows[0]]
    postal_code = selected_row.get("postal_code")

    if not postal_code:
        raise dash.exceptions.PreventUpdate

    # Ensure string & zero-padded
    postal_code = str(postal_code).zfill(6)

    result = get_all_nearest_amenities(
        postal_code=postal_code,  # already string
        hdb_amenities_dist_with_postal=hdb_df,
        all_primary_schools=schools_df,
        mrt_stations=mrt_df,
        hawkercentrecoord=hawker_df
    )

    if result is None:
        raise dash.exceptions.PreventUpdate

    hdb_row = hdb_df[hdb_df['postal_code'] == postal_code]
    if hdb_row.empty:
        raise dash.exceptions.PreventUpdate

    hdb_lat = hdb_row.iloc[0]['latitude']
    hdb_lon = hdb_row.iloc[0]['longitude']

    def find_coords(name, df, name_col):
        row = df[df[name_col] == name]
        if not row.empty:
            return row.iloc[0]['latitude'], row.iloc[0]['longitude']
        return None, None

    mrt_lat, mrt_lon = find_coords(result["mrt"][0], mrt_df, 'station_name')
    sch_lat, sch_lon = find_coords(result["school"][0], schools_df, 'SchoolName')
    hawker_lat, hawker_lon = find_coords(result["hawker"][0], hawker_df, 'hc_name')

    markers = []
    if hdb_lat and hdb_lon:
        markers.append(dl.Marker(position=[hdb_lat, hdb_lon], children=dl.Tooltip("🏠 HDB Location")))
    if mrt_lat and mrt_lon:
        markers.append(dl.Marker(position=[mrt_lat, mrt_lon], children=dl.Tooltip(f"🚇 MRT: {result['mrt'][0]} ({result['mrt'][1]} km)")))
    if sch_lat and sch_lon:
        markers.append(dl.Marker(position=[sch_lat, sch_lon], children=dl.Tooltip(f"🏫 School: {result['school'][0]} ({result['school'][1]} km)")))
    if hawker_lat and hawker_lon:
        markers.append(dl.Marker(position=[hawker_lat, hawker_lon], children=dl.Tooltip(f"🍜 Hawker: {result['hawker'][0]} ({result['hawker'][1]} km)")))

    return markers, [hdb_lat, hdb_lon]

@callback(
    Output('map-markers-town2', 'children'),
    Output('amenity-map-town2', 'center'),
    Input('transaction-table-town2', 'selected_rows'),
    State('transaction-table-town2', 'data')
)
def update_map_and_center_town2(selected_rows, table_data):
    if not selected_rows or not table_data:
        raise dash.exceptions.PreventUpdate

    selected_row = table_data[selected_rows[0]]
    postal_code = selected_row.get("postal_code")

    if not postal_code:
        raise dash.exceptions.PreventUpdate

    postal_code = str(postal_code).zfill(6)

    result = get_all_nearest_amenities(
        postal_code=postal_code,
        hdb_amenities_dist_with_postal=hdb_df,
        all_primary_schools=schools_df,
        mrt_stations=mrt_df,
        hawkercentrecoord=hawker_df
    )

    if result is None:
        raise dash.exceptions.PreventUpdate

    hdb_row = hdb_df[hdb_df['postal_code'] == postal_code]
    if hdb_row.empty:
        raise dash.exceptions.PreventUpdate

    hdb_lat = hdb_row.iloc[0]['latitude']
    hdb_lon = hdb_row.iloc[0]['longitude']

    def find_coords(name, df, name_col):
        row = df[df[name_col] == name]
        if not row.empty:
            return row.iloc[0]['latitude'], row.iloc[0]['longitude']
        return None, None

    mrt_lat, mrt_lon = find_coords(result["mrt"][0], mrt_df, 'station_name')
    sch_lat, sch_lon = find_coords(result["school"][0], schools_df, 'SchoolName')
    hawker_lat, hawker_lon = find_coords(result["hawker"][0], hawker_df, 'hc_name')

    markers = []
    if hdb_lat and hdb_lon:
        markers.append(dl.Marker(position=[hdb_lat, hdb_lon], children=dl.Tooltip("🏠 HDB Location")))
    if mrt_lat and mrt_lon:
        markers.append(dl.Marker(position=[mrt_lat, mrt_lon], children=dl.Tooltip(f"🚇 MRT: {result['mrt'][0]} ({result['mrt'][1]} km)")))
    if sch_lat and sch_lon:
        markers.append(dl.Marker(position=[sch_lat, sch_lon], children=dl.Tooltip(f"🏫 School: {result['school'][0]} ({result['school'][1]} km)")))
    if hawker_lat and hawker_lon:
        markers.append(dl.Marker(position=[hawker_lat, hawker_lon], children=dl.Tooltip(f"🍜 Hawker: {result['hawker'][0]} ({result['hawker'][1]} km)")))

    return markers, [hdb_lat, hdb_lon]

@callback(
    Output('transaction-table-town1', 'style_data_conditional'),
    Input('transaction-table-town1', 'active_cell')
)
def style_active_row_town1(active_cell):
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
    if active_cell:
        row_idx = active_cell['row']
        style.append({
            'if': {'row_index': row_idx},
            'backgroundColor': '#7F0019',
            'color': 'white',
            'borderTop': '2px solid #dddddd'
        })
    return style

@callback(
    Output('transaction-table-town2', 'style_data_conditional'),
    Input('transaction-table-town2', 'active_cell')
)
def style_active_row_town2(active_cell):
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
    if active_cell:
        row_idx = active_cell['row']
        style.append({
            'if': {'row_index': row_idx},
            'backgroundColor': '#7F0019',
            'color': 'white',
            'borderTop': '2px solid #dddddd'
        })
    return style

@callback(
    Output('summary-toggle', 'options'),
    Output('summary-toggle', 'value'),
    Input('user-filter-store', 'data'),
)
def update_toggle_options(filter_data):
    if not filter_data:
        raise dash.exceptions.PreventUpdate

    town1 = filter_data.get('town1', 'Town 1')
    town2 = filter_data.get('town2', 'Town 2')

    options = [{'label': f'{town1.title()} ', 'value': 'town1'}]
    if town2:
        options.append({'label': f'{town2.title()} ', 'value': 'town2'})

    return options, 'town1'

@callback(
    Output('town1-name', 'children'),
    Output('town2-name', 'children'),
    Input('user-filter-store', 'data'),
)
def update_town_titles(filter_data):
    town1 = filter_data.get('town1', 'Town 1') if filter_data else 'Town 1'
    town2 = filter_data.get('town2', 'Town 2') if filter_data else 'Town 2'
    return town1.title(), town2.title()

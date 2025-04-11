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





# Layout
layout = html.Div([
    dcc.Location(id='url'),
    dcc.Store(id='map-center-store', storage_type='memory'),

    html.H2("Your Selected Filters", style={'fontFamily': 'Inter, sans-serif', 'textAlign': 'left', 'marginLeft': '100px'}),

    html.Div(id='filter-summary', style={'width': '80%', 'margin': 'auto', 'marginBottom': '20px'}),


    html.Div(id='bar-chart-section', children=[
        html.H2("Price trends for properties in the area", style={
            'textAlign': 'center', 'fontFamily': 'Inter, sans-serif', 'marginTop': '30px'
        }),
        html.P(id='bar-chart-subtitle', style={
            'textAlign': 'center', 'fontFamily': 'Inter, sans-serif', 'fontSize': '16px', 'marginBottom': '30px'
        }),
        html.Div(id='bar-chart-subtitle', style={'marginBottom': '10px', 'textAlign': 'center'
                                                 , 'fontFamily': 'Inter, sans-serif', 'fontSize': '16px'}),
    ]),
    html.Div([
        html.Div([
            # Chart
            html.Div([
                dcc.Graph(id='quarterly-bar-chart', config={'displayModeBar': False})
            ], style={'flex': '1', 'maxWidth': '50%', 'marginLeft': '100px'}),

            # Summary Box
            html.Div(id='price-summary', style={
                'flex': '1',
                'padding': '20px',
                'backgroundColor': '#f5f5f5',
                'border': '1px solid #ccc',
                'borderRadius': '10px',
                'marginLeft': '20px',
                'fontFamily': 'Inter, sans-serif'
            })
        ], style={
            'display': 'flex',
            'flexWrap': 'nowrap',
            'justifyContent': 'center',
            'alignItems': 'flex-start',
            'gap': '2px',
            'marginTop': '20px'
        })
    ]),

    html.H3("Recent Transactions Matching Your Filters", style={'textAlign': 'center', 'fontFamily': 'Inter, sans-serif', 
                                                                'marginTop': '20px', 'marginBottom': '20px'}),
    dcc.Store(id='selected-postal-store'),
    html.Div(id='filter-table'),

    html.Hr(),
    html.Div(id='property-details', style={'marginTop': '30px', 'width': '80%', 'margin': 'auto'}),
    html.Div([
        html.H3("Map of Nearby Amenities", style={
            'textAlign': 'center',
            'marginTop': '40px',
            'fontFamily': 'Inter, sans-serif'
        }),
        html.Div([
            dl.Map(id='amenity-map',
                center=[1.3521, 103.8198],
                zoom=12,
                children=[
                    dl.TileLayer(),
                    dl.LayerGroup(id='map-markers')
                ],
                style={'width': '100%', 'height': '400px'} 
                )], style={'width': '50%', 'margin': '0 auto'})  # <-- Shrink this to 50%
    ], style={'marginTop': '30px'})
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
    Output('price-summary', 'children'),
    Output('bar-chart-subtitle', 'children'),
    Output('filter-summary', 'children'),
    Input('user-filter-store', 'data')
)
def update_quarterly_chart(filter_data):
    import pandas as pd
    import plotly.express as px

    df = hdb_df.copy()
    
    if not filter_data:
        raise dash.exceptions.PreventUpdate

    # Extract filters
    town = filter_data.get('town')
    flat_type = filter_data.get('flat_type')
    floor_level = filter_data.get('floor_level')
    lease = filter_data.get('remaining_lease')
    max_mrt = filter_data.get('max_dist_mrt')
    max_sch = filter_data.get('max_dist_school')
    flat_type_col = f"flat_type_{flat_type}"

    # Apply filtering
    df = df[(df['town'] == town) & (df[flat_type_col] == 1)]
    # Floor level filter logic
    if floor_level:
        # Calculate the actual level range from string like '01 TO 03' in storey_median
        def extract_level_range(median_str):
            try:
                start, end = median_str.split(" TO ")
                return (int(start), int(end))
            except:
                return (None, None)

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

    # Time filtering
    months = [
        '2024-04', '2024-05', '2024-06', '2024-07', '2024-08', '2024-09',
        '2024-10', '2024-11', '2024-12', '2025-01', '2025-02', '2025-03'
    ]
    month_to_q = {m: f"Q{((int(m[5:7]) - 1) // 3) + 1} {m[:4]}" for m in months}
    df = df[df['month'].isin(months)]
    df['Quarter'] = df['month'].map(month_to_q)

    # Subtitle & Filter Summary
    subtitle = f"Based on flats in {town.title()} with {flat_type.title()} flat type and same amenity features"
    summary_filters = html.Ul([
        html.Li(f"🏙️ Town: {town}"),
        html.Li(f"🏠 Flat Type: {flat_type}"),
        html.Li(f"📏 Floor Level: {floor_level}"),
        html.Li(f"🕒 Min Lease: {lease} years") if lease else None,
        html.Li(f"🚇 Max Distance to MRT: {max_mrt} km") if max_mrt else None,
        html.Li(f"🏫 Max Distance to School: {max_sch} km") if max_sch else None
    ])

    # Empty case fallback
    if df.empty:
        fig = px.bar(
            x=['Q2 2024', 'Q3 2024', 'Q4 2024', 'Q1 2025'],
            y=[0, 0, 0, 0],
            labels={'x': 'Quarter', 'y': 'Avg Price (SGD)'},
            title='Average Price by Quarter',
            width=500,
            height=400
        )
        fig.update_traces(width=0.3, marker_color='lightgray')
        fig.update_layout(margin=dict(l=10, r=10, t=40, b=20))

        summary = html.Ul([
            html.Li("📊 Average Price: $0"),
            html.Li("📈 Max Price: No data available"),
            html.Li("📉 Min Price: No data available")
        ])
        return fig, summary, subtitle, summary_filters

    # Compute quarterly average
    q_avg = df.groupby('Quarter')['adjusted_resale_price'].mean().fillna(0).round().reset_index()
    q_avg['Quarter'] = pd.Categorical(q_avg['Quarter'], ['Q2 2024', 'Q3 2024', 'Q4 2024', 'Q1 2025'], ordered=True)
    q_avg = q_avg.sort_values('Quarter')

    # Bar chart
    fig = px.bar(
        q_avg,
        x='Quarter',
        y='adjusted_resale_price',
        labels={'adjusted_resale_price': 'Avg Price (SGD)'},
        title='Average Price by Quarter',
        width=500,
        height=400
    )
    fig.update_traces(width=0.3, marker_color='orange')
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=20))

    # Summary Stats
    avg = int(df['adjusted_resale_price'].mean())
    max_row = df.loc[df['adjusted_resale_price'].idxmax()]
    min_row = df.loc[df['adjusted_resale_price'].idxmin()]
    max_month = datetime.strptime(max_row['month'], "%Y-%m").strftime("%B %Y")
    min_month = datetime.strptime(min_row['month'], "%Y-%m").strftime("%B %Y")

    summary = html.Div([
            html.H3("Within the last year", style={"fontWeight": "bold", "fontSize": "24px", "marginBottom": "5px"}),
            html.P("Transactions from April 2024 - March 2025", style={"fontStyle": "italic", "fontSize": "16px", "marginBottom": "20px"}),

            html.H4("Average price of transactions", style={"fontSize": "20px", "marginBottom": "5px", "fontStyle":"italic"}),
            html.P(f"${avg:,}", style={"fontSize": "20px", "fontWeight": "bold", "marginBottom": "20px"}),

            html.H4("Highest transaction price", style={"fontSize": "20px", "marginBottom": "5px"}),
            html.P(f"${int(max_row['adjusted_resale_price']):,}", style={"fontSize": "20px", "fontWeight": "bold", "margin": "0"}),
            html.P(f"{max_row['address']}", style={"fontSize": "16px", "margin": "0", "fontStyle":"italic"}),
            html.P(f"{max_month}", style={"fontSize": "16px", "marginBottom": "20px"}),

            html.H4("Lowest transaction price", style={"fontSize": "20px", "marginBottom": "5px"}),
            html.P(f"${int(min_row['adjusted_resale_price']):,}", style={"fontSize": "20px", "fontWeight": "bold", "margin": "0"}),
            html.P(f"{min_row['address']}", style={"fontSize": "16px", "margin": "0", "fontStyle":"italic"}),
            html.P(f"{min_month}", style={"fontSize": "16px"})
        ], style={
            "padding": "20px",
            "backgroundColor": "#ffffff",  # <-- Set background to white
            "border": "1px solid #ccc",
            "borderRadius": "10px",
            "fontFamily": "Inter, sans-serif"
        })
    
    return fig, summary, subtitle, summary_filters

# Callback to filter and display table
@callback(
    Output('filter-table', 'children'),
    Output('selected-postal-store', 'data'),
    Input('user-filter-store', 'data'),
    Input('url', 'pathname'),
)
def update_table(filter_data, pathname):
    if pathname != "/output-general" or not filter_data:
        return html.Div("No data."), None

    town = filter_data.get('town')
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

    table_df = df[['address', 'adjusted_resale_price', 'month', 'postal_code', 'Distance to MRT (km)', 'Distance to School (km)']].rename(columns={
        'address': 'Address', 'adjusted_resale_price': 'Price (SGD)', 'month': 'Date Sold'
    })

    if table_df.empty:
        return html.Div("No results."), None

    return dash_table.DataTable(
        id='transaction-table',
        columns=[{"name": i, "id": i} for i in table_df.columns],
        data=table_df.to_dict('records'),
        row_selectable='single',
        style_cell={"textAlign": "left", "fontFamily": "Inter, sans-serif", "padding": "10px"},
        style_header={"fontWeight": "bold"},
        selected_rows=[],
        page_size=10
    ), table_df.iloc[0]['postal_code']  # default selection

# Callback to update details on click
@callback(
    Output('property-details', 'children'),
    Input('transaction-table', 'selected_rows'),
    State('transaction-table', 'data')
)
def display_details(selected_rows, table_data):
    if not selected_rows or not table_data:
        return ""

    row = table_data[selected_rows[0]]
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
        'fontFamily': 'Inter, sans-serif',
        'backgroundColor': '#fefefe',
        'border': '1px solid #ccc',
        'borderRadius': '10px',
        'padding': '20px',
        'textAlign': 'left'
    })


@callback(
    Output('map-markers', 'children'),
    Output('amenity-map', 'center'),
    Input('transaction-table', 'selected_rows'),
    State('transaction-table', 'data')
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

from dash import html, dcc, register_page, callback, Output, Input, State
import pandas as pd
import dash_leaflet as dl

# Load the CSV file
hdb_df = pd.read_csv('dataset/hdbdistamenitiescracked.csv')

# Preprocess: get unique towns and map postal codes by town
towns = sorted(hdb_df['town'].dropna().unique())
town_postal_map = hdb_df.groupby('town')['postal_code'].apply(list).to_dict()


register_page(__name__, path="/input-general")

layout = html.Div([
    html.H2("Find Your Ideal Home!", style={
        'fontFamily': 'Helvetica',
        'textAlign': 'center',
        'marginBottom': '20px'
    }),

    html.Div([

        # Town Dropdown
        html.Label("Select a Town:", style={'fontFamily': 'Helvetica'}),
        dcc.Dropdown(
            id='newbie-town-dropdown',
            options=[{'label': town.title(), 'value': town} for town in towns],
            placeholder="Select a town",
            style={'marginBottom': '25px', 'fontFamily': 'Helvetica'}
        ),

        # Postal Code Dropdown (dynamic)
        html.Label("Available Postal Codes:", style={'fontFamily': 'Helvetica'}),
        dcc.Dropdown(
            id='newbie-postal-dropdown',
            placeholder="Select a postal code",
            style={'marginBottom': '30px', 'fontFamily': 'Helvetica'}
        ),

        # Flat Type Dropdown
        html.Label("Flat Type:", style={'fontFamily': 'Helvetica'}),
        dcc.Dropdown(
            id='expert-flat-type',
            options=[
                {'label': '1 Room', 'value': '1 ROOM'},
                {'label': '2 Room', 'value': '2 ROOM'},
                {'label': '3 Room', 'value': '3 ROOM'},
                {'label': '4 Room', 'value': '4 ROOM'},
                {'label': '5 Room', 'value': '5 ROOM'},
                {'label': 'Executive', 'value': 'EXECUTIVE'},
                {'label': 'Multi-Generation', 'value': 'MULTI-GENERATION'}
            ],
            placeholder='Select Flat Type',
            style={'marginBottom': '15px', 'fontFamily': 'Helvetica'}
        ),

        # Floor Level Dropdown
        html.Label("Floor Level:", style={'fontFamily': 'Helvetica'}),
        dcc.Dropdown(
            id='expert-floor-level',
            options=[
                {'label': 'Low (01-03)', 'value': 'Low'},
                {'label': 'Mid (04-09)', 'value': 'Mid'},
                {'label': 'High (10 and above)', 'value': 'High'}
            ],
            placeholder='Select Floor Level',
            style={'marginBottom': '30px', 'fontFamily': 'Helvetica'}
        ),

        # Submit button inside a styled outer box
        html.Div([
            html.Button("Submit", id="newbie-submit", n_clicks=0, style={
                'backgroundColor': '#ff963b',
                'color': 'white',
                'padding': '10px 20px',
                'border': '2px solid #e67e22',
                'borderRadius': '8px',
                'fontSize': '16px',
                'cursor': 'pointer',
                'fontFamily': 'Helvetica'
            })
        ], style={
            'border': '2px solid #ccc',
            'padding': '10px',
            'borderRadius': '12px',
            'backgroundColor': '#fffaf3',
            'textAlign': 'center',
            'width': 'fit-content',
            'margin': '0 auto',
            'fontFamily': 'Helvetica'
        }),

        # Output text
        html.Div(id='newbie-output', style={'marginTop': '30px', 'fontFamily': 'Helvetica'}),

        # 🔍 Map
        # 🔍 Map
        html.Div([
            dl.Map(
                id="newbie-map",
                center=[1.3521, 103.8198],  # default center (static)
                zoom=11,  # default zoom (static)
                children=[
                    dl.TileLayer(),
                    dl.Marker(id="newbie-marker", position=[1.3521, 103.8198], children=[
                        dl.Popup(id="newbie-popup", children="Selected Location")
                    ])
                ],
                style={'width': '100%', 'height': '400px', 'marginTop': '20px'}
            )
        ], style={'marginTop': '40px'})
    ], style={'width': '50%', 'margin': '0 auto', 'padding': '40px', 'fontFamily': 'Helvetica'})
])

@callback(
    Output('newbie-output', 'children'),
    Input('newbie-submit', 'n_clicks'),
    State('newbie-postal-dropdown', 'value'),
    State('newbie-town-dropdown', 'value'),
)
def display_newbie_response(n_clicks, postal_code, town):
    if n_clicks > 0:
        if postal_code and not town:
            return html.Div(f"You've entered Postal Code: {postal_code}. We'll search properties around this area!")

        elif town and not postal_code:
            return html.Div(f"You've selected the town: {town}. We'll help you find the best listings there!")

        elif town and postal_code:
            # Fix: ensure type consistency for matching
            match = hdb_df[hdb_df['postal_code'].astype(str) == str(postal_code)]

            if not match.empty:
                block = str(match.iloc[0]['block']).strip()
                street = match.iloc[0]['street_name'].strip().title()
                return html.Div(f"You have entered {block} {street}, {town.title()} {postal_code}. We will search previous sales at this given address.")
            else:
                return html.Div(f"You entered Postal Code: {postal_code} and selected {town}, but we couldn't find the address in our database.")

        else:
            return html.Div("Please either select a postal code or a town.", style={'color': 'red'})

@callback(
    Output('newbie-postal-dropdown', 'options'),
    Input('newbie-town-dropdown', 'value')
)
def update_postal_options(selected_town):
    if selected_town and selected_town in town_postal_map:
        raw_postals = town_postal_map[selected_town]

        # ✅ Clean & deduplicate
        clean_postals = {int(p) for p in raw_postals if pd.notna(p) and str(p).isdigit()}
        sorted_postals = sorted(clean_postals)

        return [{'label': str(p), 'value': str(p)} for p in sorted_postals]
    return []

@callback(
    Output('newbie-marker', 'position'),
    Output('newbie-popup', 'children'),
    Input('newbie-submit', 'n_clicks'),
    State('newbie-postal-dropdown', 'value'),
    State('newbie-town-dropdown', 'value')
)
def update_map_marker_with_popup(n_clicks, postal_code, town):
    if n_clicks > 0 and postal_code:
        postal_str = str(postal_code)

        match = hdb_df[hdb_df['postal_code'] == postal_str]

        if not match.empty:
            lat = match.iloc[0]['latitude']
            lon = match.iloc[0]['longitude']
            block = str(match.iloc[0]['block']).strip()
            street = match.iloc[0]['street_name'].strip().title()
            address = f"{block} {street}, {town.title()} {postal_code}"
            return [lat, lon], address

    return [1.3521, 103.8198], "Selected Location"

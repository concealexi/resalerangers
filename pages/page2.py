from dash import html, dcc, register_page, callback, Output, Input, State

register_page(__name__, path="/page-2")

layout = html.Div([
    html.H2("Find Your Ideal Home!", style={
        'fontFamily': 'Helvetica',
        'textAlign': 'center',
        'marginBottom': '20px'
    }),

    html.Div([
        html.Label("Enter Postal Code (optional):", style={'fontFamily': 'Helvetica'}),
        dcc.Input(
            id='newbie-postal-code',
            type='number',
            placeholder='e.g. 123456',
            style={
                'padding': '10px',
                'fontSize': '16px',
                'width': '100%',
                'marginBottom': '25px',
                'fontFamily': 'Helvetica'
            }
        ),

        html.Label("Or Select a Town:", style={'fontFamily': 'Helvetica'}),
        dcc.Dropdown(
            id='newbie-town-dropdown',
            options=[
                {'label': 'North - Sembawang', 'value': 'Sembawang'},
                {'label': 'North - Woodlands', 'value': 'Woodlands'},
                {'label': 'North - Yishun', 'value': 'Yishun'},
                {'label': 'North-East - Ang Mo Kio', 'value': 'Ang Mo Kio'},
                {'label': 'North-East - Hougang', 'value': 'Hougang'},
                {'label': 'North-East - Punggol', 'value': 'Punggol'},
                {'label': 'North-East - Sengkang', 'value': 'Sengkang'},
                {'label': 'North-East - Serangoon', 'value': 'Serangoon'},
                {'label': 'East - Bedok', 'value': 'Bedok'},
                {'label': 'East - Pasir Ris', 'value': 'Pasir Ris'},
                {'label': 'East - Tampines', 'value': 'Tampines'},
                {'label': 'West - Bukit Batok', 'value': 'Bukit Batok'},
                {'label': 'West - Bukit Panjang', 'value': 'Bukit Panjang'},
                {'label': 'West - Choa Chu Kang', 'value': 'Choa Chu Kang'},
                {'label': 'West - Clementi', 'value': 'Clementi'},
                {'label': 'West - Jurong East', 'value': 'Jurong East'},
                {'label': 'West - Jurong West', 'value': 'Jurong West'},
                {'label': 'West - Tengah', 'value': 'Tengah'},
                {'label': 'Central - Bishan', 'value': 'Bishan'},
                {'label': 'Central - Bukit Merah', 'value': 'Bukit Merah'},
                {'label': 'Central - Bukit Timah', 'value': 'Bukit Timah'},
                {'label': 'Central - Central Area', 'value': 'Central Area'},
                {'label': 'Central - Geylang', 'value': 'Geylang'},
                {'label': 'Central - Kallang/ Whampoa', 'value': 'Kallang/ Whampoa'},
                {'label': 'Central - Marine Parade', 'value': 'Marine Parade'},
                {'label': 'Central - Queenstown', 'value': 'Queenstown'},
                {'label': 'Central - Toa Payoh', 'value': 'Toa Payoh'},
            ],
            placeholder="Select a town",
            style={'marginBottom': '30px', 'fontFamily': 'Helvetica'}
        ),

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

        # Stylized Button inside bordered box
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
            'padding': '2px',
            'borderRadius': '12px',
            'backgroundColor': '#fffaf3',
            'textAlign': 'center',
            'width': 'fit-content',
            'margin': '0 auto',
            'fontFamily': 'Helvetica'
        }),

        html.Div(id='newbie-output', style={'marginTop': '30px', 'fontFamily': 'Helvetica'})
    ], style={'width': '50%', 'margin': '0 auto', 'padding': '40px', 'fontFamily': 'Helvetica'})
])

@callback(
    Output('newbie-output', 'children'),
    Input('newbie-submit', 'n_clicks'),
    State('newbie-postal-code', 'value'),
    State('newbie-town-dropdown', 'value'),
)
def display_newbie_response(n_clicks, postal_code, town):
    if n_clicks > 0:
        if postal_code and not town:
            return html.Div(f"You've entered Postal Code: {postal_code}. We'll search properties around this area!")
        elif town and not postal_code:
            return html.Div(f"You've selected the town: {town}. We'll help you find the best listings there!")
        elif town and postal_code:
            return html.Div(f"You entered both Postal Code: {postal_code} and selected {town}. We’ll prioritize the postal code but use town as fallback.")
        else:
            return html.Div("Please either enter a postal code or select a town.", style={'color': 'red'})


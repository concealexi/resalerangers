from dash import html, dcc, register_page, callback, Output, Input, State

register_page(__name__, path="/page-3")

layout = html.Div([
    html.H2("Page 3"),
    html.P("You got here from the button! 🎉"),
    html.Div([
        html.Label("Postal Code:", style={'fontFamily': 'Roboto'}),
        dcc.Input(id='expert-postal-code', type='number', placeholder='Enter postal code', style={
            'padding': '10px',
            'fontSize': '16px',
            'marginBottom': '15px',
            'width': '100%'
        }),
    ]),

    # Flat Type Dropdown
    html.Div([
        html.Label("Flat Type:", style={'fontFamily': 'Roboto'}),
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
            style={'marginBottom': '15px', 'fontFamily': 'Roboto'}
        ),
    ]),

    # Flat Category Dropdown
    html.Div([
        html.Label("Flat Category:", style={'fontFamily': 'Roboto'}),
        dcc.Dropdown(
            id='expert-flat-category',
            options=[
                {'label': 'HDB', 'value': 'HDB'},
                {'label': 'DBSS', 'value': 'DBSS'},
                {'label': 'Maisonette', 'value': 'MAISONETTE'},
                {'label': 'Terrace', 'value': 'TERRACE'}
            ],
            placeholder='Select Flat Category',
            style={'marginBottom': '15px', 'fontFamily': 'Roboto'}
        ),
    ]),

    # Floor Level Dropdown
    html.Div([
        html.Label("Floor Level:", style={'fontFamily': 'Roboto'}),
        dcc.Dropdown(
            id='expert-floor-level',
            options=[
                {'label': 'Low (01-03)', 'value': 'Low'},
                {'label': 'Mid (04-09)', 'value': 'Mid'},
                {'label': 'High (10 and above)', 'value': 'High'}
            ],
            placeholder='Select Floor Level',
            style={'marginBottom': '20px', 'fontFamily': 'Roboto'}
        ),
    ]),

    # Submit Button
    html.Button('Submit', id='submit-expert-input', n_clicks=0, style={
        'padding': '10px 20px',
        'fontSize': '16px',
        'cursor': 'pointer',
        'backgroundColor': '#ff963b',
        'color': 'white',
        'border': 'none',
        'borderRadius': '8px'
    }),

    # Placeholder for output (e.g., predictions or confirmations)
    html.Div(id='expert-output', style={'marginTop': '20px', 'fontFamily': 'Roboto'})
], style={'width': '50%', 'margin': '0 auto', 'padding': '40px'})
    
@callback(
    Output('expert-output', 'children'),
    Input('submit-expert-input', 'n_clicks'),
    State('expert-postal-code', 'value'),
    State('expert-flat-type', 'value'),
    State('expert-flat-category', 'value'),
    State('expert-floor-level', 'value'),
)
def capture_expert_input(n_clicks, postal_code, flat_type, flat_category, floor_level):
    if n_clicks > 0:
        if None in (postal_code, flat_type, flat_category, floor_level):
            return html.Div("Please fill in all the fields.", style={'color': 'red'})
        else:
            # Here is where you would typically call your prediction model
            return html.Div([
                html.H4("Inputs captured successfully!", style={'color': 'green'}),
                html.Ul([
                    html.Li(f"Postal Code: {postal_code}"),
                    html.Li(f"Flat Type: {flat_type}"),
                    html.Li(f"Flat Category: {flat_category}"),
                    html.Li(f"Floor Level: {floor_level}")
                ])
            ])

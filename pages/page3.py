from dash import html, dcc, register_page, callback, Output, Input, State

register_page(__name__, path="/page-3")

layout = html.Div([
    html.H2("Welcome to the Expert Page", style={'fontFamily': 'Roboto', 'textAlign': 'center'}),
    html.P("We will help you to predict a reasonable price for HDBs with your preferred features! "
           "Enter a postal code for an area that you want to live in, the flat type, and the floor level "
           "that you want — and we'll tell you a reasonable price for that unit!",
           style={'fontFamily': 'Roboto', 'textAlign': 'center', 'marginBottom': '30px'}),

    html.Div([

        # Postal Code
        html.Label("Postal Code:", style={'fontFamily': 'Roboto'}),
        dcc.Input(id='expert-postal-code', type='number', placeholder='Enter postal code', style={
            'padding': '10px',
            'fontSize': '16px',
            'marginBottom': '20px',
            'width': '100%'
        }),

        # Flat Type Dropdown
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
            style={'marginBottom': '20px', 'fontFamily': 'Roboto'}
        ),

        # Floor Level Dropdown
        html.Label("Floor Level:", style={'fontFamily': 'Roboto'}),
        dcc.Dropdown(
            id='expert-floor-level',
            options=[
                {'label': 'Low (01-03)', 'value': 'Low'},
                {'label': 'Mid (04-09)', 'value': 'Mid'},
                {'label': 'High (10 and above)', 'value': 'High'}
            ],
            placeholder='Select Floor Level',
            style={'marginBottom': '30px', 'fontFamily': 'Roboto'}
        ),

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

        # Output
        html.Div(id='expert-output', style={'marginTop': '30px', 'fontFamily': 'Roboto'})
    ], style={'width': '50%', 'margin': '0 auto'})
])

def postal_minus_one(postal_code):
    try:
        return postal_code - 1
    except TypeError:
        return None


@callback(
    Output('expert-output', 'children'),
    Input('submit-expert-input', 'n_clicks'),
    State('expert-postal-code', 'value'),
    State('expert-flat-type', 'value'),
    State('expert-floor-level', 'value'),
)
def capture_expert_input(n_clicks, postal_code, flat_type, floor_level):
    if n_clicks > 0:
        if None in (postal_code, flat_type, floor_level):
            return html.Div("Please fill in all the fields.", style={'color': 'red'})
        else:
            adjusted_postal = postal_minus_one(postal_code)
            return html.Div([
                html.H4("Inputs captured successfully!", style={'color': 'green'}),
                html.Ul([
                    html.Li(f"Postal Code: {postal_code}"),
                    html.Li(f"Flat Type: {flat_type}"),
                    html.Li(f"Floor Level: {floor_level}"),
                    html.Li(f"Postal Code - 1: {adjusted_postal}")
                ])
            ])

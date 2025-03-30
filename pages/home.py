import dash
from dash import html, dcc, register_page

register_page(__name__, path="/")

# Card style (shared)
card_style = {
    'backgroundColor': 'white',
    'padding': '20px 20px 60px 20px',
    'borderRadius': '10px',
    'width': '400px',
    'textAlign': 'center',
    'boxShadow': '0 4px 8px rgba(0,0,0,0.1)',
    'transition': 'transform 0.3s, box-shadow 0.3s',
    'cursor': 'pointer',
    'textDecoration': 'none',
}

layout = html.Div([
    html.Div([

        # Title
        html.H1("Choose Your Persona!", style={
            'textAlign': 'center',
            'color': 'white',
            'fontFamily': 'Roboto, sans-serif',
            'marginTop': '30px'
        }),

        # Cards container
        html.Div([

            # Newbie Card (clickable)
            dcc.Link(html.Div([
                html.Div(style={  
                    'height': '450px',
                    'backgroundColor': '#ff963b',
                    'borderRadius': '10px',
                    'marginBottom': '20px'
                }),
                html.H3("Newbie", style={'fontFamily': 'Roboto'}),
                html.P("You don't know where you want to live and want to find something fitting your price range", style={'fontFamily': 'Roboto'})
            ], className="hover-card", style=card_style), href='/page-2', style={'textDecoration': 'none'}),

            # Expert Card (clickable)
            dcc.Link(html.Div([
                html.Div(style={
                    'height': '450px',
                    'backgroundColor': '#ff963b',
                    'borderRadius': '10px',
                    'marginBottom': '20px'
                }),
                html.H3("Expert", style={'fontFamily': 'Roboto'}),
                html.P("You have an idea on where you want to live and check whether the given price is reasonable", style={'fontFamily': 'Roboto'})
            ], className="hover-card", style=card_style), href='/page-3', style={'textDecoration': 'none'})

        ], style={
            'display': 'flex',
            'justifyContent': 'center',
            'gap': '40px',
            'marginTop': '50px'
        }),

    ], style={
        'padding': '40px',
        'backgroundColor': '#ff963b',
        'minHeight': '100vh',
        'fontFamily': 'Roboto, sans-serif'
    })
])

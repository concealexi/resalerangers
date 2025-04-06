import dash
from dash import html, dcc, register_page

register_page(__name__, path="/")

# Shared card style for the cards section
card_style = {
    'width': '400px',
    'height': '400px',
    'border': '6px solid #944028',
    'borderRadius': '20px',
    'padding': '20px',
    'display': 'flex',
    'flexDirection': 'column',
    'alignItems': 'center',
    'textAlign': 'center',
    'backgroundColor': '#fff'
}

# Top section with title, subtitle, and horizontal line with circles
top_section = html.Div([
    html.H1(
        "'Fair' Price",
        style={
            'textAlign': 'center',
            'fontFamily': 'Inter, sans-serif',
            'fontWeight': 'bold',
            'fontSize': '2.2rem',
            'margin': '20px 0 5px 0',
            'color': 'black'
        }
    ),
    html.P(
        [
            "to buy or not to buy",
            html.Br(),
            "- someone important probably"
        ],
        style={
            'textAlign': 'center',
            'fontFamily': 'Inter, sans-serif',
            'margin': '0 0 20px 0',
            'color': 'black',
            'fontWeight': 'bold'
        }
    ),
    html.Div(
        style={
            'width': '80%',
            'margin': '0 auto 20px auto',
            'borderBottom': '3px solid #944028',
            'position': 'relative'
        },
        children=[
            # Left circle
            html.Div(
                style={
                    'width': '15px',
                    'height': '15px',
                    'backgroundColor': '#944028',
                    'borderRadius': '50%',
                    'position': 'absolute',
                    'left': '-7.5px',
                    'top': '-6px'
                }
            ),
            # Right circle
            html.Div(
                style={
                    'width': '15px',
                    'height': '15px',
                    'backgroundColor': '#944028',
                    'borderRadius': '50%',
                    'position': 'absolute',
                    'right': '-7.5px',
                    'top': '-6px'
                }
            )
        ]
    )
])

layout = html.Div([
    # Top section moved from app.py
    top_section,

    # Prompt text
    html.Div(
        [
            "Firstly, what kind of user are you?",
            html.Br(),
            "This lets us better address your needs"
        ],
        style={
            'textAlign': 'center',
            'fontFamily': 'Inter, sans-serif',
            'fontWeight': 'bold',
            'color': 'black',
            'marginBottom': '40px',
            'fontSize': '1.1rem'
        }
    ),

    # Cards container with links
    html.Div(
        children=[
            # Left Card
            dcc.Link(
                html.Div([
                    # Icon container at the top
                    html.Div(
                        html.Img(
                            src='https://img.icons8.com/ios-filled/100/marker.png',
                            style={
                                'width': '90px',
                                'marginBottom': '10px',
                                'filter': 'invert(45%) sepia(100%) saturate(250%) hue-rotate(340deg) brightness(70%) contrast(115%)'
                            }
                        ),
                        style={
                            'width': '100%',
                            'display': 'flex',
                            'justifyContent': 'center',
                            'marginTop': '20px'
                        }
                    ),
                    # Spacer to push text down
                    html.Div(style={'flexGrow': 1}),
                    # Text container
                    html.Div([
                        html.H2([
                            "I want to check a",
                            html.Br(),
                            "specific location"
                        ], style={
                            'fontFamily': 'Inter, sans-serif', 
                            'color': '#333',
                            'height': '110px',
                            'marginBottom': '-12.5px'
                        }),
                        html.P(
                            [
                                "We can predict a price range of a",
                                html.Br(),
                                "flat based on its key characteristics"
                            ],
                            style={
                                'fontFamily': 'Inter, sans-serif', 
                                'color': '#555',
                                'height': '62.5px'
                            }
                        )
                    ], style={'marginBottom': '20px'})
                ], style=card_style),
                href='/input-specific-dummy',
                style={'textDecoration': 'none'}
            ),

            # Right Card
            dcc.Link(
                html.Div([
                    # Icon container at the top
                    html.Div(
                        html.Img(
                            src='https://img.icons8.com/ios-filled/100/map.png',
                            style={
                                'width': '90px',
                                'marginBottom': '10px',
                                'filter': 'invert(45%) sepia(100%) saturate(250%) hue-rotate(340deg) brightness(70%) contrast(115%)'
                            }
                        ),
                        style={
                            'width': '100%',
                            'display': 'flex',
                            'justifyContent': 'center',
                            'marginTop': '20px'
                        }
                    ),
                    # Spacer to push text down
                    html.Div(style={'flexGrow': 1}),
                    # Text container
                    html.Div([
                        html.H2([
                            "I want to look",
                            html.Br(),
                            "at general areas"
                        ], style={
                            'fontFamily': 'Inter, sans-serif', 
                            'color': '#333',
                            'height': '110px',
                            'marginBottom': '-25px'
                        }),
                        html.P(
                            [
                                "We can provide past transactional",
                                html.Br(),
                                "data based on the town of choice",
                                html.Br(),
                                "and some characteristics"
                            ],
                            style={
                                'fontFamily': 'Inter, sans-serif', 
                                'color': '#555',
                                'height': '75px'
                            }
                        )
                    ], style={'marginBottom': '20px'})
                ], style=card_style),
                href='/input-general',
                style={'textDecoration': 'none'}
            )
        ],
        style={
            'display': 'flex',
            'justifyContent': 'center',
            'gap': '150px',
            'flexWrap': 'wrap',
            'margin': '0 auto'
        }
    ),

    # Footer or small text section
    html.Div(
        "This is a property of Resale Rangers",
        style={
            'textAlign': 'center',
            'fontFamily': 'Inter, sans-serif',
            'color': '#888',
            'marginTop': '150px',
            'fontSize': '0.9rem'
        }
    )
],
style={
    'margin': '0',
    'padding': '0',
    'minHeight': '100vh',
    'backgroundColor': '#FFFFFF',
    'display': 'flex',
    'flexDirection': 'column',
    'justifyContent': 'flex-start'
})

import dash
from dash import html, dcc, Input, Output, callback, register_page
import joblib
import xgboost as xgb
from models.model_tuning import conformal_predict

# Register page 4 for proper routing
register_page(__name__, path="/page-4")

# Load the saved model package (assumes "models/final_model.pkl" exists)
model_package = joblib.load("models/final_model.pkl")
model = model_package['model']
q_value = model_package['q_value']

# Temporary default input vector for prediction
# (The order should match your exogenous variables:
# ['remaining_lease', 'min_dist_sch', 'storey_median', 'min_dist_mrt',
#  'floor_area_sqm', 'min_dist_cbd', 'flat_type_1 ROOM', 'flat_type_2 ROOM', 
#  'flat_type_3 ROOM', 'flat_type_4 ROOM', 'flat_type_5 ROOM', 
#  'flat_type_EXECUTIVE', 'flat_type_MULTI-GENERATION'])
default_input = [70,0.415218792367851,8.0,1.0811219644208,60,9.76408651954306,0,0,1,0,0,0,0]

layout = html.Div([
    html.H2("Fair Price Prediction"),
    html.P("This page was reached via redirect from page 3. Using default input values for prediction."),
    html.Button("Predict", id="predict-button", n_clicks=0, style={"margin-top": "20px"}),
    html.Div(id="prediction-output", style={"margin-top": "20px", "font-weight": "bold"})
])

@callback(
    Output("prediction-output", "children"),
    Input("predict-button", "n_clicks")
)
def predict_fair_price(n_clicks):
    if n_clicks:
        try:
            # Use the default input vector until dynamic input is available
            input_vector = default_input
            # Call your conformal_predict function from model_tuning
            y_pred, y_lower, y_upper = conformal_predict(model, input_vector, q_value)
            return html.Div([
                html.P(f"Predicted Price: {y_pred[0]:.2f}"),
                html.P(f"90% Confidence Interval: [{y_lower[0]:.2f}, {y_upper[0]:.2f}]")
            ])
        except Exception as e:
            return f"Error in prediction: {e}"
    return ""

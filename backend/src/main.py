import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import xgboost as xgb
from model_tuning import tune, conformal_predict

def main():
    # Step 1: Load your data
    df = pd.read_csv("../data/hdb_amenities_dist.csv")  # Replace with your actual dataset
    exog = ['remaining_lease', 'min_dist_sch', 'storey_median', 'min_dist_mrt',
        'floor_area_sqm', 'min_dist_cbd', 'flat_type_1 ROOM', 'flat_type_2 ROOM', 
        'flat_type_3 ROOM', 'flat_type_4 ROOM', 'flat_type_5 ROOM', 'flat_type_EXECUTIVE', 
        'flat_type_MULTI-GENERATION']
    
    X = df[exog]
    y = df["adjusted_resale_price"]

    # Step 2: Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Step 3: Tune model + retrain with custom asymmetric loss
    bst_final = tune(model=xgb.XGBRegressor(objective = "reg:squarederror"),
                     X_train=X_train,
                     y_train=y_train,
                     X_test=X_test,
                     y_test=y_test,
                     model_type="xgboost",
                     scoring="neg_root_mean_squared_error",
                     n_iter=10)

    # Step 4: Use full training set for calibration
    dcalib = xgb.DMatrix(X_train)
    y_calib_pred = bst_final.predict(dcalib)
    residuals = np.abs(y_train - y_calib_pred)
    ## this can be reset 
    alpha = 0.1
    q = np.quantile(residuals, 1 - alpha)  # 90% conformal interval

    # Step 5: Prompt user input
    print("\nPlease enter the following values (comma-separated):")
    print(", ".join(exog))
    user_input_str = input("Enter values in order: ")

    # Convert to list of floats
    try:
        user_input = list(map(float, user_input_str.strip().split(",")))
        assert len(user_input) == len(exog)
    except:
        print(f"[ERROR] Please enter exactly {len(exog)} comma-separated numeric values.")
        return

    # Step 6: Predict and display interval
    conformal_predict(bst_final, user_input, q)

if __name__ == "__main__":
    main()

# src/hyperparameter_tuning.py

import numpy as np
from sklearn.model_selection import RandomizedSearchCV
import xgboost as xgb
import pandas as pd

def get_param_distributions( model_type: str):
    """
    Returns a dictionary of parameter distributions for RandomizedSearchCV
    based on the specified task_type (regression/classification) and model_type.
    
    You can customize these distributions further or reduce them
    for faster experiments.
    """
    # Example distributions; tweak as needed
    
    if model_type == "random_forest":
        # Random Forest for Regression
        return {
            "max_depth": [None, 10, 15, 20,30,35,40],
            "min_samples_split": [2, 5, 10,20,50],
            "min_samples_leaf": [1, 2, 5,10,20],
            "max_features": ["sqrt", "log2", 0.3, 0.5,0.2,0.4],
            "n_estimators" :[50, 100, 200, 500] }

        
    elif model_type == "xgboost":
        # XGBoost for Regression
        return {
                "max_depth": [5, 10, 15, 20],
                "eta": [0.05, 0.1, 0.2, 0.3],
                "subsample": [0.7, 0.8, 0.9, 1.0],
                "colsample_bytree": [0.7, 0.8, 0.9, 1.0],
                "lambda": [0.1, 1.0, 10.0],
                "alpha": [0.1, 1.0, 10.0],
                "num_boost_round": [500, 1000],
                }

    else:
        raise ValueError(f"Unsupported model_type '{model_type}' for regression.")
    
    


def tune(model, X_train, y_train,
                         X_test,y_test,
                         model_type: str,
                         scoring=None,
                         cv=5,
                         n_iter=20,
                         n_jobs=-1,
                         random_state=42,
                         verbose=1):
    """
    Performs hyperparameter tuning using RandomizedSearchCV on the given model.
    
    Parameters:
        model: An instantiated model (e.g., RandomForestRegressor, XGBRegressor, etc.)
        X_train (pd.DataFrame or np.array): Training features
        y_train (pd.Series or np.array): Training target
        task_type (str): 'regression' or 'classification'
        model_type (str): e.g., 'random_forest', 'xgboost', 'logistic_regression'
        scoring (str or callable): Scoring metric for RandomizedSearchCV 
        cv (int): Number of cross-validation folds
        n_iter (int): Number of parameter settings sampled in RandomizedSearchCV
        n_jobs (int): Number of parallel jobs (-1 = use all cores)
        random_state (int): Random seed for reproducibility
        verbose (int): Verbosity level for RandomizedSearchCV
    
    Returns:
        best_model: The best estimator found by RandomizedSearchCV
        best_params: The parameter setting that gave the best results
    """
    # Get parameter distributions for the specified model & task
    param_distributions = get_param_distributions(model_type)
    
    # Set up RandomizedSearchCV
    searcher = RandomizedSearchCV(
        estimator=model,
        param_distributions=param_distributions,
        n_iter=n_iter,
        scoring=scoring,
        cv=cv,
        n_jobs=n_jobs,
        random_state=random_state,
        verbose=verbose
    )
    

    # Custom loop to track progress
   
    # Fit the search
    searcher.fit(X_train, y_train)
    
    best_params = searcher.best_params_


    """2. Retrain The best model with asymmetric loss such that it favor overetimation
rationale -> we want to reduce rate of underestimation, as that might impact buyers more
will then train the current model with the custom loss to tune it further"""
# FINAL MODEL!! 

    if model_type=="xgboost":
        bst_final_xgboost = train_with_custom_loss(X_train, y_train, X_test, y_test, best_params)
        print(f"\n[INFO] Best params found by RandomizedSearchCV: {best_params}")
        print(f"[INFO] Best score: {searcher.best_score_:.4f}")
        return bst_final_xgboost

    else :
        return searcher.best_estimator_



## for xgboost to train with assymetric losse

def asymmetric_overpricing_loss(y_pred, dtrain, alpha = 3):
    y_true = dtrain.get_label()
    residual = y_pred - y_true  

    grad = np.where(residual < 0, alpha * residual, residual)
    hess = np.where(residual < 0, alpha, 1)

    return grad, hess

def train_with_custom_loss(X_train, y_train, X_test, y_test, best_params):
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dtest = xgb.DMatrix(X_test, label=y_test)

    params = {
        **best_params,  #take best params from our prev randomsearch results
        "verbosity": 1, 
        "seed": 42,      
    }

    bst = xgb.train(
        params=params,
        dtrain=dtrain,
        num_boost_round=best_params['num_boost_round'],  
        obj=asymmetric_overpricing_loss, #our custom loss function
        evals=[(dtest, "eval")],
        early_stopping_rounds=20, #stop early if no improvement
        verbose_eval=True
    )

    return bst

## for conformal prediction 
def conformal_predict(model, X_input, q):
    """
    Returns prediction and (lower, upper) bounds of the conformal prediction interval
    X_input in [[exog]] format
    q is fiexed from above 
    """
    exog = ['remaining_lease', 'min_dist_sch', 'storey_median', 'min_dist_mrt',
        'floor_area_sqm', 'min_dist_cbd', 'flat_type_1 ROOM', 'flat_type_2 ROOM', 
        'flat_type_3 ROOM', 'flat_type_4 ROOM', 'flat_type_5 ROOM', 'flat_type_EXECUTIVE', 
        'flat_type_MULTI-GENERATION']
    data=pd.DataFrame([X_input], columns=exog)
    dinput = xgb.DMatrix(data)
    y_pred = model.predict(dinput)
    y_lower = y_pred - q
    y_upper = y_pred + q
    print(f" Predicted: {y_pred[0]:.2f}, 90% CI: [{y_lower[0]:.2f}, {y_upper[0]:.2f}]")
    return y_pred, y_lower, y_upper

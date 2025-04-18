# HDB Resale Radar App
<img src="assets/applogo.png" alt="App Logo" width="200" height="200"/>

Authors: Team Resale Rangers

## Overview
Buying a resale HDB flat in Singapore can feel like navigating a maze.Prices vary even within the same town, and current platforms don’t help users assess whether listings are overpriced or reasonable.

This project is a visual, data-driven platform designed to help users make informed decisions in Singapore’s HDB resale market.
It leverages historical transaction data, machine learning predictions, and geospatial filtering to provide price prediction and intuitive visualizations of current trends and pricing context.

The data is provided by Housing Development Board of Singapore. 

The data is available on [data.gov.sg] (https://data.gov.sg/).
- [Resale Flat Prices] (https://data.gov.sg/collections/189/view)

## Packages used
**Web framework:** dash, flask  
**Data processing:** pandas, numpy  
**Machine learning:** xgboost, joblib  
**Geospatial utilities:** haversine, geopy, geohash  
**Visualization:** plotly


# How to run the app locally
1. **Clone this repository**
2. **Ensure Python 3.7+ is installed**
3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
4. **Run App!**

   ```bash
   python app.py
   # or
   python3 app.py
5. **Open the link in the terminal in your browser**

   It should look something like:

   ```text
   http://127.0.0.1:8050# backend folder 

This directory contains our end-to-end pipeline for predicting HDB resale prices in Singapore using Random Forest and XGBoost, with enhancements like geospatial feature engineering, asymmetric loss functions, and conformal prediction for uncertainty quantification.

---

##  Technologies

###  Pre-processing Steps

Before model training, we performed the following:

- **Finalized Data:**  
  Cleaned and standardized resale flat transaction data from **2015–2024**.

- **Geocoding:**  
  Used the [OneMap API](https://www.onemap.gov.sg/) to convert addresses into latitude/longitude coordinates.

- **General Cleaning:**  
  - Merged datasets  
  - Handled missing values and duplicates  
  - Adjusted prices for inflation and floor level

- **Distance Calculations:**  
  Computed distances to:
  - MRT stations  
  - Hawker centres  
  - Schools  
  - CBD

- **Auxiliary Datasets:**  
  Integrated external data (e.g. MRT, schools, hawker centres) to:
  - Enrich feature engineering  
  - Improve dashboard visualizations

---

##  `Model_walkthrough.ipynb`

This notebook walks through the full pipeline:

- Model tuning and cross-validation  
- Asymmetric training of XGBoost  
- Performance comparison between RF and XGBoost  
- Final model export

### ✅ Steps to run the notebook

1. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
2. **follow the instruction in the notebook**

##  Technologies (Modelling)

###  Random Forest

- **Strengths**
  - Robust to overfitting  
  - Handles non-linear relationships  
  - Requires minimal tuning

- **Limitations**
  - Cannot use custom loss functions  
  - Less flexibility when penalizing underestimates

---

###  XGBoost (Final Model Chosen)

- **Strengths**
  - High accuracy due to gradient boosting  
  - Supports custom loss functions  
  - Implemented asymmetric loss to favor **overprediction** and avoid **underestimation**

- **Limitations**
  - More sensitive to overfitting  
  - Requires careful hyperparameter tuning

---

##  Methodologies & `model_tuning.py` Functions

###  Hyperparameter Tuning + Cross-Validation

- **Function:** `tune`

- **Tuning Strategy:**
  - `RandomizedSearchCV`  
    Efficiently explores the hyperparameter space using random sampling

- **Parameters:**
  - `n_iter = 20`:  
    Tries 20 random combinations to balance performance and computation time
  - `cv = 5`:  
    5-fold cross-validation ensures stable evaluation

- **Customization:**
  - To adjust the number of folds (`cv`) or iterations (`n_iter`), edit the `tune` function in `model_tuning.py`

---

###  Asymmetric Loss Function

- **Function:** `Asymmetric_overpriceing_loss`

- **Purpose:**  
  Penalizes **underpredictions** more heavily than **overpredictions**

- **Parameter:**
  - `alpha` controls the severity of the penalty  
    - e.g., `alpha = 3` → underpredicting by $10k = overpredicting by $30k

- **Impact:**  
  Encourages the model to avoid underestimating resale values, which is often more harmful in policy or planning contexts

- **Integration with XGBoost:**
  - Use via `obj` argument in `xgb.train()`

---

##  Conformal Prediction

- **Purpose:**  
  Provide prediction **intervals** along with the point estimate, to express model **uncertainty**

- **Function Signature:**
  ```python
  conformal_predict(model, X_input, q)

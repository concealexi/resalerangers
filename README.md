# HDB Resale Radar App
<img src="assets/applogo.png" alt="App Logo" width="200" height="200"/>

Authors: Team Resale Rangers

## Overview
This project is aimed at providing a data-driven tool to assist users in making informed decisions when exploring the HDB resale market in Singapore. We focus on two key user needs: predicting fair resale prices and providing transaction trends and insight on amenities. Users, based on their needs and preferences, can either input a specific flat to receive an instant price prediction, or explore general trends across different towns and flat types.

The data is sourced from publicly available HDB resale transactions, complemented with auxiliary datasets on MRT stations, schools, hawker centres, and geocoded distances. We believe this project can serve as a valuable reference for homebuyers navigating the resale market and for individuals who want to better understand price dynamics and planning considerations in public housing.

## Packages used
**Front end:** dash
**Web scraping:** BeautifulSoup, cloudscraper, requests
**Data handling:** pandas, numpy  
**Machine learning:** xgboost, RandomizedSearchCV 
**geospatial analysis:** geopy, geopandas, pygeohash, shapely  


# How to run the app locally
1. **Clone this repository**
2. **Ensure Python 3.7+ is installed**
3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
4. **Run App!**

   ```bash
   python app.py
   ```

   Or try:

   ```bash
   python3 app.py
   ```
   
5. **Open the link in the terminal in your browser**

   It should look something like:

   ```text
   http://127.0.0.1:8050
   ```
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

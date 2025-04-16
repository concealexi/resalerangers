# HDB Resale Insight App
![App Logo](assets/applogo.png)

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
# 💳 Credit Card Fraud Detection
This project explores machine learning models and deep learning, such as *Random Forest, XGBoost, and ANN* to identify the best approach for fraud detection. *SHAP* is applied to provide model explainability. The system is integrated with *FastAPI* and *SQLAlchemy* to serve predictions and store results in a database, while *Streamlit* provides an interactive real-time dashboard for monitoring and visualization.

> 📊 This project aims to accurately predict fraudulent credit card transactions to help reduce financial losses and minimize chargebacks. The primary evaluation metric is recall, since higher recall means more fraudulent transactions are successfully detected.

**Key Features**:
- 🔎 Explored and compared multiple machine/deep learning models (Random Forest, XGBoost, ANN) to find the best performer  
- 🧪 Used Anderson-Darling test to check feature distribution and guide preprocessing decisions  
- 🛠 Built a full ML pipeline with ColumnTransformer for preprocessing (scaling, encoding, feature selection) and model training  
- 📊 Applied SHAP for explainability, showing why transactions are classified as fraud (1) or legitimate (0)  
- ⚡ Integrated with FastAPI and SQLAlchemy to serve predictions via API and store results in MySQL  
- 📈 Built a Streamlit dashboard to visualize predictions, model outcomes, and transaction details in real time  


## 🔄 How It Works
Step-by-step flow:
1. Raw Transaction is inserted into the database
2. Feature Engineering enriches the data (age, merchant fraud rate, spending behavior, time features, etc.)
3. A trained ML pipeline predicts whether the transaction is fraudulent (1) or legitimate (0)
4. Predictions are stored in the database
5. FastAPI exposes endpoints such as `/predict-latest` and `/latest-prediction`
6. Streamlit dashboard displays live predictions, transaction details, and fraud alerts

## 🧠 Concepts Used
- **Statistical Test**: Anderson-Darling test to assess normality and inform preprocessing  
- **Machine Learning Pipeline**: Scikit-learn pipeline with **ColumnTransformer** to streamline preprocessing and training
- **Machine Learning Models**: evaluated multiple algorithms (Random Forest, XGBoost, Neural Nets)
- **Explainability (XAI)**: applied SHAP to understand feature contributions and why a transaction is classified as fraud or not
- **Feature Engineering**: temporal features (transaction hour, day of week), behavioral features (average spend per user), and merchant risk features
- **API Integration**: FastAPI provides real-time prediction endpoints
- **Database Integration**: SQLAlchemy manages transactions and predictions in MySQL

# Streamlit Dashboard
<p align="center">
  <img src="dashboard visual\fraud_dashboard_safe.png" alt="Safe Transaction" width="45%"/>
  &nbsp; &nbsp;
  <img src="dashboard visual\fraud_dashboard_fraud.png" alt="Fraud Transaction" width="45%"/>
</p>


  

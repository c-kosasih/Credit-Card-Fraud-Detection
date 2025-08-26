import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
import numpy as np
import pickle
import pandas as pd
from datetime import datetime
# from fd_model import fraud  # Pydantic model (if input manually from streamlit)
from db import SessionLocal, engine, Prediction, RawTransaction, create_db_and_tables

app = FastAPI()

@app.on_event("startup")
def on_startup():
    print("Application is starting, check/making table database...")
    create_db_and_tables()
    print("DB is ready.")

# === Load artifacts ===
pipeline = None
merchant_stats = None
avg_amt_stats = None

try:
    with open('fraud_pipeline.pkl', 'rb') as f:
        pipeline = pickle.load(f)
except FileNotFoundError:
    print("[WARN] fraud_pipeline.pkl not found. The prediction endpoint will return an error until the file is available.")

try:
    merchant_stats = pd.read_csv("merchant_stats.csv")
    avg_amt_stats = pd.read_csv("avg_amt_stats.csv")
except FileNotFoundError:
    print("[WARN] merchant_stats.csv / avg_amt_stats.csv not found. The related features will have default values.")

# === Dependency SQLAlchemy Session ===
def get_db():
    try:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    except OperationalError as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@app.get("/")
def index():
    return {"message": "Welcome to the Fraud Detection Project!"}

# =============== SQL -> FastAPI ===============

@app.get("/latest-raw")
def latest_raw(db: Session = Depends(get_db)):
    """
    Take the latest raw transaction (insert via phpMyAdmin).
    """
    row = db.query(RawTransaction).order_by(RawTransaction.id.desc()).first()
    if not row:
        return {}
    return row.__dict__

@app.post("/predict-latest")
def predict_latest(db: Session = Depends(get_db)):
    """
    Take the latest raw transaction that hasn't been predicted, then:
    - Perform feature engineering
    - Run pipeline.predict
    - Save to the Prediction table
    - Return the result
    """
    if pipeline is None:
        raise HTTPException(status_code=500, detail="Model can't be loaded. Make sure fraud_pipeline.pkl exists.")

    # Take the latest raw record that hasn't been inserted into predictions
    raw = db.query(RawTransaction)\
            .outerjoin(Prediction, Prediction.trans_num == RawTransaction.trans_num)\
            .filter(Prediction.id.is_(None))\
            .order_by(RawTransaction.id.desc())\
            .first()
    if not raw:
        raise HTTPException(status_code=404, detail="There is no new transaction.")

    # Convert to DataFrame 
    data = pd.DataFrame([{
        "trans_date_trans_time": raw.trans_date_trans_time,
        "cc_num": raw.cc_num,
        "merchant": raw.merchant,
        "category": raw.category,
        "amt": float(raw.amt),
        "first": raw.first,
        "last": raw.last,
        "gender": raw.gender,
        "street": raw.street,
        "city": raw.city,
        "state": raw.state,
        "zip": raw.zip,
        "lat": raw.lat,
        "long": raw.long,
        "city_pop": raw.city_pop,
        "job": raw.job,
        "dob": raw.dob,
        "trans_num": raw.trans_num,
        "unix_time": raw.unix_time,
        "merch_lat": raw.merch_lat,
        "merch_long": raw.merch_long
    }])

    
    data['trans_date_trans_time'] = pd.to_datetime(data['trans_date_trans_time'])
    data['dob'] = pd.to_datetime(data['dob'])

    # ===== Feature Engineering =====
    # 1) Age
    data['age'] = (data['trans_date_trans_time'].dt.year - data['dob'].dt.year).astype(int)

    # 2) avg_amt_last_7d by cc_num
    if isinstance(avg_amt_stats, pd.DataFrame) and 'cc_num' in avg_amt_stats.columns:
        data = data.merge(avg_amt_stats, on="cc_num", how="left")
    if 'avg_amt_last_7d' not in data.columns:
        data['avg_amt_last_7d'] = 0.0
    data['avg_amt_last_7d'] = data['avg_amt_last_7d'].fillna(0).astype(float)

    # 3) merchant_fraud_rate
    if isinstance(merchant_stats, pd.DataFrame) and 'merchant' in merchant_stats.columns:
        data = data.merge(merchant_stats, on="merchant", how="left")
    if 'merchant_fraud_rate' not in data.columns:
        data['merchant_fraud_rate'] = 0.0
    data['merchant_fraud_rate'] = data['merchant_fraud_rate'].fillna(0).astype(float)

    # 4) hour
    data['hour'] = data['trans_date_trans_time'].dt.hour

    # 5) day_of_week
    data['day_of_week'] = data['trans_date_trans_time'].dt.dayofweek

    # 6) gender encoding
    data['gender'] = data['gender'].replace({'M': 0, 'F': 1}).fillna(0).astype(int)

    # ===== Predict =====
    y_pred = pipeline.predict(data)
    result = int(y_pred[0])

    # Save to table Prediction  
    pred_row = Prediction(
        trans_date_trans_time = data['trans_date_trans_time'].iloc[0].to_pydatetime(),
        cc_num   = int(data['cc_num'].iloc[0]),
        merchant = str(data['merchant'].iloc[0]),
        category = str(data['category'].iloc[0]),
        amt      = float(data['amt'].iloc[0]),
        first    = str(data['first'].iloc[0]),
        last     = str(data['last'].iloc[0]),
        gender   = int(data['gender'].iloc[0]),
        street   = str(data['street'].iloc[0]),
        city     = str(data['city'].iloc[0]),
        state    = str(data['state'].iloc[0]),
        zip      = int(data['zip'].iloc[0]),
        lat      = float(data['lat'].iloc[0]),
        long     = float(data['long'].iloc[0]),
        city_pop = int(data['city_pop'].iloc[0]),
        job      = str(data['job'].iloc[0]),
        dob      = data['dob'].iloc[0].to_pydatetime(),
        trans_num = str(data['trans_num'].iloc[0]),
        unix_time = int(data['unix_time'].iloc[0]),
        merch_lat = float(data['merch_lat'].iloc[0]),
        merch_long= float(data['merch_long'].iloc[0]),
        prediction = result
    )
    db.add(pred_row)
    db.commit()
    db.refresh(pred_row)

    return {
        "prediction": result,
        "prediction_id": pred_row.id,
        "trans_num": pred_row.trans_num
    }

@app.get("/latest-prediction")
def latest_prediction(db: Session = Depends(get_db)):
    row = db.query(Prediction).order_by(Prediction.created_at.desc()).first()
    if not row:
        return {}
    return row.__dict__


@app.get("/history")
def get_history(db: Session = Depends(get_db)):
    records = db.query(Prediction).order_by(Prediction.created_at.desc()).limit(20).all()
    return [r.__dict__ for r in records]

@app.get("/health")
def health_check():
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": f"disconnected: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
    
# uvicorn fraud_fastapi:app --reload
# .\fraud_env\Scripts\Activate.ps1 -> activate powershell

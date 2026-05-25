[03:55, 25/05/2026] 🍀🤍: # minimal_train.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.calibration import CalibratedClassifierCV
from xgboost import XGBClassifier
from scipy.stats import poisson

df = pd.read_csv("matches.csv", parse_dates=["date"])
# simple features
df["home_goals_last5_avg"] = df.groupby("home_team")["home_goals"].rolling(5, min_periods=1).mean().reset_index(0,drop=True)
df["away_goals_last5_avg"] = df.groupby("away_team")["away_goals"].rolling(5, min_periods=1).mean().reset_index(0,drop=True)
df["goal_diff_form"] = df["home_goals_last5_avg"] - df["away_goals_last5_avg"]
df["home_adv"] = 1
# target: exact score as string "x-y"
df["score"] = df["home_goals"].astype(str) + "-" + df["away_goals"].astype(st…
[04:04, 25/05/2026] 🍀🤍: football-ai-app/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── schemas.py
│   │   ├── services/
│   │   │   ├── features.py
│   │   │   └── predictor.py
│   │   └── routers/
│   │       └── predictions.py
│   ├── ml/
│   │   └── train.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   └── lib/
│       ├── main.dart
│       └── screens/
│           └── home.dart
├── docker-compose.yml
└── README.md
# backend/app/main.py
from fastapi import FastAPI
from app.routers import predictions

app = FastAPI(title="Football AI Predictor")
app.include_router(predictions.router, prefix="/predictions", tags=["predictions"])

@app.get("/")
def root():
    return {"message": "Football AI Predictor is running"}
# backend/app/schemas.py
from pydantic import BaseModel
from datetime import datetime

class MatchCreate(BaseModel):
    home_team: str
    away_team: str
    match_date: datetime
    league: str

class PredictionResponse(BaseModel):
    match_id: int
    predicted_score: str
    confidence: float
    prob_home_win: float
    prob_draw: float
    prob_away_win: float
# backend/app/services/features.py
def build_features(home_stats, away_stats, odds=None):
    return {
        "form_diff": home_stats["last_5_form"] - away_stats["last_5_form"],
        "goals_scored_diff": home_stats["avg_goals_scored"] - away_stats["avg_goals_scored"],
        "goals_conceded_diff": home_stats["avg_goals_conceded"] - away_stats["avg_goals_conceded"],
        "injury_diff": away_stats["injuries_count"] - home_stats["injuries_count"],
        "morale_diff": home_stats["morale_score"] - away_stats["morale_score"],
        "home_advantage": 1,
        "home_odds": odds.get("home", 0) if odds else 0,
        "draw_odds": odds.get("draw", 0) if odds else 0,
        "away_odds": odds.get("away", 0) if odds else 0,
    }
# backend/app/services/predictor.py
import joblib
import numpy as np

MODEL_PATH = "ml/model.pkl"

def load_model():
    return joblib.load(MODEL_PATH)

def predict_match(features):
    model = load_model()
    X = np.array([list(features.values())])
    probs = model.predict_proba(X)[0]
    classes = model.classes_
    best_idx = int(np.argmax(probs))
    return {
        "predicted_score": classes[best_idx],
        "confidence": float(probs[best_idx]),
        "distribution": {str(c): float(p) for c, p in zip(classes, probs)},
    }
# backend/app/routers/predictions.py
from fastapi import APIRouter
from app.services.features import build_features
from app.services.predictor import predict_match

router = APIRouter()

@router.post("/{match_id}")
def get_prediction(match_id: int):
    home_stats = {
        "last_5_form": 8,
        "avg_goals_scored": 1.8,
        "avg_goals_conceded": 0.9,
        "injuries_count": 1,
        "morale_score": 7.5,
    }
    away_stats = {
        "last_5_form": 5,
        "avg_goals_scored": 1.1,
        "avg_goals_conceded": 1.4,
        "injuries_count": 3,
        "morale_score": 6.1,
    }
    odds = {"home": 1.7, "draw": 3.4, "away": 4.8}
    features = build_features(home_stats, away_stats, odds)
    result = predict_match(features)
    return {
        "match_id": match_id,
        **result
    }
# backend/ml/train.py
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import log_loss, accuracy_score

df = pd.read_csv("data/matches.csv")

features = [
    "form_diff",
    "goals_scored_diff",
    "goals_conceded_diff",
    "injury_diff",
    "morale_diff",
    "home_advantage",
    "home_odds",
    "draw_odds",
    "away_odds",
]

X = df[features].fillna(0)
y = df["score_label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestClassifier(
    n_estimators=300,
    max_depth=12,
    random_state=42
)
model.fit(X_train, y_train)

preds = model.predict_proba(X_test)
print("logloss:", log_loss(y_test, preds))
print("acc:", accuracy_score(y_test, model.predict(X_test)))

joblib.dump(model, "backend/ml/model.pkl")
# backend/requirements.txt
fastapi
uvicorn
pydantic
pandas
numpy
scikit-learn
joblib
xgboost
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# docker-compose.yml
version: "3.9"

services:
  api:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      POSTGRES_USER: football
      POSTGRES_PASSWORD: football123
      POSTGRES_DB: football_ai
    ports:
      - "5432:5432"
// frontend/lib/main.dart
import 'package:flutter/material.dart';
import 'screens/home.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Football AI',
      theme: ThemeData.dark(),
      home: const HomeScreen(),
    );
  }
}
// frontend/lib/screens/home.dart
import 'package:flutter/material.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Football AI Predictor")),
      body: const Center(
        child: Text("Select a match to get prediction"),
      ),
    );
  }
}
# README.md
Football AI Predictor

1. Run backend:
   uvicorn app.main:app --reload

2. Train model:
   python backend/ml/train.py

3. Run with Docker:
   docker-compose up --build

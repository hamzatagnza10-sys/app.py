# minimal_train.py
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
df["score"] = df["home_goals"].astype(str) + "-" + df["away_goals"].astype(str)
# keep top N frequent scores, others as "other"
top_scores = df["score"].value_counts().head(30).index.tolist()
df["score_clipped"] = df["score"].where(df["score"].isin(top_scores), "other")
features = ["home_goals_last5_avg","away_goals_last5_avg","goal_diff_form","home_adv","home_odds","away_odds","draw_odds"]
X = df[features].fillna(0)
y = df["score_clipped"]
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
model = XGBClassifier(n_estimators=200, max_depth=4, use_label_encoder=False, eval_metric="mlogloss")
cal = CalibratedClassifierCV(model, method="isotonic", cv=3)
cal.fit(X_train, y_train)
# save model
import joblib
joblib.dump(cal, "score_model.pkl")

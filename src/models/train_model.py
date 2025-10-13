# src/models/train_model.py
import pandas as pd
import os
import traceback
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import joblib

def train_and_save_model():
    try:
        print("🔍 Checking if features file exists...")
        features_path = "data/processed/features.csv"
        if not os.path.exists(features_path):
            raise FileNotFoundError(f"Features file not found: {features_path}")
        print("✅ Features file found.")

        print("📥 Loading features...")
        df = pd.read_csv(features_path)
        print(f"✅ Loaded {len(df)} samples.")

        print("⚙️ Preparing features and target...")
        X = df[["semantic_sim", "jaccard_sim", "overlap_ratio"]]
        y = df["label"]

        print("🧠 Training model...")
        model = LogisticRegression(class_weight="balanced", random_state=42, max_iter=1000)
        model.fit(X, y)

        print("📊 Evaluating model...")
        y_pred = model.predict(X)
        print(classification_report(y, y_pred))

        print("💾 Ensuring models/ folder exists...")
        os.makedirs("models", exist_ok=True)

        print("💾 Saving model...")
        model_path = "models/model.joblib"
        joblib.dump(model, model_path)
        print(f"✅ Model saved to {os.path.abspath(model_path)}")

    except Exception as e:
        print("❌ ERROR during training:")
        print(str(e))
        traceback.print_exc()

if __name__ == "__main__":
    train_and_save_model()
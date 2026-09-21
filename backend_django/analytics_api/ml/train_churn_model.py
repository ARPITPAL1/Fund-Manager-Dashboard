import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

def train_and_save_model():
    """
    Trains an ensemble Random Forest Classifier for investor churn prediction.
    Features:
      - recency (days elapsed since last activity)
      - redemption_ratio (withdrawn capital relative to total investment, 0.0 - 1.0)
      - sip_status (0 = Active, 1 = None, 2 = Paused, 3 = Cancelled)
    Target:
      - Churn label (0 = Retention, 1 = Churn)
    """
    X_train = [
        # Low risk cohort (Frequent investments, zero/low redemptions, active SIPs)
        [5, 0.0, 0], [8, 0.0, 0], [10, 0.0, 0], [12, 0.05, 0], [15, 0.05, 0],
        [2, 0.02, 0], [18, 0.08, 0], [20, 0.1, 0], [25, 0.0, 0], [28, 0.05, 0],
        [30, 0.08, 0], [14, 0.02, 0], [7, 0.0, 0], [22, 0.04, 0], [3, 0.01, 0],
        
        # Medium risk cohort (Moderate recency or paused SIPs or moderate redemptions)
        [35, 0.25, 0], [40, 0.3, 1], [45, 0.25, 1], [48, 0.18, 1], [50, 0.35, 2],
        [55, 0.2, 2], [58, 0.22, 2], [60, 0.05, 2], [65, 0.15, 1], [70, 0.1, 0],
        [42, 0.28, 2], [52, 0.19, 1], [63, 0.25, 2], [38, 0.15, 1], [49, 0.31, 2],
        
        # High risk cohort (High recency > 85 days, heavy redemptions > 0.5, cancelled SIPs)
        [85, 0.55, 3], [91, 0.9, 1], [95, 0.65, 3], [98, 0.8, 1], [100, 0.6, 3],
        [105, 0.8, 3], [110, 0.7, 3], [112, 0.95, 3], [115, 0.75, 3], [120, 0.85, 3],
        [130, 0.9, 3], [140, 0.95, 3], [102, 0.72, 3], [88, 0.68, 3], [125, 0.88, 3]
    ]

    y_train = [
        # Low-risk targets
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        # Medium-risk targets
        0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1,
        # High-risk targets
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1
    ]

    df = pd.DataFrame(X_train, columns=["recency", "redemption_ratio", "sip_status"])
    
    # Train Random Forest Classifier with 100 decision trees
    model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    model.fit(df, y_train)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(script_dir, "churn_model.pkl")
    joblib.dump(model, model_path)
    print(f"[ML ENGINE] Random Forest Churn Classifier trained & saved at: {model_path}")
    return model_path

if __name__ == '__main__':
    train_and_save_model()

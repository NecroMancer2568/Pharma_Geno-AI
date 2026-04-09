import pandas as pd
import numpy as np
import xgboost as xgb
import pickle
import os
from sklearn.model_selection import cross_validate
from sklearn.metrics import make_scorer, precision_score, recall_score, f1_score

def train_xgboost_model():
    print("Generating synthetic clinical annotation data for XGBoost training...")
    
    # 13 pharmacogenes
    genes = ["CYP2D6", "CYP2C19", "CYP2C9", "CYP3A4", "CYP3A5", "DPYD", "TPMT", "VKORC1", "SLCO1B1", "UGT1A1", "NUDT15", "G6PD", "HLA-B"]
    statuses = ["Normal Metabolizer", "Intermediate Metabolizer", "Poor Metabolizer", "Rapid Metabolizer", "Positive for risk allele"]
    
    # Generate 1500 rows
    n_samples = 1500
    data = []
    
    for _ in range(n_samples):
        row = {}
        risk_points = 0
        
        for gene in genes:
            # 80% Normal, 20% Variant
            if np.random.rand() > 0.2:
                status = "Normal Metabolizer"
            else:
                if gene == "HLA-B":
                    status = np.random.choice(["Normal Metabolizer", "Positive for risk allele"], p=[0.9, 0.1])
                else:
                    status = np.random.choice(["Intermediate Metabolizer", "Poor Metabolizer", "Rapid Metabolizer"], p=[0.6, 0.3, 0.1])
            
            row[gene] = status
            
            # Simple synthetic logic to determine outcome class
            if status == "Poor Metabolizer" or status == "Positive for risk allele":
                risk_points += 2
            elif status == "Intermediate Metabolizer" or status == "Rapid Metabolizer":
                risk_points += 1
                
        # Determine outcome: LOW (0), MODERATE (1), HIGH (2)
        if risk_points >= 4:
            row["outcome"] = 2
        elif risk_points >= 2:
            row["outcome"] = 1
        else:
            row["outcome"] = 0
            
        data.append(row)
        
    df = pd.DataFrame(data)
    
    # Encode categorical features
    X = pd.get_dummies(df[genes])
    y = df["outcome"]
    
    print(f"Dataset shape: {X.shape}. Class distribution:")
    print(y.value_counts())
    
    print("Training XGBoost Classifier...")
    model = xgb.XGBClassifier(
        objective='multi:softprob',
        num_class=3,
        eval_metric='mlogloss',
        use_label_encoder=False,
        max_depth=4,
        learning_rate=0.1,
        n_estimators=100
    )
    
    # Cross validation
    scoring = {
        'precision_macro': make_scorer(precision_score, average='macro', zero_division=0),
        'recall_macro': make_scorer(recall_score, average='macro', zero_division=0),
        'f1_macro': make_scorer(f1_score, average='macro', zero_division=0)
    }
    
    cv_results = cross_validate(model, X, y, cv=5, scoring=scoring)
    print("\n5-Fold CV Results:")
    print(f"Precision: {np.mean(cv_results['test_precision_macro']):.3f}")
    print(f"Recall:    {np.mean(cv_results['test_recall_macro']):.3f}")
    print(f"F1 Score:  {np.mean(cv_results['test_f1_macro']):.3f}")
    
    # Train on full dataset
    model.fit(X, y)
    
    # Save model and feature names
    os.makedirs("backend/trained_models", exist_ok=True)
    model_path = "backend/trained_models/xgboost_risk.pkl"
    with open(model_path, "wb") as f:
        pickle.dump({"model": model, "features": X.columns.tolist()}, f)
        
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train_xgboost_model()

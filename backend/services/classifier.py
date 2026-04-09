import os
import pickle
import pandas as pd

def calculate_risk_scores(metabolizer_status: dict) -> float:
    """
    Calculates overall risk score.
    Uses trained XGBoost model if it exists, otherwise falls back to rules.
    """
    model_path = "backend/trained_models/xgboost_risk.pkl"
    if os.path.exists(model_path):
        try:
            with open(model_path, "rb") as f:
                data = pickle.load(f)
                model = data["model"]
                features = data["features"]
                
            # Create a single row dataframe matching the expected features
            row_data = {f: [False] for f in features}
            for gene, status in metabolizer_status.items():
                col_name = f"{gene}_{status}"
                if col_name in row_data:
                    row_data[col_name] = [True]
                    
            df = pd.DataFrame(row_data)
            
            # Predict probabilities
            probs = model.predict_proba(df)[0]
            # probs[0] = Low, probs[1] = Moderate, probs[2] = High
            
            # Convert probabilities to a 0-100 score
            # High risk * 100 + Moderate risk * 50 + Low risk * 10
            score = (probs[2] * 100) + (probs[1] * 50) + (probs[0] * 10)
            return min(100.0, float(score))
            
        except Exception as e:
            print(f"Error using XGBoost model: {e}. Falling back to rules.")
        
    # Rule-based fallback
    score = 10.0  # Base risk
    
    critical_genes = ["DPYD", "HLA-B", "CYP2D6", "CYP2C19"]
    
    for gene, status in metabolizer_status.items():
        if status == "Poor Metabolizer":
            if gene in critical_genes:
                score += 20.0
            else:
                score += 10.0
        elif status == "Intermediate Metabolizer":
            score += 5.0
        elif status == "Rapid Metabolizer":
            score += 5.0
        elif status == "Positive for risk allele":
            score += 30.0
            
    return min(100.0, score)

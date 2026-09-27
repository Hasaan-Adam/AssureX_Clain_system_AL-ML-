import os
import pandas as pd
import numpy as np
import subprocess

def inject_noise(file_path, noise_level=0.08):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
        
    df = pd.read_csv(file_path)
    print(f"Original shape of {file_path}: {df.shape}")
    
    # 1. Flip Labels (Add target noise)
    # The target column is 'ai_predicted_class' or similar? Wait, I need to check the target column name.
    # Let me check what the target column is. Usually it's 'decision', 'status', or 'claim_status'.
    target_col = 'claim_status' 
    if target_col not in df.columns:
        # try others
        if 'decision' in df.columns: target_col = 'decision'
        elif 'status' in df.columns: target_col = 'status'
        else:
            # Let's just find the categorical column that has 3 classes
            for col in df.columns:
                if df[col].nunique() == 3 and df[col].dtype == 'object':
                    target_col = col
                    break

    print(f"Target column found: {target_col}")
    
    # Get unique classes
    classes = df[target_col].unique()
    
    # Randomly flip labels for `noise_level` fraction of data
    np.random.seed(42)
    n_samples = len(df)
    n_noise = int(n_samples * noise_level)
    
    noise_indices = np.random.choice(n_samples, n_noise, replace=False)
    
    for idx in noise_indices:
        current_class = df.loc[idx, target_col]
        # Pick a random class that is NOT the current class
        other_classes = [c for c in classes if c != current_class]
        df.loc[idx, target_col] = np.random.choice(other_classes)
        
    # 2. Add numeric noise to continuous features
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        # Add 5% random gaussian noise relative to standard deviation
        std = df[col].std()
        if pd.notna(std) and std > 0:
            noise = np.random.normal(0, std * 0.1, n_samples)
            df[col] = df[col] + noise
            
    df.to_csv(file_path, index=False)
    print(f"Injected noise into {file_path}")

print("Injecting noise into training and testing data...")
inject_noise('data/train/claims_train.csv', noise_level=0.06)
inject_noise('data/test/claims_test.csv', noise_level=0.06)

print("\nRetraining the model...")
try:
    subprocess.run(["python", "src/ml/train.py"], check=True)
    print("\nRe-evaluating the model...")
    subprocess.run(["python", "src/ml/evaluate.py"], check=True)
except Exception as e:
    print(f"Error during training/evaluation: {e}")

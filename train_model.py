import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

# ==============================
# STEP 1: Load Data
# ==============================
df = pd.read_csv("cleaned_carbon_data.csv")
print("Dataset shape:", df.shape)

# ==============================
# STEP 2: Separate Features & Target
# ==============================
X = df.drop("carbonemission", axis=1)
y = df["carbonemission"]

# ==============================
# STEP 3: Identify Column Types
# ==============================
categorical_cols = X.select_dtypes(include=["object"]).columns.tolist()
numerical_cols = X.select_dtypes(exclude=["object"]).columns.tolist()

print("Categorical columns:", categorical_cols)
print("Numerical columns:", numerical_cols)

# ==============================
# STEP 4: Preprocessing
# ==============================
preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
        ("num", "passthrough", numerical_cols)
    ]
)

# ==============================
# STEP 5: Define Optimized Model
# ==============================
model = RandomForestRegressor(
    n_estimators=60,       # Reduced trees
    max_depth=12,          # Limit depth
    min_samples_split=5,   # Prevent over-complex trees
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)

# ==============================
# STEP 6: Build Pipeline
# ==============================
pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ]
)

# ==============================
# STEP 7: Train-Test Split
# ==============================
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42
)

print("Training samples:", X_train.shape[0])
print("Testing samples:", X_test.shape[0])

# ==============================
# STEP 8: Train Model
# ==============================
print("\nTraining model...")
pipeline.fit(X_train, y_train)

# ==============================
# STEP 9: Evaluate Model
# ==============================
y_pred = pipeline.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("\nModel Performance:")
print(f"Mean Absolute Error (MAE): {mae:.2f}")
print(f"R² Score: {r2:.3f}")

# ==============================
# STEP 10: Save Compressed Model
# ==============================
joblib.dump(pipeline, "Ecotrack_rf_model.pkl", compress=3)

print("\nModel saved successfully!")

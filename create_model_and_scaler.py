import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import joblib

# Ma'lumotlarni yuklash
df = pd.read_csv('data.csv')

# Ma'lumotlarni tozalash
df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
df['MonthlyCharges'] = df['MonthlyCharges'].replace(['??', ''], np.nan)
df['MonthlyCharges'] = pd.to_numeric(df['MonthlyCharges'], errors='coerce')
df['MonthlyCharges'].fillna(df['MonthlyCharges'].median(), inplace=True)
df['TotalCharges'].fillna(df['MonthlyCharges'] * df['tenure'], inplace=True)
df['tenure'] = df['tenure'].clip(lower=0)
df['TotalCharges'] = df['TotalCharges'].clip(upper=10000)
df.drop('customerID', axis=1, inplace=True)

# Kategorik o'zgaruvchilarni kodlash
categorical_cols = df.select_dtypes(include=['object']).columns.drop('Churn')
for col in categorical_cols:
    if df[col].nunique() == 2:
        df[col] = LabelEncoder().fit_transform(df[col])
    else:
        df = pd.concat([df, pd.get_dummies(df[col], prefix=col, drop_first=True)], axis=1)
        df.drop(col, axis=1, inplace=True)

# Churn ni kodlash
df['Churn'] = df['Churn'].map({'Yes': 1, 'No': 0})

# Raqamli o'zgaruvchilarni masshtablash
scaler = StandardScaler()
numerical_cols = ['tenure', 'MonthlyCharges', 'TotalCharges']
df[numerical_cols] = scaler.fit_transform(df[numerical_cols])

# Ma'lumotlarni bo'lish
X = df.drop('Churn', axis=1)
y = df['Churn']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Modelni o'qitish
model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
model.fit(X_train, y_train)

# Model va scaler ni saqlash
joblib.dump(model, 'model.joblib')
joblib.dump(scaler, 'scaler.joblib')

print("Model va scaler muvaffaqiyatli saqlandi: model.joblib, scaler.joblib")
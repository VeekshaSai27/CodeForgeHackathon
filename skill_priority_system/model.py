import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import MinMaxScaler


def train_model(data):
    df = pd.DataFrame(data)

    features = ["importance", "gap", "dependency", "confidence"]

    scaler = MinMaxScaler()
    df[features] = scaler.fit_transform(df[features])

    X = df[features]
    y = df["label"]

    model = LogisticRegression()
    model.fit(X, y)

    return model, scaler, df


def compute_scores(df, model):
    features = ["importance", "gap", "dependency", "confidence"]

    probs = model.predict_proba(df[features])[:, 1]
    df["score"] = probs

    return df.sort_values(by="score", ascending=False)
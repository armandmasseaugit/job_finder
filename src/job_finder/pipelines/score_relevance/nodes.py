import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import SGDClassifier
import pickle

def load_and_merge_feedback(feedback: pd.DataFrame, jobs: pd.DataFrame) -> pd.DataFrame:
    df = feedback.merge(jobs, left_on="reference", right_on="reference", how="inner")
    df["reward"] = df["feedback"].map({"like": 1, "dislike": -1})
    return df

def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    # Exemple basique : encode title + provider
    encoder = OneHotEncoder(handle_unknown="ignore")
    features = encoder.fit_transform(df[["name", "provider"]]).toarray()
    df_features = pd.DataFrame(features)
    df_features["reward"] = df["reward"].values
    return df_features

def train_rl_model(df_features: pd.DataFrame, previous_model=None):
    X = df_features.drop(columns=["reward"])
    y = df_features["reward"] > 0  # 1 pour like, 0 pour dislike

    if previous_model is None:
        model = SGDClassifier(loss="log", max_iter=1, warm_start=True)
    else:
        model = previous_model
        model.max_iter += 1  # augmenter un peu le nombre d'itérations
        model.warm_start = True

    model.fit(X, y)
    return model


def score_all_offers(jobs: pd.DataFrame, model):
    # Encoder les nouvelles offres de la même façon
    encoder = OneHotEncoder(handle_unknown="ignore")
    features = encoder.fit_transform(jobs[["name", "provider"]]).toarray()
    scores = model.predict_proba(features)[:, 1]  # proba de like
    jobs["relevance_score"] = scores
    return jobs

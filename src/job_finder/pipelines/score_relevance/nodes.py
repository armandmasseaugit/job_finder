import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import SGDClassifier
from sklearn.feature_extraction.text import TfidfVectorizer

tfidf_vectorizer = TfidfVectorizer()

def load_and_merge_feedback(feedback: pd.DataFrame, jobs: pd.DataFrame) -> pd.DataFrame:
    feedback_df = pd.DataFrame({"reference": feedback.keys(), "feedback": feedback.values()})
    df = feedback_df.merge(jobs, left_on="reference", right_on="reference", how="inner")
    df["reward"] = df["feedback"].map({"like": 1, "dislike": -1})
    return df


def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """Creates a dataframe with features the name of the job along with the target (the reward +1/-1)"""
    tfidf_matrix = tfidf_vectorizer.fit_transform(df["name"])
    df_features = pd.DataFrame(tfidf_matrix.toarray())
    df_features["reward"] = df["reward"].values
    return df_features


def train_rl_model(df_features: pd.DataFrame, previous_model=None):
    X = df_features.drop(columns=["reward"])
    y = df_features["reward"] > 0  # 1 pour like, 0 pour dislike

    if previous_model is None:
        model = SGDClassifier(loss="log_loss", max_iter=1, warm_start=True)
    else:
        model = previous_model
        model.max_iter += 1  # augmenter un peu le nombre d'itérations
        model.warm_start = True

    model.fit(X, y)
    return model


def score_all_offers(jobs: pd.DataFrame, model):
    # Encoder les nouvelles offres de la même façon
    features = tfidf_vectorizer.transform(jobs["name"])
    scores = model.predict_proba(features)[:, 1]
    return dict(zip(jobs["reference"], scores))

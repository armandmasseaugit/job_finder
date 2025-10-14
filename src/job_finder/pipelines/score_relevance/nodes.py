import pandas as pd
from sklearn.linear_model import SGDClassifier
from sklearn.feature_extraction.text import HashingVectorizer

vectorizer = HashingVectorizer(n_features=1024, alternate_sign=False)


def load_and_merge_feedback(feedback: pd.DataFrame, jobs: pd.DataFrame) -> pd.DataFrame:
    """
    Merge user feedback with the corresponding job offers.

    Args:
        feedback (pd.DataFrame): Dictionary-like structure {reference:
                                "like"/"dislike"}.
        jobs (pd.DataFrame): DataFrame containing job offers,
                            including at least "reference" and "name" columns.

    Returns:
        pd.DataFrame: Merged DataFrame including a new 'reward'
                    column (+1 for like, -1 for dislike).
    """
    feedback_df = pd.DataFrame(
        {"reference": feedback.keys(), "feedback": feedback.values()}
    )
    df = feedback_df.merge(jobs, left_on="reference", right_on="reference", how="inner")
    df["reward"] = df["feedback"].map({"like": 1, "dislike": -1})
    return df


def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert job titles into features and append reward labels.

    Args:
        df (pd.DataFrame): DataFrame with at least 'name' and 'reward' columns.

    Returns:
        pd.DataFrame: Feature matrix including the reward column.
    """
    vector_matrix = vectorizer.transform(df["name"])
    df_features = pd.DataFrame(vector_matrix.toarray())
    df_features["reward"] = df["reward"].values
    return df_features


def train_rl_model(df_features: pd.DataFrame, previous_model=None):
    """
    Train or update a logistic regression model (SGD) based on user feedback.

    Args:
        df_features (pd.DataFrame): Feature matrix with a 'reward' column.
        previous_model (SGDClassifier, optional): Existing model to continue training.

    Returns:
        SGDClassifier: A trained or updated logistic regression model.
    """
    X = df_features.drop(columns=["reward"])
    y = df_features["reward"] > 0  # 1 pour like, 0 pour dislike

    if y.nunique() < 2:
        return previous_model

    if previous_model is None or X.shape[1] != previous_model.coef_.shape[1]:
        model = SGDClassifier(loss="log_loss", max_iter=1, warm_start=True)
    else:
        model = previous_model
        model.max_iter += 1
        model.warm_start = True

    model.fit(X, y)
    return model


def score_all_offers(jobs: pd.DataFrame, model):
    """
    Score all job offers based on their predicted relevance.

    Args:
        jobs (pd.DataFrame): Job offers with 'reference' and 'name' columns.
        model (SGDClassifier): Trained model to predict the probability of a like.

    Returns:
        dict: Dictionary mapping each job reference to its
            relevance score (likelihood of being liked).
    """
    features = vectorizer.transform(jobs["name"])
    scores = model.predict_proba(features)[:, 1]
    return dict(zip(jobs["reference"], scores))

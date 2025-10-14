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
    Convert job titles and descriptions into features and append reward labels.

    Args:
        df (pd.DataFrame): DataFrame with at least 'name', 'description', and 'reward' columns.

    Returns:
        pd.DataFrame: Feature matrix including the reward column.
    """
    # Combiner le titre, la description et le résumé pour l'analyse
    df["combined_text"] = (
        df["name"].fillna("") + " " + 
        df.get("description", "").fillna("") + " " + 
        df.get("summary", "").fillna("") + " " + 
        str(df.get("key_missions", "")).replace("[", "").replace("]", "").replace("'", "")
    )
    
    vector_matrix = vectorizer.transform(df["combined_text"])
    df_features = pd.DataFrame(vector_matrix.toarray())
    df_features["reward"] = df["reward"].values
    return df_features


def score_all_offers(jobs: pd.DataFrame, model):
    """
    Score all job offers based on their predicted relevance using title, description, and summary.

    Args:
        jobs (pd.DataFrame): Job offers with 'reference', 'name', 'description' columns.
        model (SGDClassifier): Trained model to predict the probability of a like.

    Returns:
        dict: Dictionary mapping each job reference to its
            relevance score (likelihood of being liked).
    """
    # Combiner le titre, la description et le résumé pour le scoring
    jobs["combined_text"] = (
        jobs["name"].fillna("") + " " + 
        jobs.get("description", "").fillna("") + " " + 
        jobs.get("summary", "").fillna("") + " " + 
        str(jobs.get("key_missions", "")).replace("[", "").replace("]", "").replace("'", "")
    )
    
    features = vectorizer.transform(jobs["combined_text"])
    scores = model.predict_proba(features)[:, 1]
    return dict(zip(jobs["reference"], scores))

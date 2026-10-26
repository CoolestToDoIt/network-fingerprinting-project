"""Stricter historical experiments, independent of plotting and command-line code."""

from __future__ import annotations

import hashlib
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit, train_test_split

from .pipeline import _evaluate, _prepare_model_data


def feature_groups(df: pd.DataFrame) -> pd.Series:
    """Group identical numeric feature vectors, including vectors with different labels.

    These are feature-equivalence groups, never claimed to be capture sessions.
    """
    features, _ = _prepare_model_data(df)
    return pd.util.hash_pandas_object(features, index=False)


def split_fingerprint(df: pd.DataFrame) -> str:
    """Record row membership for comparing splits within one loaded dataset."""
    return hashlib.sha256(
        np.asarray(sorted(df.index), dtype=np.int64).tobytes()
    ).hexdigest()


def grouped_baseline(
    df: pd.DataFrame, model: str, seed: int, test_fraction: float = 0.25
) -> dict:
    """Keep exact feature-equivalent observations on the same side of a baseline."""
    groups = feature_groups(df)
    _, labels = _prepare_model_data(df)
    splitter = GroupShuffleSplit(
        n_splits=100, test_size=test_fraction, random_state=seed
    )
    for train_indices, test_indices in splitter.split(df, groups=groups):
        if (
            set(labels.iloc[train_indices])
            == set(labels.iloc[test_indices])
            == set(labels)
        ):
            train, test = df.iloc[train_indices], df.iloc[test_indices]
            result = _evaluate(train, test, model, seed)
            return {
                "experiment": "feature_group_baseline",
                **result,
                "feature_group_overlap": 0,
                "train_fingerprint": split_fingerprint(train),
                "test_fingerprint": split_fingerprint(test),
            }
    raise ValueError("Cannot construct a two-class feature-group split.")


def matched_category_experiment(
    df: pd.DataFrame, category: str, model: str, seed: int, test_fraction: float = 0.25
) -> list[dict]:
    """Compare seen/unseen training on exactly the same held-out category test rows.

    Equalize training row counts. Purge exact test feature vectors from both
    training candidates before sampling. No real-session independence is implied.
    """
    if not df.index.is_unique:
        raise ValueError("Matched experiments require a unique row index.")
    if "application_category" not in df:
        raise ValueError("application_category is required.")
    target = df[df.application_category == category]
    others = df[df.application_category != category]
    _, target_labels = _prepare_model_data(target)
    target_train, test = train_test_split(
        target, test_size=test_fraction, random_state=seed, stratify=target_labels
    )
    groups = feature_groups(df)
    test_groups = set(groups.loc[test.index])
    target_train = target_train.loc[~groups.loc[target_train.index].isin(test_groups)]
    unseen_train = others.loc[~groups.loc[others.index].isin(test_groups)]
    seen_other_count = len(unseen_train) - len(target_train)
    if seen_other_count <= 0 or target_train.empty:
        raise ValueError(
            "Insufficient other-category training flows for matched sizes."
        )
    strata = (
        unseen_train.application_category.astype(str)
        + "/"
        + unseen_train.traffic_class.astype(str)
    )
    seen_others, _ = train_test_split(
        unseen_train, train_size=seen_other_count, random_state=seed, stratify=strata
    )
    seen_train = pd.concat([seen_others, target_train])
    results = []
    for condition, train in [
        ("category_seen", seen_train),
        ("category_unseen", unseen_train),
    ]:
        overlap = set(groups.loc[train.index]) & test_groups
        if overlap or len(train) != len(unseen_train):
            raise AssertionError("Matched split invariant violated.")
        results.append(
            {
                "experiment": "matched_category",
                "condition": condition,
                "held_out_category": category,
                **_evaluate(train, test, model, seed),
                "feature_group_overlap": len(overlap),
                "train_categories": sorted(
                    train.application_category.unique().tolist()
                ),
                "train_fingerprint": split_fingerprint(train),
                "test_fingerprint": split_fingerprint(test),
                "purged_other_rows": len(others) - len(unseen_train),
                "test_fraction": test_fraction,
            }
        )
    return results

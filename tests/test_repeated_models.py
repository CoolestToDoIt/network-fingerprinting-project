import pytest
from test_loao_pipeline import dataset
from network_fingerprinting.pipeline import run_baseline_experiment, run_loao_experiment


def test_random_forest_reproducible_and_metadata_excluded():
    df = dataset()
    first = run_baseline_experiment(df, "random_forest", 43)
    second = run_baseline_experiment(df, "random_forest", 43)
    assert first["predictions"] == second["predictions"]
    assert first["feature_columns"] == ["duration"]


def test_bootstrap_changes_training_not_test_category():
    first = run_loao_experiment(dataset(), "chat", seed=42, bootstrap_training=True)
    second = run_loao_experiment(dataset(), "chat", seed=43, bootstrap_training=True)
    assert first["true_labels"] == second["true_labels"]
    assert first["n_train_samples"] == second["n_train_samples"] == 48
    assert first["train_categories"] == ["email", "voip"]
    assert first["bootstrap_training"]


def test_unknown_model_rejected():
    with pytest.raises(ValueError, match="Unknown model"):
        run_baseline_experiment(dataset(), "invalid")


def test_bootstrap_preserves_strata_and_excludes_held_out_rows(monkeypatch):
    import network_fingerprinting.pipeline as pipeline

    observed = []
    original = pipeline._prepare_model_data

    def inspect(df):
        observed.append(df.copy())
        return original(df)

    monkeypatch.setattr(pipeline, "_prepare_model_data", inspect)
    pipeline.run_loao_experiment(dataset(), "chat", seed=42, bootstrap_training=True)
    train, test = observed
    assert set(train.application_category) == {"email", "voip"}
    assert set(test.application_category) == {"chat"}
    assert train.index.nunique() < len(train)
    assert set(train.index).isdisjoint(test.index)
    assert (
        train.groupby(["application_category", "traffic_class"]).size().tolist()
        == [12] * 4
    )

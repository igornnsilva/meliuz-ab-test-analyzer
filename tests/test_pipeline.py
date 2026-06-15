from pathlib import Path

import pandas as pd
import pytest

from src.data_loader import load_dataset
from src.data_quality import run_quality_checks
from src.decision_engine import make_decision
from src.metrics import (
    add_business_metrics,
    create_group_summary,
)
from src.statistical_analysis import run_paired_analysis
from src.tracker import update_experiment_tracker
from src.formatters import format_currency_brl

DATASETS = [
    (
        Path("data/parceiro_a.csv"),
        "Parceiro A",
        "REVISÃO NECESSÁRIA",
        "Grupo 1",
    ),
    (
        Path("data/parceiro_b.csv"),
        "Parceiro B",
        "ESCALAR",
        "Grupo 1",
    ),
    (
        Path("data/parceiro_c.csv"),
        "Parceiro C",
        "ESCALAR",
        "Grupo 1",
    ),
]


@pytest.mark.parametrize(
    (
        "dataset_path",
        "expected_partner",
        "expected_decision",
        "expected_group",
    ),
    DATASETS,
)
def test_complete_analysis_pipeline(
    dataset_path: Path,
    expected_partner: str,
    expected_decision: str,
    expected_group: str,
) -> None:
    """
    Verifica se o pipeline completo funciona para os três datasets.
    """
    assert dataset_path.exists()

    df = load_dataset(dataset_path)

    assert not df.empty
    assert df["Parceiro"].nunique() == 1
    assert df["Parceiro"].iloc[0] == expected_partner
    assert df["Grupos de usuários"].nunique() >= 2

    quality = run_quality_checks(df)

    analyzed_df = add_business_metrics(df)

    expected_metric_columns = {
        "receita_liquida",
        "taxa_comissao",
        "taxa_cashback",
        "margem_liquida",
        "ticket_medio",
        "receita_por_comprador",
    }

    assert expected_metric_columns.issubset(
        analyzed_df.columns
    )

    summary = create_group_summary(analyzed_df)

    assert not summary.empty
    assert len(summary) == df[
        "Grupos de usuários"
    ].nunique()

    comparisons = run_paired_analysis(
        df=analyzed_df,
        control_group="Grupo 1",
    )

    assert not comparisons.empty

    expected_comparisons = (
        df["Grupos de usuários"].nunique() - 1
    )

    comparison_groups = comparisons[
        "grupo_variante"
    ].nunique()

    assert comparison_groups == expected_comparisons

    decision = make_decision(
        summary=summary,
        comparisons=comparisons,
        quality=quality,
        control_group="Grupo 1",
    )

    assert decision["parceiro"] == expected_partner
    assert decision["decisao"] == expected_decision
    assert (
        decision["grupo_recomendado"]
        == expected_group
    )


def test_partner_a_detects_unstable_cashback() -> None:
    """
    Verifica se o problema de tratamento do Parceiro A é detectado.
    """
    df = load_dataset("data/parceiro_a.csv")

    quality = run_quality_checks(df)

    assert quality["status"] == "REVISÃO NECESSÁRIA"
    assert quality["grupos_instaveis"]
    assert "Grupo 1" in quality["grupos_instaveis"]


@pytest.mark.parametrize(
    "dataset_path",
    [
        Path("data/parceiro_b.csv"),
        Path("data/parceiro_c.csv"),
    ],
)
def test_stable_datasets_are_approved(
    dataset_path: Path,
) -> None:
    """
    Verifica se B e C passam nas validações de qualidade.
    """
    df = load_dataset(dataset_path)

    quality = run_quality_checks(df)

    assert quality["status"] == "APROVADO"
    assert quality["grupos_instaveis"] == []
    assert quality["duplicidades"] == 0
    assert quality["datas_alinhadas"] is True


def test_tracker_updates_without_duplicates(
    tmp_path: Path,
) -> None:
    """
    Verifica se uma nova execução atualiza o teste existente,
    sem criar registros duplicados.
    """
    df = load_dataset("data/parceiro_b.csv")

    quality = run_quality_checks(df)
    analyzed_df = add_business_metrics(df)
    summary = create_group_summary(analyzed_df)

    comparisons = run_paired_analysis(
        analyzed_df,
        control_group="Grupo 1",
    )

    decision = make_decision(
        summary=summary,
        comparisons=comparisons,
        quality=quality,
        control_group="Grupo 1",
    )

    tracker_path = (
        tmp_path / "experiment_tracker.csv"
    )

    fake_report_path = Path(
        "reports/parceiro_b/relatorio.html"
    )

    update_experiment_tracker(
        analyzed_df=analyzed_df,
        summary=summary,
        quality=quality,
        decision=decision,
        report_path=fake_report_path,
        tracker_path=tracker_path,
    )

    update_experiment_tracker(
        analyzed_df=analyzed_df,
        summary=summary,
        quality=quality,
        decision=decision,
        report_path=fake_report_path,
        tracker_path=tracker_path,
    )

    tracker_df = pd.read_csv(
        tracker_path,
        encoding="utf-8-sig",
    )

    assert len(tracker_df) == 1
    assert (
        tracker_df.iloc[0]["parceiro"]
        == "Parceiro B"
    )
def test_currency_uses_brazilian_format() -> None:
    """Verifica se valores monetários usam o padrão brasileiro."""
    assert format_currency_brl(404711) == "R$ 404.711,00"
    assert format_currency_brl(1234.5) == "R$ 1.234,50"
    assert format_currency_brl(0) == "R$ 0,00"
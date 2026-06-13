from datetime import datetime
from pathlib import Path

import pandas as pd


TRACKER_COLUMNS = [
    "test_id",
    "nome_teste",
    "descricao",
    "parceiro",
    "data_inicio",
    "data_fim",
    "variantes",
    "quantidade_variantes",
    "status_dados",
    "resultado",
    "decisao",
    "grupo_recomendado",
    "escalar_automaticamente",
    "confianca",
    "avisos",
    "relatorio",
    "analisado_em",
]


def build_tracker_row(
    analyzed_df: pd.DataFrame,
    summary: pd.DataFrame,
    quality: dict,
    decision: dict,
    report_path: Path,
) -> dict:
    """
    Monta a linha consolidada de um teste A/B.
    """
    partner = str(decision["parceiro"])

    start_date = analyzed_df["Data"].min()
    end_date = analyzed_df["Data"].max()

    groups = sorted(
        analyzed_df["Grupos de usuários"].unique()
    )

    variants_text = ", ".join(groups)

    test_id = (
        f"{partner}|"
        f"{start_date.strftime('%Y-%m-%d')}|"
        f"{end_date.strftime('%Y-%m-%d')}"
    )

    best_revenue_row = summary.loc[
        summary["receita_liquida"].idxmax()
    ]

    best_revenue_group = str(
        best_revenue_row["Grupos de usuários"]
    )

    best_revenue = float(
        best_revenue_row["receita_liquida"]
    )

    warnings_text = (
        " | ".join(quality["avisos"])
        if quality["avisos"]
        else "Nenhum aviso relevante."
    )

    result_text = (
        f"O grupo com maior receita líquida total foi "
        f"{best_revenue_group}, com R$ {best_revenue:,.2f}. "
        f"{decision['motivo']}"
    )

    decision_text = (
        f"{decision['decisao']} — "
        f"{decision['grupo_recomendado']}"
    )

    description = (
        f"Teste A/B de cashback do {partner}, realizado entre "
        f"{start_date.strftime('%d/%m/%Y')} e "
        f"{end_date.strftime('%d/%m/%Y')}, com "
        f"{len(groups)} variantes: {variants_text}."
    )

    return {
        "test_id": test_id,
        "nome_teste": f"Teste de cashback — {partner}",
        "descricao": description,
        "parceiro": partner,
        "data_inicio": start_date.strftime("%Y-%m-%d"),
        "data_fim": end_date.strftime("%Y-%m-%d"),
        "variantes": variants_text,
        "quantidade_variantes": len(groups),
        "status_dados": quality["status"],
        "resultado": result_text,
        "decisao": decision_text,
        "grupo_recomendado": decision["grupo_recomendado"],
        "escalar_automaticamente": (
            decision["escalar_automaticamente"]
        ),
        "confianca": decision["confianca"],
        "avisos": warnings_text,
        "relatorio": report_path.as_posix(),
        "analisado_em": datetime.now().isoformat(
            timespec="seconds"
        ),
    }


def update_experiment_tracker(
    analyzed_df: pd.DataFrame,
    summary: pd.DataFrame,
    quality: dict,
    decision: dict,
    report_path: Path,
    tracker_path: Path = Path(
        "outputs/experiment_tracker.csv"
    ),
) -> Path:
    """
    Adiciona ou atualiza um teste no CSV consolidado.

    Caso o mesmo parceiro e período sejam analisados novamente,
    a linha anterior é substituída em vez de duplicada.
    """
    tracker_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    new_row = build_tracker_row(
        analyzed_df=analyzed_df,
        summary=summary,
        quality=quality,
        decision=decision,
        report_path=report_path,
    )

    new_row_df = pd.DataFrame(
        [new_row],
        columns=TRACKER_COLUMNS,
    )

    if tracker_path.exists():
        tracker_df = pd.read_csv(
            tracker_path,
            encoding="utf-8-sig",
        )

        if "test_id" not in tracker_df.columns:
            tracker_df = pd.DataFrame(
                columns=TRACKER_COLUMNS
            )

        tracker_df = tracker_df.loc[
            tracker_df["test_id"] != new_row["test_id"]
        ]

        tracker_df = pd.concat(
            [tracker_df, new_row_df],
            ignore_index=True,
        )

    else:
        tracker_df = new_row_df

    tracker_df = tracker_df[
        TRACKER_COLUMNS
    ].sort_values(
        by=["parceiro", "data_inicio"]
    )

    tracker_df.to_csv(
        tracker_path,
        index=False,
        encoding="utf-8-sig",
    )

    return tracker_path
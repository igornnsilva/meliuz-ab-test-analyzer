from datetime import datetime
from pathlib import Path

import pandas as pd

from src.formatters import format_currency_brl


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
    "relatorio_pdf",
    "analisado_em",
]


def build_tracker_row(
    analyzed_df: pd.DataFrame,
    summary: pd.DataFrame,
    quality: dict,
    decision: dict,
    report_path: Path,
    pdf_report_path: Path | None = None,
) -> dict:
    """
    Monta a linha consolidada de um teste A/B.

    O relatório HTML é obrigatório. O relatório PDF é opcional
    para manter compatibilidade com chamadas anteriores.
    """
    partner = str(decision["parceiro"])

    start_date = analyzed_df["Data"].min()
    end_date = analyzed_df["Data"].max()

    groups = sorted(
        analyzed_df["Grupos de usuários"]
        .astype(str)
        .unique()
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

    warnings = quality.get(
        "avisos",
        [],
    )

    warnings_text = (
        " | ".join(
            str(warning)
            for warning in warnings
        )
        if warnings
        else "Nenhum aviso relevante."
    )

    result_text = (
        "O grupo com maior receita líquida total foi "
        f"{best_revenue_group}, com "
        f"{format_currency_brl(best_revenue)}. "
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

    html_report = Path(
        report_path
    ).as_posix()

    pdf_report = (
        Path(pdf_report_path).as_posix()
        if pdf_report_path is not None
        else ""
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
        "grupo_recomendado": (
            decision["grupo_recomendado"]
        ),
        "escalar_automaticamente": (
            decision["escalar_automaticamente"]
        ),
        "confianca": decision["confianca"],
        "avisos": warnings_text,
        "relatorio": html_report,
        "relatorio_pdf": pdf_report,
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
    pdf_report_path: Path | None = None,
    tracker_path: Path = Path(
        "outputs/experiment_tracker.csv"
    ),
) -> Path:
    """
    Adiciona ou atualiza um teste no CSV consolidado.

    Caso o mesmo parceiro e período sejam analisados novamente,
    a linha anterior é substituída em vez de duplicada.

    Arquivos antigos que ainda não possuem a coluna
    relatorio_pdf são atualizados automaticamente.
    """
    tracker_path = Path(
        tracker_path
    )

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
        pdf_report_path=pdf_report_path,
    )

    new_row_df = pd.DataFrame(
        [new_row],
        columns=TRACKER_COLUMNS,
    )

    if tracker_path.exists():
        try:
            tracker_df = pd.read_csv(
                tracker_path,
                encoding="utf-8-sig",
            )
        except pd.errors.EmptyDataError:
            tracker_df = pd.DataFrame(
                columns=TRACKER_COLUMNS
            )

        if "test_id" not in tracker_df.columns:
            tracker_df = pd.DataFrame(
                columns=TRACKER_COLUMNS
            )
        else:
            # Acrescenta colunas novas e mantém a ordem oficial.
            tracker_df = tracker_df.reindex(
                columns=TRACKER_COLUMNS
            )

            tracker_df = tracker_df.loc[
                tracker_df["test_id"]
                != new_row["test_id"]
            ]

        tracker_df = pd.concat(
            [
                tracker_df,
                new_row_df,
            ],
            ignore_index=True,
        )

    else:
        tracker_df = new_row_df

    tracker_df = (
        tracker_df.reindex(
            columns=TRACKER_COLUMNS
        )
        .sort_values(
            by=[
                "parceiro",
                "data_inicio",
            ],
            na_position="last",
        )
        .reset_index(
            drop=True
        )
    )

    tracker_df.to_csv(
        tracker_path,
        index=False,
        encoding="utf-8-sig",
    )

    return tracker_path

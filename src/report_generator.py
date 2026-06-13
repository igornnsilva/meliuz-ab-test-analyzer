from html import escape
from pathlib import Path

import pandas as pd


def format_currency(value: float) -> str:
    """
    Formata valores monetários no padrão brasileiro.
    """
    if pd.isna(value):
        return "N/A"

    formatted = (
        f"{value:,.2f}"
        .replace(",", "TEMP")
        .replace(".", ",")
        .replace("TEMP", ".")
    )

    return f"R$ {formatted}"


def format_percentage(value: float) -> str:
    """
    Formata proporções como porcentagem.
    """
    if pd.isna(value):
        return "N/A"

    return f"{value * 100:.2f}%"


def prepare_summary_table(
    summary: pd.DataFrame,
) -> str:
    """
    Prepara a tabela consolidada para o relatório HTML.
    """
    table = summary[
        [
            "Grupos de usuários",
            "dias",
            "compradores",
            "vendas_totais",
            "cashback",
            "receita_liquida",
            "ticket_medio",
            "taxa_cashback",
            "margem_liquida",
        ]
    ].copy()

    table.columns = [
        "Variante",
        "Dias",
        "Compradores",
        "Vendas totais",
        "Cashback",
        "Receita líquida",
        "Ticket médio",
        "Taxa de cashback",
        "Margem líquida",
    ]

    table["Compradores"] = (
        table["Compradores"]
        .astype(int)
        .map(lambda value: f"{value:,}".replace(",", "."))
    )

    monetary_columns = [
        "Vendas totais",
        "Cashback",
        "Receita líquida",
        "Ticket médio",
    ]

    for column in monetary_columns:
        table[column] = table[column].map(
            format_currency
        )

    percentage_columns = [
        "Taxa de cashback",
        "Margem líquida",
    ]

    for column in percentage_columns:
        table[column] = table[column].map(
            format_percentage
        )

    return table.to_html(
        index=False,
        border=0,
        classes="data-table",
    )


def prepare_statistical_table(
    comparisons: pd.DataFrame,
) -> str:
    """
    Prepara os principais resultados estatísticos.
    """
    main_metrics = [
        "compradores",
        "vendas totais",
        "receita_liquida",
        "ticket_medio",
    ]

    table = comparisons.loc[
        comparisons["metrica"].isin(main_metrics),
        [
            "grupo_variante",
            "metrica",
            "lift_percentual",
            "p_valor_t_pareado",
            "ic95_inferior",
            "ic95_superior",
            "significativo_5pct",
        ],
    ].copy()

    metric_names = {
        "compradores": "Compradores",
        "vendas totais": "Vendas totais",
        "receita_liquida": "Receita líquida",
        "ticket_medio": "Ticket médio",
    }

    table["metrica"] = table["metrica"].map(
        metric_names
    )

    table["lift_percentual"] = table[
        "lift_percentual"
    ].map(
        lambda value: (
            "N/A"
            if pd.isna(value)
            else f"{value:+.2f}%"
        )
    )

    table["p_valor_t_pareado"] = table[
        "p_valor_t_pareado"
    ].map(
        lambda value: f"{value:.6f}"
    )

    table["intervalo_confianca"] = table.apply(
        lambda row: (
            f"[{row['ic95_inferior']:.2f}, "
            f"{row['ic95_superior']:.2f}]"
        ),
        axis=1,
    )

    table["significativo_5pct"] = table[
        "significativo_5pct"
    ].map(
        {
            True: "Sim",
            False: "Não",
        }
    )

    table = table[
        [
            "grupo_variante",
            "metrica",
            "lift_percentual",
            "p_valor_t_pareado",
            "intervalo_confianca",
            "significativo_5pct",
        ]
    ]

    table.columns = [
        "Variante",
        "Métrica",
        "Lift",
        "P-valor",
        "IC 95%",
        "Significativo",
    ]

    return table.to_html(
        index=False,
        border=0,
        classes="data-table",
    )


def generate_html_report(
    analyzed_df: pd.DataFrame,
    summary: pd.DataFrame,
    comparisons: pd.DataFrame,
    quality: dict,
    decision: dict,
    chart_paths: dict[str, Path],
    report_directory: Path,
) -> Path:
    """
    Gera um relatório HTML completo e apresentável.
    """
    report_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    report_path = report_directory / "relatorio.html"

    partner = escape(str(decision["parceiro"]))

    start_date = analyzed_df["Data"].min().strftime(
        "%d/%m/%Y"
    )

    end_date = analyzed_df["Data"].max().strftime(
        "%d/%m/%Y"
    )

    decision_class = (
        "decision-success"
        if decision["escalar_automaticamente"]
        else "decision-warning"
    )

    warnings = quality["avisos"]

    if warnings:
        warnings_html = "".join(
            f"<li>{escape(str(warning))}</li>"
            for warning in warnings
        )
    else:
        warnings_html = (
            "<li>Nenhum problema relevante encontrado.</li>"
        )

    summary_table = prepare_summary_table(summary)

    statistical_table = prepare_statistical_table(
        comparisons
    )

    chart_html = ""

    chart_titles = {
        "vendas": "Vendas totais por dia",
        "compradores": "Compradores por dia",
        "receita": "Receita líquida por dia",
        "cashback": "Estabilidade da taxa de cashback",
        "receita_total": "Receita líquida total",
    }

    for chart_name, chart_path in chart_paths.items():
        relative_path = chart_path.relative_to(
            report_directory
        ).as_posix()

        chart_html += f"""
        <section class="chart-card">
            <h3>{chart_titles[chart_name]}</h3>
            <img
                src="{relative_path}"
                alt="{chart_titles[chart_name]}"
            >
        </section>
        """

    html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >
    <title>Relatório A/B — {partner}</title>

    <style>
        body {{
            margin: 0;
            background: #f4f6f8;
            font-family: Arial, Helvetica, sans-serif;
            color: #202124;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 32px 20px 60px;
        }}

        .header {{
            background: #ffffff;
            padding: 28px;
            border-radius: 12px;
            margin-bottom: 24px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }}

        .header h1 {{
            margin-top: 0;
        }}

        .section {{
            background: #ffffff;
            padding: 24px;
            border-radius: 12px;
            margin-bottom: 24px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            overflow-x: auto;
        }}

        .decision {{
            padding: 24px;
            border-radius: 12px;
            margin-bottom: 24px;
        }}

        .decision-success {{
            background: #e6f4ea;
            border-left: 6px solid #188038;
        }}

        .decision-warning {{
            background: #fef7e0;
            border-left: 6px solid #f9ab00;
        }}

        .decision h2 {{
            margin-top: 0;
        }}

        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 16px;
        }}

        .data-table th,
        .data-table td {{
            padding: 12px;
            border-bottom: 1px solid #dadce0;
            text-align: left;
            white-space: nowrap;
        }}

        .data-table th {{
            background: #f1f3f4;
        }}

        .charts-grid {{
            display: grid;
            grid-template-columns:
                repeat(auto-fit, minmax(450px, 1fr));
            gap: 20px;
        }}

        .chart-card {{
            background: #ffffff;
            padding: 20px;
            border-radius: 12px;
            box-shadow:
                0 2px 8px rgba(0, 0, 0, 0.08);
        }}

        .chart-card img {{
            width: 100%;
            height: auto;
        }}

        .metadata {{
            display: flex;
            flex-wrap: wrap;
            gap: 24px;
        }}

        .metadata-item strong {{
            display: block;
            margin-bottom: 4px;
        }}

        .footer {{
            text-align: center;
            color: #5f6368;
            margin-top: 32px;
        }}
    </style>
</head>

<body>
    <main class="container">

        <header class="header">
            <h1>Relatório de Teste A/B de Cashback</h1>

            <div class="metadata">
                <div class="metadata-item">
                    <strong>Parceiro</strong>
                    {partner}
                </div>

                <div class="metadata-item">
                    <strong>Período</strong>
                    {start_date} até {end_date}
                </div>

                <div class="metadata-item">
                    <strong>Status dos dados</strong>
                    {escape(str(quality["status"]))}
                </div>

                <div class="metadata-item">
                    <strong>Grupo de controle</strong>
                    {escape(str(decision["grupo_controle"]))}
                </div>
            </div>
        </header>

        <section class="decision {decision_class}">
            <h2>Decisão recomendada</h2>

            <p>
                <strong>Decisão:</strong>
                {escape(str(decision["decisao"]))}
            </p>

            <p>
                <strong>Grupo recomendado:</strong>
                {escape(str(decision["grupo_recomendado"]))}
            </p>

            <p>
                <strong>Confiança:</strong>
                {escape(str(decision["confianca"]))}
            </p>

            <p>
                <strong>Justificativa:</strong><br>
                {escape(str(decision["motivo"]))}
            </p>
        </section>

        <section class="section">
            <h2>Qualidade dos dados</h2>

            <ul>
                {warnings_html}
            </ul>
        </section>

        <section class="section">
            <h2>Resultados consolidados</h2>

            {summary_table}
        </section>

        <section class="section">
            <h2>Comparações estatísticas</h2>

            <p>
                As variantes foram comparadas com o grupo de
                controle usando observações pareadas por data.
            </p>

            {statistical_table}
        </section>

        <section>
            <h2>Visualizações</h2>

            <div class="charts-grid">
                {chart_html}
            </div>
        </section>

        <footer class="footer">
            Relatório gerado automaticamente pela solução
            de análise de testes A/B.
        </footer>

    </main>
</body>
</html>
"""

    report_path.write_text(
        html_content,
        encoding="utf-8",
    )

    return report_path
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


def save_line_chart(
    df: pd.DataFrame,
    metric: str,
    title: str,
    ylabel: str,
    output_path: Path,
    percentage: bool = False,
) -> None:
    """
    Gera um gráfico de linha por grupo ao longo do tempo.
    """
    plt.figure(figsize=(12, 6))

    for group in sorted(df["Grupos de usuários"].unique()):
        group_data = df.loc[
            df["Grupos de usuários"] == group
        ].sort_values("Data")

        values = group_data[metric]

        if percentage:
            values = values * 100

        plt.plot(
            group_data["Data"],
            values,
            label=group,
            linewidth=2,
        )

    plt.title(title)
    plt.xlabel("Data")
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=150,
        bbox_inches="tight",
    )

    plt.close()


def save_bar_chart(
    summary: pd.DataFrame,
    metric: str,
    title: str,
    ylabel: str,
    output_path: Path,
) -> None:
    """
    Gera um gráfico de barras das métricas consolidadas.
    """
    chart_data = summary.sort_values(
        "Grupos de usuários"
    )

    plt.figure(figsize=(9, 6))

    bars = plt.bar(
        chart_data["Grupos de usuários"],
        chart_data[metric],
    )

    plt.title(title)
    plt.xlabel("Variante")
    plt.ylabel(ylabel)
    plt.grid(
        axis="y",
        alpha=0.3,
    )

    for bar, value in zip(
        bars,
        chart_data[metric],
    ):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:,.0f}",
            ha="center",
            va="bottom",
        )

    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=150,
        bbox_inches="tight",
    )

    plt.close()


def generate_charts(
    analyzed_df: pd.DataFrame,
    summary: pd.DataFrame,
    report_directory: Path,
) -> dict[str, Path]:
    """
    Gera todos os gráficos utilizados no relatório.
    """
    charts_directory = report_directory / "charts"

    charts_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    chart_paths = {
        "vendas": charts_directory / "vendas_diarias.png",
        "compradores": charts_directory / "compradores_diarios.png",
        "receita": charts_directory / "receita_liquida_diaria.png",
        "cashback": charts_directory / "taxa_cashback.png",
        "receita_total": charts_directory / "receita_liquida_total.png",
    }

    save_line_chart(
        df=analyzed_df,
        metric="vendas totais",
        title="Vendas totais diárias por variante",
        ylabel="Vendas totais (R$)",
        output_path=chart_paths["vendas"],
    )

    save_line_chart(
        df=analyzed_df,
        metric="compradores",
        title="Compradores diários por variante",
        ylabel="Quantidade de compradores",
        output_path=chart_paths["compradores"],
    )

    save_line_chart(
        df=analyzed_df,
        metric="receita_liquida",
        title="Receita líquida diária por variante",
        ylabel="Receita líquida (R$)",
        output_path=chart_paths["receita"],
    )

    save_line_chart(
        df=analyzed_df,
        metric="taxa_cashback",
        title="Taxa de cashback ao longo do teste",
        ylabel="Taxa de cashback (%)",
        output_path=chart_paths["cashback"],
        percentage=True,
    )

    save_bar_chart(
        summary=summary,
        metric="receita_liquida",
        title="Receita líquida total por variante",
        ylabel="Receita líquida total (R$)",
        output_path=chart_paths["receita_total"],
    )

    return chart_paths
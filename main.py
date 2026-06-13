
import argparse
import unicodedata
from pathlib import Path

import pandas as pd

from src.charts import generate_charts
from src.data_loader import load_dataset
from src.data_quality import run_quality_checks
from src.decision_engine import (
    decision_to_dataframe,
    make_decision,
)
from src.metrics import (
    add_business_metrics,
    create_group_summary,
)
from src.report_generator import generate_html_report
from src.statistical_analysis import run_paired_analysis
from src.tracker import update_experiment_tracker


def parse_arguments() -> argparse.Namespace:
    """
    Lê os argumentos enviados pelo terminal.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Analisador reutilizável de testes A/B de cashback."
        )
    )

    parser.add_argument(
        "--file",
        required=True,
        help="Caminho do arquivo CSV que será analisado.",
    )

    parser.add_argument(
        "--control",
        default="Grupo 1",
        help="Nome do grupo de controle. Padrão: Grupo 1.",
    )

    return parser.parse_args()


def create_partner_slug(partner: str) -> str:
    """
    Cria um nome seguro para arquivos e diretórios.

    Exemplo:
        Parceiro Á -> parceiro_a
    """
    normalized = unicodedata.normalize(
        "NFKD",
        partner.strip().lower(),
    )

    without_accents = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )

    slug = "".join(
        character if character.isalnum() else "_"
        for character in without_accents
    )

    while "__" in slug:
        slug = slug.replace("__", "_")

    return slug.strip("_")


def format_currency(value: float) -> str:
    """
    Formata um número como moeda brasileira.
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


def format_number(value: float) -> str:
    """
    Formata um número inteiro no padrão brasileiro.
    """
    if pd.isna(value):
        return "N/A"

    return f"{int(value):,}".replace(",", ".")


def validate_loaded_dataset(df: pd.DataFrame) -> None:
    """
    Executa validações adicionais após o carregamento.
    """
    if df.empty:
        raise ValueError(
            "O dataset está vazio e não pode ser analisado."
        )

    partner_count = df["Parceiro"].nunique()

    if partner_count != 1:
        raise ValueError(
            "Cada arquivo deve conter exatamente um parceiro. "
            f"Foram encontrados {partner_count} parceiros."
        )

    group_count = df["Grupos de usuários"].nunique()

    if group_count < 2:
        raise ValueError(
            "O dataset precisa possuir pelo menos dois grupos."
        )


def print_dataset_information(
    df: pd.DataFrame,
    file_path: str,
) -> None:
    """
    Exibe informações gerais do dataset.
    """
    print("\n" + "=" * 70)
    print("DATASET CARREGADO COM SUCESSO")
    print("=" * 70)

    print(f"\nArquivo: {file_path}")
    print(f"Quantidade de linhas: {len(df)}")
    print(f"Quantidade de colunas: {len(df.columns)}")

    print(
        "Período: "
        f"{df['Data'].min().strftime('%d/%m/%Y')} até "
        f"{df['Data'].max().strftime('%d/%m/%Y')}"
    )

    partners = ", ".join(
        sorted(df["Parceiro"].unique())
    )

    groups = ", ".join(
        sorted(df["Grupos de usuários"].unique())
    )

    print(f"Parceiro encontrado: {partners}")
    print(f"Grupos encontrados: {groups}")


def print_quality_report(quality: dict) -> None:
    """
    Exibe o relatório de qualidade dos dados.
    """
    print("\n" + "=" * 70)
    print("RELATÓRIO DE QUALIDADE DOS DADOS")
    print("=" * 70)

    print(f"\nStatus: {quality['status']}")
    print(f"Duplicidades: {quality['duplicidades']}")

    print(
        "Cashback acima da comissão:",
        quality["cashback_acima_comissao"],
    )

    print(
        "Todos os grupos possuem as mesmas datas:",
        quality["datas_alinhadas"],
    )

    print("\nValores nulos por coluna:")

    for column, count in quality["nulos_por_coluna"].items():
        print(f"  {column}: {count}")

    print("\nValores negativos por coluna:")

    for column, count in quality["valores_negativos"].items():
        print(f"  {column}: {count}")

    print("\nValores zerados por coluna:")

    for column, count in quality["valores_zerados"].items():
        print(f"  {column}: {count}")

    print("\nResumo dos grupos:")

    group_summary = quality["resumo_grupos"].copy()

    group_summary["primeira_data"] = (
        group_summary["primeira_data"]
        .dt.strftime("%d/%m/%Y")
    )

    group_summary["ultima_data"] = (
        group_summary["ultima_data"]
        .dt.strftime("%d/%m/%Y")
    )

    print(group_summary.to_string(index=False))

    print("\nEstabilidade da taxa de cashback:")

    cashback_stability = (
        quality["estabilidade_cashback"].copy()
    )

    percentage_columns = [
        "taxa_minima_pct",
        "taxa_maxima_pct",
        "taxa_media_pct",
        "taxa_mediana_pct",
        "desvio_padrao_pct",
        "amplitude_pct",
    ]

    for column in percentage_columns:
        cashback_stability[column] = (
            cashback_stability[column].round(4)
        )

    print(
        cashback_stability.to_string(
            index=False,
        )
    )

    print("\nAvisos:")

    if quality["avisos"]:
        for warning in quality["avisos"]:
            print(f"  - {warning}")
    else:
        print(
            "  Nenhum problema de qualidade encontrado."
        )


def print_business_summary(
    summary: pd.DataFrame,
) -> None:
    """
    Exibe as métricas consolidadas de cada variante.
    """
    print("\n" + "=" * 70)
    print("RESULTADOS CONSOLIDADOS POR VARIANTE")
    print("=" * 70)

    for _, row in summary.iterrows():
        print(
            f"\n{row['Grupos de usuários']}"
        )

        print("-" * 50)

        print(
            f"Dias analisados: {int(row['dias'])}"
        )

        print(
            "Compradores:",
            format_number(row["compradores"]),
        )

        print(
            "Vendas totais:",
            format_currency(row["vendas_totais"]),
        )

        print(
            "Comissão:",
            format_currency(row["comissao"]),
        )

        print(
            "Cashback:",
            format_currency(row["cashback"]),
        )

        print(
            "Receita líquida:",
            format_currency(
                row["receita_liquida"]
            ),
        )

        print(
            "Ticket médio:",
            format_currency(row["ticket_medio"]),
        )

        print(
            "Receita por comprador:",
            format_currency(
                row["receita_por_comprador"]
            ),
        )

        print(
            "Média diária de compradores:",
            f"{row['media_diaria_compradores']:.2f}",
        )

        print(
            "Média diária de vendas:",
            format_currency(
                row["media_diaria_vendas"]
            ),
        )

        print(
            "Média diária de receita líquida:",
            format_currency(
                row["media_diaria_receita_liquida"]
            ),
        )

        print(
            f"Taxa de comissão: "
            f"{row['taxa_comissao'] * 100:.2f}%"
        )

        print(
            f"Taxa de cashback: "
            f"{row['taxa_cashback'] * 100:.2f}%"
        )

        print(
            f"Margem líquida: "
            f"{row['margem_liquida'] * 100:.2f}%"
        )


def print_statistical_results(
    comparisons: pd.DataFrame,
) -> None:
    """
    Exibe os resultados das comparações estatísticas.
    """
    print("\n" + "=" * 70)
    print("COMPARAÇÕES ESTATÍSTICAS PAREADAS")
    print("=" * 70)

    metric_names = {
        "compradores": "Compradores",
        "vendas totais": "Vendas totais",
        "receita_liquida": "Receita líquida",
        "ticket_medio": "Ticket médio",
        "margem_liquida": "Margem líquida",
        "receita_por_comprador": (
            "Receita por comprador"
        ),
    }

    for variant, results in comparisons.groupby(
        "grupo_variante"
    ):
        control = results[
            "grupo_controle"
        ].iloc[0]

        print(f"\n{variant} versus {control}")
        print("-" * 70)

        for _, row in results.iterrows():
            metric_name = metric_names.get(
                row["metrica"],
                row["metrica"],
            )

            significance = (
                "SIGNIFICATIVO"
                if row["significativo_5pct"]
                else "NÃO SIGNIFICATIVO"
            )

            lift = row["lift_percentual"]

            lift_text = (
                "N/A"
                if pd.isna(lift)
                else f"{lift:+.2f}%"
            )

            print(f"\n{metric_name}")
            print(f"  Lift: {lift_text}")

            print(
                f"  Média diária do controle: "
                f"{row['media_diaria_controle']:.2f}"
            )

            print(
                f"  Média diária da variante: "
                f"{row['media_diaria_variante']:.2f}"
            )

            print(
                f"  Diferença média diária: "
                f"{row['diferenca_media_diaria']:.2f}"
            )

            print(
                f"  IC 95% da diferença: "
                f"[{row['ic95_inferior']:.2f}, "
                f"{row['ic95_superior']:.2f}]"
            )

            print(
                f"  Teste t pareado — p-valor: "
                f"{row['p_valor_t_pareado']:.6f}"
            )

            print(
                f"  Wilcoxon — p-valor: "
                f"{row['p_valor_wilcoxon']:.6f}"
            )

            print(
                f"  Resultado: {significance}"
            )


def print_decision(decision: dict) -> None:
    """
    Exibe a recomendação final do motor de decisão.
    """
    print("\n" + "=" * 70)
    print("DECISÃO RECOMENDADA")
    print("=" * 70)

    print(
        f"\nParceiro: {decision['parceiro']}"
    )

    print(
        f"Decisão: {decision['decisao']}"
    )

    print(
        "Grupo recomendado:",
        decision["grupo_recomendado"],
    )

    print(
        "Escalar automaticamente:",
        (
            "SIM"
            if decision["escalar_automaticamente"]
            else "NÃO"
        ),
    )

    print(
        f"Confiança: {decision['confianca']}"
    )

    print(
        f"\nJustificativa:\n"
        f"{decision['motivo']}"
    )


def save_outputs(
    summary: pd.DataFrame,
    comparisons: pd.DataFrame,
    decision: dict,
    partner: str,
) -> list[Path]:
    """
    Salva os resultados consolidados em arquivos CSV.
    """
    output_directory = Path("outputs")

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    partner_slug = create_partner_slug(partner)

    summary_path = (
        output_directory
        / f"{partner_slug}_resumo_grupos.csv"
    )

    comparisons_path = (
        output_directory
        / (
            f"{partner_slug}_"
            "comparacoes_estatisticas.csv"
        )
    )

    decision_path = (
        output_directory
        / f"{partner_slug}_decisao.csv"
    )

    summary.to_csv(
        summary_path,
        index=False,
        encoding="utf-8-sig",
    )

    comparisons.to_csv(
        comparisons_path,
        index=False,
        encoding="utf-8-sig",
    )

    decision_to_dataframe(
        decision
    ).to_csv(
        decision_path,
        index=False,
        encoding="utf-8-sig",
    )

    return [
        summary_path,
        comparisons_path,
        decision_path,
    ]


def generate_report_files(
    analyzed_df: pd.DataFrame,
    summary: pd.DataFrame,
    comparisons: pd.DataFrame,
    quality: dict,
    decision: dict,
    partner: str,
) -> Path:
    """
    Gera os gráficos e o relatório HTML.
    """
    partner_slug = create_partner_slug(partner)

    report_directory = (
        Path("reports") / partner_slug
    )

    chart_paths = generate_charts(
        analyzed_df=analyzed_df,
        summary=summary,
        report_directory=report_directory,
    )

    report_path = generate_html_report(
        analyzed_df=analyzed_df,
        summary=summary,
        comparisons=comparisons,
        quality=quality,
        decision=decision,
        chart_paths=chart_paths,
        report_directory=report_directory,
    )

    return report_path


def main() -> None:
    """
    Executa todas as etapas da análise.
    """
    arguments = parse_arguments()

    try:
        df = load_dataset(arguments.file)

        validate_loaded_dataset(df)

        print_dataset_information(
            df=df,
            file_path=arguments.file,
        )

        partner = str(
            df["Parceiro"].iloc[0]
        )

        quality = run_quality_checks(df)

        print_quality_report(quality)

        analyzed_df = add_business_metrics(df)

        summary = create_group_summary(
            analyzed_df
        )

        print_business_summary(summary)

        comparisons = run_paired_analysis(
            df=analyzed_df,
            control_group=arguments.control,
        )

        print_statistical_results(
            comparisons
        )

        decision = make_decision(
            summary=summary,
            comparisons=comparisons,
            quality=quality,
            control_group=arguments.control,
        )

        print_decision(decision)

        output_paths = save_outputs(
            summary=summary,
            comparisons=comparisons,
            decision=decision,
            partner=partner,
        )

        report_path = generate_report_files(
            analyzed_df=analyzed_df,
            summary=summary,
            comparisons=comparisons,
            quality=quality,
            decision=decision,
            partner=partner,
        )

        tracker_path = update_experiment_tracker(
            analyzed_df=analyzed_df,
            summary=summary,
            quality=quality,
            decision=decision,
            report_path=report_path,
        )

        print("\n" + "=" * 70)
        print("ANÁLISE FINALIZADA COM SUCESSO")
        print("=" * 70)

        print("\nArquivos CSV gerados:")

        for output_path in output_paths:
            print(
                f"  {output_path.resolve()}"
            )

        print(
            f"\nRelatório HTML gerado:\n"
            f"  {report_path.resolve()}"
        )

        print(
            f"\nPlanilha consolidada em CSV:\n"
            f"  {tracker_path.resolve()}"
        )

    except (
        FileNotFoundError,
        ValueError,
        KeyError,
        pd.errors.ParserError,
        pd.errors.EmptyDataError,
    ) as error:
        print("\n" + "=" * 70)
        print("ERRO DURANTE A ANÁLISE")
        print("=" * 70)

        print(
            f"\nTipo do erro: "
            f"{type(error).__name__}"
        )

        print(f"Mensagem: {error}")

        raise SystemExit(1) from error

    except Exception as error:
        print("\n" + "=" * 70)
        print("ERRO INESPERADO DURANTE A ANÁLISE")
        print("=" * 70)

        print(
            f"\nTipo do erro: "
            f"{type(error).__name__}"
        )

        print(f"Mensagem: {error}")

        raise SystemExit(1) from error


if __name__ == "__main__":
    main()


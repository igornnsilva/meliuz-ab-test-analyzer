import pandas as pd


NUMERIC_COLUMNS = [
    "compradores",
    "comissão",
    "cashback",
    "vendas totais",
]

# Variações muito pequenas podem acontecer porque os valores
# monetários foram arredondados para reais inteiros.
MAX_RATE_SPREAD_PERCENTAGE_POINTS = 0.10


def check_group_dates(df: pd.DataFrame) -> tuple[bool, list[str]]:
    """
    Verifica se todos os grupos possuem observações nas mesmas datas.
    """
    group_column = "Grupos de usuários"
    groups = sorted(df[group_column].unique())

    if not groups:
        return False, []

    reference_group = groups[0]

    reference_dates = set(
        df.loc[df[group_column] == reference_group, "Data"]
    )

    groups_with_different_dates = []

    for group in groups[1:]:
        current_dates = set(
            df.loc[df[group_column] == group, "Data"]
        )

        if current_dates != reference_dates:
            groups_with_different_dates.append(group)

    dates_are_aligned = len(groups_with_different_dates) == 0

    return dates_are_aligned, groups_with_different_dates


def analyze_cashback_stability(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, list[str]]:
    """
    Analisa se a taxa de cashback permaneceu estável em cada grupo.

    A taxa é calculada como:

        cashback / vendas totais * 100

    A amplitude representa a diferença entre a maior e a menor taxa
    observada dentro do grupo.
    """
    valid_rows = df["vendas totais"] > 0

    rate_df = df.loc[valid_rows].copy()

    rate_df["taxa_cashback_pct"] = (
        rate_df["cashback"]
        / rate_df["vendas totais"]
        * 100
    )

    # Aproxima a taxa para intervalos de 0,5 ponto percentual.
    # Isso ajuda a identificar as taxas nominais do teste.
    rate_df["taxa_nominal_pct"] = (
        rate_df["taxa_cashback_pct"] * 2
    ).round() / 2

    stability_summary = (
        rate_df.groupby("Grupos de usuários")
        .agg(
            observacoes=("Data", "size"),
            taxa_minima_pct=("taxa_cashback_pct", "min"),
            taxa_maxima_pct=("taxa_cashback_pct", "max"),
            taxa_media_pct=("taxa_cashback_pct", "mean"),
            taxa_mediana_pct=("taxa_cashback_pct", "median"),
            desvio_padrao_pct=("taxa_cashback_pct", "std"),
        )
        .reset_index()
    )

    stability_summary["amplitude_pct"] = (
        stability_summary["taxa_maxima_pct"]
        - stability_summary["taxa_minima_pct"]
    )

    nominal_rates = (
        rate_df.groupby("Grupos de usuários")["taxa_nominal_pct"]
        .apply(
            lambda values: sorted(
                float(value)
                for value in values.dropna().unique()
            )
        )
        .reset_index(name="taxas_nominais_detectadas")
    )

    stability_summary = stability_summary.merge(
        nominal_rates,
        on="Grupos de usuários",
        how="left",
    )

    stability_summary["quantidade_taxas_detectadas"] = (
        stability_summary["taxas_nominais_detectadas"].apply(len)
    )

    stability_summary["tratamento_estavel"] = (
        stability_summary["amplitude_pct"]
        <= MAX_RATE_SPREAD_PERCENTAGE_POINTS
    )

    unstable_groups = stability_summary.loc[
        ~stability_summary["tratamento_estavel"],
        "Grupos de usuários",
    ].tolist()

    return stability_summary, unstable_groups


def run_quality_checks(df: pd.DataFrame) -> dict:
    """
    Executa verificações estruturais, numéricas e de estabilidade
    do tratamento.
    """
    duplicated_rows = int(
        df.duplicated(
            subset=[
                "Data",
                "Grupos de usuários",
                "Parceiro",
            ]
        ).sum()
    )

    nulls_by_column = {
        column: int(count)
        for column, count in df.isna().sum().items()
    }

    negative_values = {
        column: int((df[column] < 0).sum())
        for column in NUMERIC_COLUMNS
    }

    zero_values = {
        column: int((df[column] == 0).sum())
        for column in NUMERIC_COLUMNS
    }

    cashback_above_commission = int(
        (df["cashback"] > df["comissão"]).sum()
    )

    group_summary = (
        df.groupby("Grupos de usuários")
        .agg(
            quantidade_linhas=("Data", "size"),
            quantidade_dias=("Data", "nunique"),
            primeira_data=("Data", "min"),
            ultima_data=("Data", "max"),
        )
        .reset_index()
    )

    dates_are_aligned, different_date_groups = check_group_dates(df)

    cashback_stability, unstable_groups = (
        analyze_cashback_stability(df)
    )

    warnings = []

    if duplicated_rows > 0:
        warnings.append(
            f"Foram encontradas {duplicated_rows} observações duplicadas."
        )

    total_nulls = sum(nulls_by_column.values())

    if total_nulls > 0:
        warnings.append(
            f"Foram encontrados {total_nulls} valores nulos."
        )

    total_negative_values = sum(negative_values.values())

    if total_negative_values > 0:
        warnings.append(
            f"Foram encontrados {total_negative_values} valores negativos."
        )

    if cashback_above_commission > 0:
        warnings.append(
            "Existem observações em que o cashback é maior que a comissão."
        )

    if not dates_are_aligned:
        warnings.append(
            "Os grupos não possuem observações exatamente nas mesmas datas."
        )

    if df["Parceiro"].nunique() > 1:
        warnings.append(
            "O arquivo possui mais de um parceiro."
        )

    if unstable_groups:
        group_names = ", ".join(unstable_groups)

        warnings.append(
            "A taxa de cashback não permaneceu estável nos grupos: "
            f"{group_names}."
        )

    status = "APROVADO" if not warnings else "REVISÃO NECESSÁRIA"

    return {
        "status": status,
        "quantidade_linhas": len(df),
        "quantidade_colunas": len(df.columns),
        "duplicidades": duplicated_rows,
        "nulos_por_coluna": nulls_by_column,
        "valores_negativos": negative_values,
        "valores_zerados": zero_values,
        "cashback_acima_comissao": cashback_above_commission,
        "datas_alinhadas": dates_are_aligned,
        "grupos_com_datas_diferentes": different_date_groups,
        "resumo_grupos": group_summary,
        "estabilidade_cashback": cashback_stability,
        "grupos_instaveis": unstable_groups,
        "avisos": warnings,
    }
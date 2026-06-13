from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy import stats


METRICS = [
    "compradores",
    "vendas totais",
    "receita_liquida",
    "ticket_medio",
    "margem_liquida",
    "receita_por_comprador",
]


def calculate_confidence_interval(
    differences: pd.Series,
    confidence_level: float = 0.95,
) -> tuple[float, float]:
    """
    Calcula o intervalo de confiança da diferença média pareada.
    """
    clean_differences = differences.dropna().astype(float)

    sample_size = len(clean_differences)

    if sample_size < 2:
        return float("nan"), float("nan")

    mean_difference = float(clean_differences.mean())

    standard_deviation = float(
        clean_differences.std(ddof=1)
    )

    if np.isclose(standard_deviation, 0):
        return mean_difference, mean_difference

    standard_error = (
        standard_deviation / math.sqrt(sample_size)
    )

    alpha = 1 - confidence_level

    critical_value = stats.t.ppf(
        1 - alpha / 2,
        df=sample_size - 1,
    )

    margin_of_error = critical_value * standard_error

    return (
        mean_difference - margin_of_error,
        mean_difference + margin_of_error,
    )


def run_paired_t_test(
    control_values: pd.Series,
    variant_values: pd.Series,
) -> tuple[float, float]:
    """
    Executa o teste t pareado.
    """
    differences = (
        variant_values.astype(float)
        - control_values.astype(float)
    )

    if np.allclose(differences, 0):
        return 0.0, 1.0

    result = stats.ttest_rel(
        variant_values,
        control_values,
        nan_policy="omit",
    )

    return float(result.statistic), float(result.pvalue)


def run_wilcoxon_test(
    control_values: pd.Series,
    variant_values: pd.Series,
) -> tuple[float, float]:
    """
    Executa o teste não paramétrico de Wilcoxon pareado.

    Ele funciona como uma verificação de robustez para o teste t.
    """
    differences = (
        variant_values.astype(float)
        - control_values.astype(float)
    )

    if np.allclose(differences, 0):
        return 0.0, 1.0

    try:
        result = stats.wilcoxon(
            variant_values,
            control_values,
            alternative="two-sided",
            zero_method="wilcox",
            method="auto",
        )

        return float(result.statistic), float(result.pvalue)

    except ValueError:
        return float("nan"), float("nan")


def run_paired_analysis(
    df: pd.DataFrame,
    control_group: str = "Grupo 1",
    alpha: float = 0.05,
) -> pd.DataFrame:
    """
    Compara cada variante com o grupo de controle por data.
    """
    group_column = "Grupos de usuários"

    available_groups = sorted(
        df[group_column].unique()
    )

    if control_group not in available_groups:
        raise ValueError(
            f"O grupo de controle '{control_group}' não existe. "
            f"Grupos disponíveis: {available_groups}"
        )

    variant_groups = [
        group
        for group in available_groups
        if group != control_group
    ]

    if not variant_groups:
        raise ValueError(
            "O dataset precisa possuir pelo menos dois grupos."
        )

    results = []

    for variant_group in variant_groups:
        control_data = (
            df.loc[
                df[group_column] == control_group,
                ["Data", *METRICS],
            ]
            .copy()
        )

        variant_data = (
            df.loc[
                df[group_column] == variant_group,
                ["Data", *METRICS],
            ]
            .copy()
        )

        paired_data = control_data.merge(
            variant_data,
            on="Data",
            how="inner",
            suffixes=("_controle", "_variante"),
        )

        for metric in METRICS:
            control_column = f"{metric}_controle"
            variant_column = f"{metric}_variante"

            metric_data = paired_data[
                [
                    "Data",
                    control_column,
                    variant_column,
                ]
            ].dropna()

            control_values = metric_data[
                control_column
            ].astype(float)

            variant_values = metric_data[
                variant_column
            ].astype(float)

            differences = (
                variant_values - control_values
            )

            number_of_pairs = len(metric_data)

            control_mean = float(control_values.mean())
            variant_mean = float(variant_values.mean())
            mean_difference = float(differences.mean())

            if np.isclose(control_mean, 0):
                lift_percentage = float("nan")
            else:
                lift_percentage = (
                    mean_difference / control_mean * 100
                )

            t_statistic, t_pvalue = run_paired_t_test(
                control_values=control_values,
                variant_values=variant_values,
            )

            wilcoxon_statistic, wilcoxon_pvalue = (
                run_wilcoxon_test(
                    control_values=control_values,
                    variant_values=variant_values,
                )
            )

            confidence_lower, confidence_upper = (
                calculate_confidence_interval(
                    differences=differences,
                    confidence_level=0.95,
                )
            )

            statistically_significant = (
                t_pvalue < alpha
            )

            if mean_difference > 0:
                direction = "AUMENTO"
            elif mean_difference < 0:
                direction = "REDUÇÃO"
            else:
                direction = "SEM ALTERAÇÃO"

            results.append(
                {
                    "grupo_controle": control_group,
                    "grupo_variante": variant_group,
                    "metrica": metric,
                    "n_pares": number_of_pairs,
                    "media_diaria_controle": control_mean,
                    "media_diaria_variante": variant_mean,
                    "diferenca_media_diaria": mean_difference,
                    "lift_percentual": lift_percentage,
                    "ic95_inferior": confidence_lower,
                    "ic95_superior": confidence_upper,
                    "estatistica_t": t_statistic,
                    "p_valor_t_pareado": t_pvalue,
                    "estatistica_wilcoxon": (
                        wilcoxon_statistic
                    ),
                    "p_valor_wilcoxon": (
                        wilcoxon_pvalue
                    ),
                    "significativo_5pct": (
                        statistically_significant
                    ),
                    "direcao": direction,
                }
            )

    return pd.DataFrame(results)
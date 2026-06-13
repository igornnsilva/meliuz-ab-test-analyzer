from __future__ import annotations

import pandas as pd


def get_comparison_result(
    comparisons: pd.DataFrame,
    variant: str,
    metric: str,
) -> pd.Series | None:
    """
    Retorna a comparação de uma variante para uma métrica específica.
    """
    result = comparisons.loc[
        (comparisons["grupo_variante"] == variant)
        & (comparisons["metrica"] == metric)
    ]

    if result.empty:
        return None

    return result.iloc[0]


def identify_quality_blockers(quality: dict) -> list[str]:
    """
    Identifica problemas que impedem uma decisão automática confiável.
    """
    blockers = []

    if quality["duplicidades"] > 0:
        blockers.append("existem observações duplicadas")

    if sum(quality["nulos_por_coluna"].values()) > 0:
        blockers.append("existem valores nulos")

    if sum(quality["valores_negativos"].values()) > 0:
        blockers.append("existem valores negativos")

    if quality["cashback_acima_comissao"] > 0:
        blockers.append(
            "existem observações com cashback acima da comissão"
        )

    if not quality["datas_alinhadas"]:
        blockers.append(
            "os grupos não possuem observações nas mesmas datas"
        )

    if quality["grupos_instaveis"]:
        unstable_groups = ", ".join(
            quality["grupos_instaveis"]
        )

        blockers.append(
            "a taxa de cashback mudou durante o teste nos grupos: "
            f"{unstable_groups}"
        )

    return blockers


def choose_provisional_group(
    summary: pd.DataFrame,
) -> str:
    """
    Escolhe provisoriamente o grupo com maior receita líquida total.
    """
    best_index = summary["receita_liquida"].idxmax()

    return str(
        summary.loc[
            best_index,
            "Grupos de usuários",
        ]
    )


def evaluate_variant_against_control(
    comparisons: pd.DataFrame,
    variant: str,
) -> dict:
    """
    Avalia uma variante em relação ao controle.
    """
    revenue = get_comparison_result(
        comparisons,
        variant,
        "receita_liquida",
    )

    sales = get_comparison_result(
        comparisons,
        variant,
        "vendas totais",
    )

    buyers = get_comparison_result(
        comparisons,
        variant,
        "compradores",
    )

    if revenue is None or sales is None or buyers is None:
        return {
            "variant": variant,
            "valid": False,
            "reason": "comparação incompleta",
        }

    revenue_positive_significant = bool(
        revenue["lift_percentual"] > 0
        and revenue["significativo_5pct"]
        and revenue["ic95_inferior"] > 0
    )

    revenue_negative_significant = bool(
        revenue["lift_percentual"] < 0
        and revenue["significativo_5pct"]
        and revenue["ic95_superior"] < 0
    )

    sales_positive_significant = bool(
        sales["lift_percentual"] > 0
        and sales["significativo_5pct"]
    )

    buyers_positive_significant = bool(
        buyers["lift_percentual"] > 0
        and buyers["significativo_5pct"]
    )

    growth_positive_significant = bool(
        sales_positive_significant
        or buyers_positive_significant
    )

    return {
        "variant": variant,
        "valid": True,
        "revenue_lift": float(
            revenue["lift_percentual"]
        ),
        "sales_lift": float(
            sales["lift_percentual"]
        ),
        "buyers_lift": float(
            buyers["lift_percentual"]
        ),
        "revenue_positive_significant": (
            revenue_positive_significant
        ),
        "revenue_negative_significant": (
            revenue_negative_significant
        ),
        "growth_positive_significant": (
            growth_positive_significant
        ),
    }


def make_decision(
    summary: pd.DataFrame,
    comparisons: pd.DataFrame,
    quality: dict,
    control_group: str = "Grupo 1",
) -> dict:
    """
    Produz uma decisão automática e auditável para o teste A/B.
    """
    partner = str(summary["Parceiro"].iloc[0])

    available_groups = summary[
        "Grupos de usuários"
    ].tolist()

    if control_group not in available_groups:
        raise ValueError(
            f"O grupo de controle '{control_group}' "
            "não está presente no resumo."
        )

    quality_blockers = identify_quality_blockers(
        quality
    )

    provisional_group = choose_provisional_group(
        summary
    )

    # Problemas de qualidade impedem uma decisão causal automática.
    if quality_blockers:
        blockers_text = "; ".join(quality_blockers)

        return {
            "parceiro": partner,
            "grupo_controle": control_group,
            "grupo_recomendado": provisional_group,
            "decisao": "REVISÃO NECESSÁRIA",
            "escalar_automaticamente": False,
            "confianca": "BAIXA",
            "motivo": (
                "A decisão automática foi bloqueada porque "
                f"{blockers_text}. "
                f"Se fosse obrigatório escolher apenas pelos "
                f"resultados agregados, o grupo provisório seria "
                f"{provisional_group}, por apresentar a maior "
                f"receita líquida total."
            ),
        }

    variant_groups = [
        group
        for group in available_groups
        if group != control_group
    ]

    evaluations = [
        evaluate_variant_against_control(
            comparisons=comparisons,
            variant=variant,
        )
        for variant in variant_groups
    ]

    strong_candidates = [
        evaluation["variant"]
        for evaluation in evaluations
        if evaluation.get(
            "revenue_positive_significant",
            False,
        )
    ]

    # Uma variante só substitui o controle automaticamente quando
    # melhora significativamente a receita líquida.
    if strong_candidates:
        candidate_summary = summary.loc[
            summary["Grupos de usuários"].isin(
                strong_candidates
            )
        ]

        best_candidate_index = (
            candidate_summary["receita_liquida"].idxmax()
        )

        best_candidate = str(
            summary.loc[
                best_candidate_index,
                "Grupos de usuários",
            ]
        )

        candidate_evaluation = next(
            evaluation
            for evaluation in evaluations
            if evaluation["variant"] == best_candidate
        )

        return {
            "parceiro": partner,
            "grupo_controle": control_group,
            "grupo_recomendado": best_candidate,
            "decisao": "ESCALAR",
            "escalar_automaticamente": True,
            "confianca": "ALTA",
            "motivo": (
                f"{best_candidate} apresentou aumento "
                f"estatisticamente significativo de "
                f"{candidate_evaluation['revenue_lift']:.2f}% "
                f"na receita líquida em relação ao controle."
            ),
        }

    revenue_dominated_variants = [
        evaluation
        for evaluation in evaluations
        if evaluation.get(
            "revenue_negative_significant",
            False,
        )
    ]

    if len(revenue_dominated_variants) == len(
        variant_groups
    ):
        confidence = "ALTA"
    else:
        confidence = "MÉDIA"

    variant_descriptions = []

    for evaluation in evaluations:
        if not evaluation.get("valid"):
            continue

        variant_descriptions.append(
            f"{evaluation['variant']}: "
            f"receita líquida "
            f"{evaluation['revenue_lift']:+.2f}%, "
            f"vendas "
            f"{evaluation['sales_lift']:+.2f}% e "
            f"compradores "
            f"{evaluation['buyers_lift']:+.2f}%"
        )

    descriptions_text = "; ".join(
        variant_descriptions
    )

    return {
        "parceiro": partner,
        "grupo_controle": control_group,
        "grupo_recomendado": control_group,
        "decisao": "ESCALAR",
        "escalar_automaticamente": True,
        "confianca": confidence,
        "motivo": (
            f"Nenhuma variante apresentou aumento "
            f"estatisticamente significativo de receita líquida "
            f"em relação ao controle. Portanto, a recomendação é "
            f"manter e escalar {control_group}. "
            f"Resultados observados: {descriptions_text}."
        ),
    }


def decision_to_dataframe(
    decision: dict,
) -> pd.DataFrame:
    """
    Converte a decisão em DataFrame para exportação.
    """
    return pd.DataFrame([decision])
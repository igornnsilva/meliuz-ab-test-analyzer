import numpy as np
import pandas as pd


def add_business_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adiciona métricas econômicas em cada observação diária.
    """
    result = df.copy()

    # Valor que efetivamente sobra para o Méliuz.
    result["receita_liquida"] = (
        result["comissão"] - result["cashback"]
    )

    # Comissão recebida como percentual das vendas.
    result["taxa_comissao"] = np.where(
        result["vendas totais"] > 0,
        result["comissão"] / result["vendas totais"],
        np.nan,
    )

    # Cashback distribuído como percentual das vendas.
    result["taxa_cashback"] = np.where(
        result["vendas totais"] > 0,
        result["cashback"] / result["vendas totais"],
        np.nan,
    )

    # Receita líquida como percentual das vendas.
    result["margem_liquida"] = np.where(
        result["vendas totais"] > 0,
        result["receita_liquida"] / result["vendas totais"],
        np.nan,
    )

    # Valor médio vendido por comprador.
    result["ticket_medio"] = np.where(
        result["compradores"] > 0,
        result["vendas totais"] / result["compradores"],
        np.nan,
    )

    # Receita líquida gerada por comprador.
    result["receita_por_comprador"] = np.where(
        result["compradores"] > 0,
        result["receita_liquida"] / result["compradores"],
        np.nan,
    )

    return result


def create_group_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Consolida os resultados de cada variante do teste.
    """
    summary = (
        df.groupby(
            ["Parceiro", "Grupos de usuários"],
            as_index=False,
        )
        .agg(
            dias=("Data", "nunique"),
            compradores=("compradores", "sum"),
            vendas_totais=("vendas totais", "sum"),
            comissao=("comissão", "sum"),
            cashback=("cashback", "sum"),
            receita_liquida=("receita_liquida", "sum"),
            media_diaria_compradores=("compradores", "mean"),
            media_diaria_vendas=("vendas totais", "mean"),
            media_diaria_receita_liquida=(
                "receita_liquida",
                "mean",
            ),
        )
    )

    # Métricas consolidadas devem ser calculadas usando os totais.
    summary["ticket_medio"] = np.where(
        summary["compradores"] > 0,
        summary["vendas_totais"] / summary["compradores"],
        np.nan,
    )

    summary["taxa_comissao"] = np.where(
        summary["vendas_totais"] > 0,
        summary["comissao"] / summary["vendas_totais"],
        np.nan,
    )

    summary["taxa_cashback"] = np.where(
        summary["vendas_totais"] > 0,
        summary["cashback"] / summary["vendas_totais"],
        np.nan,
    )

    summary["margem_liquida"] = np.where(
        summary["vendas_totais"] > 0,
        summary["receita_liquida"]
        / summary["vendas_totais"],
        np.nan,
    )

    summary["receita_por_comprador"] = np.where(
        summary["compradores"] > 0,
        summary["receita_liquida"]
        / summary["compradores"],
        np.nan,
    )

    return summary
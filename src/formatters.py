import pandas as pd


def format_currency_brl(value: float) -> str:
    """Formata um valor monetário no padrão brasileiro."""
    if pd.isna(value):
        return "N/A"

    formatted = (
        f"{float(value):,.2f}"
        .replace(",", "TEMP")
        .replace(".", ",")
        .replace("TEMP", ".")
    )

    return f"R$ {formatted}"


def format_integer_brl(value: float) -> str:
    """Formata um número inteiro com separador de milhar brasileiro."""
    if pd.isna(value):
        return "N/A"

    return f"{int(value):,}".replace(",", ".")
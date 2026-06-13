from pathlib import Path

import pandas as pd


# Colunas que obrigatoriamente devem existir nos datasets
REQUIRED_COLUMNS = {
    "Data",
    "Grupos de usuários",
    "Parceiro",
    "compradores",
    "comissão",
    "cashback",
    "vendas totais",
}


# Colunas que contêm valores monetários em formato brasileiro
MONETARY_COLUMNS = [
    "comissão",
    "cashback",
    "vendas totais",
]


def parse_brl_value(value: object) -> float:
    """
    Converte um valor monetário brasileiro para número.

    Exemplos:
        R$ 10.273    -> 10273.0
        R$ 1.234,56 -> 1234.56
        5000         -> 5000.0
    """
    if pd.isna(value):
        return float("nan")

    if isinstance(value, (int, float)):
        return float(value)

    cleaned_value = (
        str(value)
        .replace("R$", "")
        .replace("\u00a0", "")
        .replace(" ", "")
        .strip()
    )

    if not cleaned_value:
        return float("nan")

    # Se houver vírgula, ela é considerada separador decimal.
    if "," in cleaned_value:
        cleaned_value = (
            cleaned_value
            .replace(".", "")
            .replace(",", ".")
        )
    else:
        # Nos datasets, o ponto representa milhar.
        cleaned_value = cleaned_value.replace(".", "")

    try:
        return float(cleaned_value)
    except ValueError as error:
        raise ValueError(
            f"Não foi possível converter o valor monetário: {value}"
        ) from error


def validate_schema(df: pd.DataFrame) -> None:
    """
    Verifica se o dataset possui todas as colunas obrigatórias.
    """
    missing_columns = REQUIRED_COLUMNS.difference(df.columns)

    if missing_columns:
        missing_text = ", ".join(sorted(missing_columns))

        raise ValueError(
            f"O dataset não possui as seguintes colunas obrigatórias: "
            f"{missing_text}"
        )


def load_dataset(file_path: str | Path) -> pd.DataFrame:
    """
    Carrega, valida e prepara um dataset de teste A/B.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {path.resolve()}"
        )

    if path.suffix.lower() != ".csv":
        raise ValueError(
            "O arquivo informado precisa estar no formato CSV."
        )

    # utf-8-sig também funciona caso o arquivo possua BOM.
    df = pd.read_csv(path, encoding="utf-8-sig")

    # Remove espaços acidentais dos nomes das colunas.
    df.columns = df.columns.str.strip()

    validate_schema(df)

    df = df.copy()

    # Converte a data para o tipo de data do Pandas.
    df["Data"] = pd.to_datetime(
        df["Data"],
        format="%Y-%m-%d",
        errors="raise",
    )

    # Converte as colunas monetárias.
    for column in MONETARY_COLUMNS:
        df[column] = df[column].apply(parse_brl_value)

    # Garante que compradores seja uma coluna numérica inteira.
    df["compradores"] = pd.to_numeric(
        df["compradores"],
        errors="raise",
    ).astype(int)

    # Remove espaços acidentais dos campos de texto.
    df["Grupos de usuários"] = (
        df["Grupos de usuários"].astype(str).str.strip()
    )

    df["Parceiro"] = (
        df["Parceiro"].astype(str).str.strip()
    )

    # Ordena para facilitar as análises posteriores.
    df = df.sort_values(
        by=["Parceiro", "Grupos de usuários", "Data"]
    ).reset_index(drop=True)

    return df

import json
from pathlib import Path


# ==================================================
# 1. CONFIGURAÇÕES
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DATA_FOLDER = (
    PROJECT_ROOT / "data" / "processed" / "nasa"
)


# ==================================================
# 2. CARREGAR OS DADOS ORIGINAIS
# ==================================================

def load_raw_data(raw_file):
    """
    Carrega os dados originais da NASA a partir
    do caminho recebido.
    """

    raw_file = Path(raw_file)

    if not raw_file.exists():
        raise FileNotFoundError(
            f"Ficheiro original não encontrado: {raw_file}"
        )

    with open(
        raw_file,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    return data


# ==================================================
# 3. LIMPAR VALORES INDIVIDUAIS
# ==================================================

def clean_value(value, fill_value):
    """
    Substitui os valores de preenchimento da NASA
    por None.
    """

    if value == fill_value:
        return None

    return value


# ==================================================
# 4. LIMPAR E ORGANIZAR OS PARÂMETROS
# ==================================================

def clear_parameters(data: dict):
    """
    Organiza os parâmetros da NASA por dia
    e substitui valores ausentes por None.
    """

    parameters = (
        data.get("properties", {})
        .get("parameter", {})
    )

    fill_value = (
        data.get("header", {})
        .get("fill_value", -999)
    )

    if not isinstance(parameters, dict) or not parameters:
        raise ValueError(
            "Não existem parâmetros válidos nos dados NASA."
        )

    # Obter as datas disponíveis
    first_parameter = next(iter(parameters.values()))

    if not isinstance(first_parameter, dict):
        raise ValueError(
            "Estrutura diária dos parâmetros inválida."
        )

    dates = sorted(first_parameter.keys())

    cleaned_data = []

    # Percorrer cada dia
    for current_date in dates:

        daily_record = {
            "date": current_date
        }

        # Percorrer cada variável climática
        for variable, daily_values in parameters.items():

            value = daily_values.get(current_date)

            daily_record[variable] = clean_value(
                value,
                fill_value
            )

        cleaned_data.append(daily_record)

    return cleaned_data


# ==================================================
# 5. GUARDAR OS DADOS LIMPOS
# ==================================================

def save_cleaned_data(raw_file):
    """
    Carrega, limpa e guarda os dados num novo ficheiro.
    O ficheiro original permanece inalterado.
    """

    raw_file = Path(raw_file)

    # Carregar dados originais
    raw_data = load_raw_data(raw_file)

    # Limpar dados
    cleaned_data = clear_parameters(raw_data)

    # Criar pasta de destino
    PROCESSED_DATA_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )

    # Construir nome do ficheiro
    filename = raw_file.stem + "_cleaned.json"

    output_file = PROCESSED_DATA_FOLDER / filename

    # Guardar dados limpos
    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            cleaned_data,
            file,
            ensure_ascii=False,
            indent=4,
            allow_nan=False
        )

    print("\nDados limpos guardados com sucesso!")
    print(f"Ficheiro: {output_file}")

    return output_file

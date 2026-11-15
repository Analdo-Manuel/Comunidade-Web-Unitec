
import json
from pathlib import Path

from src.nasa.nasa_client import get_daily_data


# Identificar a raiz do projecto
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Pasta onde serão guardados os dados originais
RAW_DATA_FOLDER = PROJECT_ROOT / "data" / "raw" / "nasa"


def collect_nasa_data(
    field_id: str,
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str
):
    # 1. Consultar a NASA POWER
    print("A recolher dados da NASA POWER...")

    data = get_daily_data(
        latitude=latitude,
        longitude=longitude,
        start_date=start_date,
        end_date=end_date
    )

    # 2. Criar a pasta de destino, caso não exista
    RAW_DATA_FOLDER.mkdir(parents=True, exist_ok=True)

    # 3. Preparar um identificador seguro para o nome do ficheiro
    safe_field_id = "".join(
        char for char in field_id
        if char.isalnum() or char in ("-", "_")
    )

    if not safe_field_id:
        raise ValueError("Identificador da machamba inválido.")

    # 4. Construir o nome do ficheiro
    filename = (
        f"nasa_{safe_field_id}_"
        f"{start_date}_{end_date}.json"
    )

    output_file = RAW_DATA_FOLDER / filename

    # 5. Guardar a resposta original da NASA
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=4
        )

    print("\nRecolha concluída com sucesso!")
    print(f"Ficheiro guardado em: {output_file}")

    return output_file

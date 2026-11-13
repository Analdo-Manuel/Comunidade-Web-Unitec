
import json
from pathlib import Path

from src.nasa.nasa_client import get_daily_data


# Identificar a raiz do projecto
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Localização do ficheiro de configuração
LOCATION_FILE = PROJECT_ROOT / "data" / "input" / "location.json"

# Pasta onde serão guardados os dados originais
RAW_DATA_FOLDER = PROJECT_ROOT / "data" / "raw" / "nasa"


def collect_nasa_data():

    # 1. Ler a configuração da machamba
    with open(LOCATION_FILE, "r", encoding="utf-8") as file:
        config = json.load(file)

    location = config["location"]
    period = config["analysis_period"]

    # 2. Consultar a NASA POWER
    print("A recolher dados da NASA POWER...")

    data = get_daily_data(
        latitude=location["latitude"],
        longitude=location["longitude"],
        start_date=period["start_date"],
        end_date=period["end_date"]
    )

    # 3. Criar a pasta de destino, caso não exista
    RAW_DATA_FOLDER.mkdir(parents=True, exist_ok=True)

    # 4. Construir o nome do ficheiro
    filename = (
        f"nasa_{config['field_id']}_"
        f"{period['start_date']}_"
        f"{period['end_date']}.json"
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


if __name__ == "__main__":
    collect_nasa_data()

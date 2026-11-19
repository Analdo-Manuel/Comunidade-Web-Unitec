
import json
import hashlib
import time
import math
from pathlib import Path

from src.nasa.nasa_client import get_daily_data


PROJECT_ROOT = Path(__file__).resolve().parents[2]

CACHE_FOLDER = PROJECT_ROOT / "data" / "cache" / "nasa"

CACHE_TTL = 7 * 24 * 60 * 60  # 7 dias

CACHE_RADIUS_KM = 5


def calculate_distance_km(lat1, lon1, lat2, lon2):
    """
    Calcula a distância entre duas coordenadas geográficas.
    Resultado em quilómetros.
    """

    earth_radius = 6371

    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(delta_lon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return earth_radius * c


def find_cached_data(latitude, longitude, start_date, end_date):

    CACHE_FOLDER.mkdir(parents=True, exist_ok=True)

    current_time = time.time()
    candidates = []

    metadata_files = CACHE_FOLDER.glob("*.meta.json")

    for metadata_file in metadata_files:

        try:
            with open(metadata_file, "r", encoding="utf-8") as file:
                metadata = json.load(file)

            # O período tem de ser exactamente igual
            if (
                metadata["start_date"] != start_date
                or metadata["end_date"] != end_date
            ):
                continue

            raw_filename = metadata_file.name.replace(
                ".meta.json", ".json"
            )

            raw_file = metadata_file.with_name(raw_filename)

            if not raw_file.exists():
                continue

            # Verificar validade do cache
            file_age = current_time - raw_file.stat().st_mtime

            if file_age < 0 or file_age >= CACHE_TTL:
                print(f"Cache expirado. A eliminar: {raw_file.name}")

                # Eliminar ficheiro de dados
                raw_file.unlink(missing_ok=True)

                # Eliminar ficheiro de metadados
                metadata_file.unlink(missing_ok=True)
                continue

            # Calcular distância entre as localizações
            distance = calculate_distance_km(
                latitude,
                longitude,
                metadata["latitude"],
                metadata["longitude"]
            )

            if distance <= CACHE_RADIUS_KM:
                candidates.append(
                    (distance, raw_file)
                )

        except (OSError, ValueError, KeyError, TypeError):
            continue

    # Escolher o cache geograficamente mais próximo
    if candidates:
        distance, raw_file = min(
            candidates,
            key=lambda candidate: candidate[0]
        )

        print("Cache encontrado!")
        print(f"Distância da localização original: {distance:.2f} km")

        return raw_file

    return None


def collect_nasa_data(
    field_id: str,
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str
):

    print("A verificar o cache da NASA POWER...")

    # Procurar dados num raio de 5 km
    cached_file = find_cached_data(
        latitude=latitude,
        longitude=longitude,
        start_date=start_date,
        end_date=end_date
    )

    if cached_file:
        print("A reutilizar dados guardados.")
        return cached_file

    print("Cache não encontrado. A consultar NASA POWER...")

    # Criar identificador único para esta localização e período
    cache_key = (
        f"{latitude}|{longitude}|"
        f"{start_date}|{end_date}"
    )

    cache_hash = hashlib.sha256(
        cache_key.encode("utf-8")
    ).hexdigest()

    cache_file = CACHE_FOLDER / f"nasa_{cache_hash}.json"

    metadata_file = CACHE_FOLDER / (
        f"nasa_{cache_hash}.meta.json"
    )

    # Consultar NASA POWER
    data = get_daily_data(
        latitude=latitude,
        longitude=longitude,
        start_date=start_date,
        end_date=end_date
    )

    # Guardar dados brutos
    with open(cache_file, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=4
        )

    # Guardar informações necessárias para localizar o cache
    metadata = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date
    }

    with open(metadata_file, "w", encoding="utf-8") as file:
        json.dump(
            metadata,
            file,
            ensure_ascii=False,
            indent=4
        )

    print("Dados guardados no cache com sucesso!")

    return cache_file

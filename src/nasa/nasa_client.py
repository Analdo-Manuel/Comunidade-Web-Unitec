
import requests
from datetime import datetime


# Endereço principal da API NASA POWER
NASA_API_URL = (
    "https://power.larc.nasa.gov/api/temporal/daily/point"
)


def format_date(date: str) -> str:
    """
    Converte uma data YYYY-MM-DD para YYYYMMDD,
    formato exigido pela NASA POWER.
    """

    parsed_date = datetime.strptime(date, "%Y-%m-%d")

    return parsed_date.strftime("%Y%m%d")


def get_daily_data( latitude: float, longitude: float, start_date: str, end_date: str ) -> dict:
    """
    Consulta os dados climáticos diários da NASA POWER.

    Recebe:
        latitude
        longitude
        data inicial
        data final

    Devolve:
        Resposta da NASA em formato JSON.
    """

    parameters = {
        "parameters": "PRECTOTCORR,T2M,T2M_MAX,T2M_MIN,RH2M",
        "community": "AG",
        "longitude": longitude,
        "latitude": latitude,
        "start": format_date(start_date),
        "end": format_date(end_date),
        "format": "JSON",
        "time-standard": "UTC"
    }

    try:
        response = requests.get(
            NASA_API_URL,
            params=parameters,
            timeout=30
        )

        # Verifica se o pedido HTTP foi bem-sucedido
        response.raise_for_status()

        # Converte a resposta para um dicionário Python
        data = response.json()

        # Confirma se a resposta contém os dados esperados
        if "properties" not in data or "parameter" not in data["properties"]:
            raise ValueError(
                "A resposta da NASA não contém os dados esperados."
            )

        return data

    except requests.exceptions.RequestException as error:
        raise RuntimeError(
            f"Erro ao comunicar com a NASA POWER: {error}"
        ) from error

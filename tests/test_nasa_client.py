
import json
from pathlib import Path

from src.nasa.nasa_client import get_daily_data


# Localizar a raiz do projecto
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Caminho do ficheiro de localização
LOCATION_FILE = PROJECT_ROOT / "data" / "input" / "location.json"

def data_organizer(data: str) -> str:
    """
    Função auxiliar para organizar a data no formato YYYY-MM-DD. 
    """
    return f"{data[:4]}-{data[4:6]}-{data[6:]}"


def main():

    # 1. Ler a localização e o período
    with open(LOCATION_FILE, "r", encoding="utf-8") as file: location_data = json.load(file)

    location = location_data["location"]
    period = location_data["analysis_period"]

    print("\nA consultar a NASA POWER...")

    # 2. Consultar a API
    data = get_daily_data(
        latitude=location["latitude"],
        longitude=location["longitude"],
        start_date=period["start_date"],
        end_date=period["end_date"]
    )

    # 3. Extrair os dados recebidos
    
    parameters = data["properties"]["parameter"]

    # 4. Mostrar o resultado
    print("\nCONEXÃO COM NASA POWER: SUCESSO")

    print(f"Localização: {location_data['field_name']}")
    print(f"Latitude: {location['latitude']}")
    print(f"Longitude: {location['longitude']}")

    print("\nVariáveis recebidas:")

    for variable, daily_values in parameters.items():
        print(f"- {variable}: {len(daily_values)} registos")

    precipitation = parameters["PRECTOTCORR"]
    Temperatura = parameters["T2M"]
    Temperatura_Max = parameters["T2M_MAX"]
    Temperatura_Min = parameters["T2M_MIN"]

    print("\nPrimeiros valores de precipitação:")

    for date, value in list(precipitation.items())[:2]:
        print(f"Data: {data_organizer(date)} | Valuer: {value} mm")
        
    print("\nPrimeiros valores de Temperatura:")

    for date, value in list(Temperatura.items())[:2]:
        print(f"Data: {data_organizer(date)} | Valuer: {value} C°")
    
    print("\nPrimeiros valores de Temperatura_Max:")

    for date, value in list(Temperatura_Max.items())[:2]:
        print(f"Data: {data_organizer(date)} | Valuer: {value} C°")
        
    print("\nPrimeiros valores de Temperatura_Min:")
    
    for date, value in list(Temperatura_Min.items())[:2]:
        print(f"Data: {data_organizer(date)} | Valuer: {value} C°")


if __name__ == "__main__":
    main()
    


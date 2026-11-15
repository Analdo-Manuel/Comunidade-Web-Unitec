import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

LOCATION_FILE = (
    PROJECT_ROOT / "data" / "input" / "location.json"
)

PROCESSED_DATA_FOLDER = (
    PROJECT_ROOT / "data" / "processed" / "nasa"
)

PROCESSED_DATA_FOLDER_1 = (
    PROJECT_ROOT / "data" / "processed" / "climate"
)

def load_location_config():
    with open(LOCATION_FILE, "r", encoding="utf-8") as file:
        config = json.load(file)

    return config

def load_cleaned_data(config=None):
    if config is None:
        config = load_location_config()
  
    period = config["analysis_period"]
    
    # Construir o nome do ficheiro
    filename = (
        f"nasa_{config['field_id']}_"
        f"{period['start_date']}_"
        f"{period['end_date']}_cleaned.json"
    )

    processed_file =  PROCESSED_DATA_FOLDER / filename
    
    with open(processed_file, "r", encoding="utf-8") as file:
        data = json.load(file)
        
    return data

def calculate_total_precipitation(data: dict) -> dict:
    """
    Função auxiliar para calcular a soma total de uma variável climática.
    """
    
    total = 0.0
    days_with_data = 0
    days_without_data = 0

    for record in data:
        value = record.get("PRECTOTCORR")

        if value is not None:
            total += value
            days_with_data += 1
        else:
            days_without_data += 1

    return {
        f"Total_Precipitation": total,
        f"Days_with_data": days_with_data,
        f"Days_without_data": days_without_data
    }
    
def calculate_average_temperature(data: dict) -> dict:
    """
    Função auxiliar para calcular a média de uma variável climática.
    """

    total = 0.0
    days_with_data = 0
    days_without_data = 0

    for record in data:
        value = record.get("T2M")

        if value is not None:
            total += value
            days_with_data += 1
        else:
            days_without_data += 1

    average = total / days_with_data if days_with_data > 0 else None

    return {
        f"Average_Temperature": round(average, 2) if average is not None else None,
        f"Days_with_data": days_with_data,
        f"Days_without_data": days_without_data
    }
    
def calculate_temperature_extremes(data: dict) -> dict:
    """
    Função auxiliar para calcular os extremos de temperatura.
    """

    max_temp = []
    min_temp = []

    for record in data:
        min_value = record.get("T2M_MIN")
        max_value = record.get("T2M_MAX")

        if min_value is not None:
            min_temp.append(min_value)
        if max_value is not None:
            max_temp.append(max_value)
            
    lowest_temp = min(min_temp) if min_temp else None
    highest_temp = max(max_temp) if max_temp else None

    return {
        f"Max_Temperature": highest_temp,
        f"Min_Temperature": lowest_temp,
        f"Days_with_min_data": len(min_temp),
        f"Days_with_max_data": len(max_temp)
    }
    
def calculate_average_humidity(data: dict) -> dict:
    """
    Função auxiliar para calcular a média de uma variável climática.
    """

    total = 0.0
    days_with_data = 0
    days_without_data = 0

    for record in data:
        value = record.get("RH2M")

        if value is not None:
            total += value
            days_with_data += 1
        else:
            days_without_data += 1

    average = total / days_with_data if days_with_data > 0 else None

    return {
        f"Average_Humidity": round(average, 2) if average is not None else None,
        f"Days_with_data": days_with_data,
        f"Days_without_data": days_without_data
    }
    
def calculate_rainy_days(data: dict) -> dict:
    """
    Função auxiliar para calcular o número de dias chuvosos.
    """

    rainy_days_count = 0
    days_without_rain = 0
    days_without_data = 0

    for record in data:
        value = record.get("PRECTOTCORR")

        if value is not None:
            if value > 0:
                rainy_days_count += 1
            else:
                days_without_rain += 1
        else:
            days_without_data += 1

    return {
        f"Rainy_Days": rainy_days_count,
        f"Days_without_rain": days_without_rain,
        f"Days_without_data": days_without_data
    }
    
def analyze_climate(data: dict) -> dict:
    """
    Função principal para analisar os dados climáticos.
    """
    
    precipitation_summary = calculate_total_precipitation(data)
    temperature_summary = calculate_average_temperature(data)
    temperature_extremes = calculate_temperature_extremes(data)
    humidity_summary = calculate_average_humidity(data)
    rainy_summary = calculate_rainy_days(data)

    return {
        "Precipitation": precipitation_summary,
        "Temperature": temperature_summary,
        "Temperature_Extremes": temperature_extremes,
        "Humidity": humidity_summary,
        "Rainy_Days": rainy_summary
    }
    
def save_climate_analysis(): 
    config = load_location_config()
    
    data = load_cleaned_data(config)
    
    climate_results = analyze_climate(data)
    
    result = {
        "field": {
            "field_id": config["field_id"],
            "field_name": config["field_name"]
        },
        
        "location": config["location"],
        "analysis_period": config["analysis_period"],
        "climate_indicators": climate_results
    }
    
    # Construir o nome do ficheiro
    filename = (
        f"climate_{config['field_id']}_"
        f"{config['analysis_period']['start_date']}_"
        f"{config['analysis_period']['end_date']}.json"
    )
    
    output_file = PROCESSED_DATA_FOLDER_1 / filename
    
    PROCESSED_DATA_FOLDER_1.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=4)
        
    print(f"\nANALISE CLIMATICA CONCLUIDA COM SUCESSO!")
    print(f"Fazenda: {config['field_name']}")
    print(f"Ficheiro guardado em: {output_file}")

if __name__ == "__main__":
    save_climate_analysis()
import json
from pathlib import Path
from datetime import datetime, timezone


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
    
def calculate_data_coverage(data):
    total_days = len(data)
    
    variables = ["PRECTOTCORR", "T2M", "T2M_MAX", "T2M_MIN", "RH2M"]
    
    coverage = {}
    
    for variable in variables:
        available_days = sum(1 for record in data if record.get(variable) is not None)
        
        missing_days = total_days - available_days
        
        percentage = (available_days / total_days) * 100 if total_days > 0 else 0
        
        coverage[variable] = {
            "available_days": available_days,
            "missing_days": missing_days,
            "coverage_percentage": round(percentage, 2)
        }

    return {
        "total_days": total_days,
        "variables_coverage": coverage
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

    # Carregar dados limpos
    data = load_cleaned_data(config)

    # Executar análise climática
    climate_results = analyze_climate(data)

    # Identificar o período analisado
    period = config["analysis_period"]

    start_date = datetime.strptime(
        period["start_date"], "%Y-%m-%d"
    )

    end_date = datetime.strptime(
        period["end_date"], "%Y-%m-%d"
    )

    expected_days = (end_date - start_date).days + 1

    # Obter os contadores já calculados pelos indicadores
    precipitation = climate_results["Precipitation"]
    temperature = climate_results["Temperature"]
    temperature_extremes = climate_results["Temperature_Extremes"]
    humidity = climate_results["Humidity"]

    # Organizar a qualidade dos dados por variável
    variables_quality = {
        "PRECTOTCORR": {
            "available_days": precipitation["Days_with_data"],
            "missing_days": precipitation["Days_without_data"]
        },
        "T2M": {
            "available_days": temperature["Days_with_data"],
            "missing_days": temperature["Days_without_data"]
        },
        "T2M_MAX": {
            "available_days": temperature_extremes["Days_with_max_data"],
            "missing_days": expected_days - temperature_extremes["Days_with_max_data"]
        },
        "T2M_MIN": {
            "available_days": temperature_extremes["Days_with_min_data"],
            "missing_days": expected_days - temperature_extremes["Days_with_min_data"]
        },
        "RH2M": {
            "available_days": humidity["Days_with_data"],
            "missing_days": humidity["Days_without_data"]
        }
    }

    # Calcular a cobertura de cada variável
    for variable, quality in variables_quality.items():
        available = quality["available_days"]

        quality["coverage_percentage"] = round(
            (available / expected_days) * 100,
            2
        ) if expected_days > 0 else 0

    # Determinar o estado geral da qualidade dos dados
    coverage_values = [
        item["coverage_percentage"]
        for item in variables_quality.values()
    ]

    if all(value == 100 for value in coverage_values):
        quality_status = "complete"
    elif any(value > 0 for value in coverage_values):
        quality_status = "partial"
    else:
        quality_status = "unavailable"

    # Construir resposta padronizada
    result = {
        "api": {
            "name": "Agro Intelligence",
            "version": "1.0.0"
        },

        "metadata": {
            "source": "NASA POWER",
            "temporal_resolution": "daily",
            "time_standard": "UTC",
            "generated_at": datetime.now(timezone.utc).isoformat()
        },

        "location": config["location"],

        "analysis_period": {
            "start_date": period["start_date"],
            "end_date": period["end_date"],
            "total_days": expected_days
        },

        "data_quality": {
            "status": quality_status,
            "expected_days": expected_days,
            "variables": variables_quality
        },

        "indicators": {
            "precipitation": {
                "total": precipitation["Total_Precipitation"],
                "unit": "mm",
                "days_with_data": precipitation["Days_with_data"],
                "days_without_data": precipitation["Days_without_data"]
            },

            "temperature": {
                "average": temperature["Average_Temperature"],
                "highest": temperature_extremes["Max_Temperature"],
                "lowest": temperature_extremes["Min_Temperature"],
                "unit": "°C"
            },

            "humidity": {
                "average": humidity["Average_Humidity"],
                "unit": "%"
            },

            "rainfall": {
                "rainy_days": climate_results["Rainy_Days"]["Rainy_Days"],
                "days_without_rain": climate_results["Rainy_Days"]["Days_without_rain"],
                "days_without_data": climate_results["Rainy_Days"]["Days_without_data"]
            }
        }
    }

    # Guardar resultado
    filename = (
        f"climate_{config['field_id']}_"
        f"{period['start_date']}_"
        f"{period['end_date']}.json"
    )

    output_file = PROCESSED_DATA_FOLDER_1 / filename

    PROCESSED_DATA_FOLDER_1.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(
            result,
            file,
            ensure_ascii=False,
            indent=4,
            allow_nan=False
        )

    print("\nANÁLISE CLIMÁTICA CONCLUÍDA!")
    print(f"Localização: {config['location']}")
    print(f"Período: {period['start_date']} até {period['end_date']}")
    print(f"Qualidade dos dados: {quality_status}")
    print(f"Ficheiro guardado em: {output_file}")

    return output_file

if __name__ == "__main__":
    save_climate_analysis()
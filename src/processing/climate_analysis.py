
import json
from pathlib import Path
from datetime import datetime, date, timedelta, timezone


# ==================================================
# 1. CONFIGURAÇÕES
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DATA_FOLDER = (
    PROJECT_ROOT / "data" / "processed" / "climate"
)


# ==================================================
# 2. GERAR O CALENDÁRIO DO PERÍODO
# ==================================================

def generate_analysis_dates(start_date, end_date):

    start = datetime.strptime(
        start_date, "%Y-%m-%d"
    ).date()

    end = datetime.strptime(
        end_date, "%Y-%m-%d"
    ).date()

    if start > end:
        raise ValueError(
            "A data inicial não pode ser posterior à data final."
        )

    dates = []
    current_date = start

    while current_date <= end:

        dates.append(
            current_date.strftime("%Y%m%d")
        )

        current_date += timedelta(days=1)

    return dates


# ==================================================
# 3. CALCULAR PRECIPITAÇÃO
# ==================================================

def calculate_total_precipitation(data, expected_days):

    total = 0.0
    days_with_data = 0

    for record in data:

        value = record.get("PRECTOTCORR")

        if value is not None:
            total += value
            days_with_data += 1

    days_without_data = expected_days - days_with_data

    return {
        "Total_Precipitation": round(total, 2) if days_with_data > 0 else None,
        "Days_with_data": days_with_data,
        "Days_without_data": days_without_data
    }


# ==================================================
# 4. CALCULAR TEMPERATURA MÉDIA
# ==================================================

def calculate_average_temperature(data, expected_days):

    total = 0.0
    days_with_data = 0

    for record in data:

        value = record.get("T2M")

        if value is not None:
            total += value
            days_with_data += 1

    average = (
        total / days_with_data
        if days_with_data > 0
        else None
    )

    return {
        "Average_Temperature": round(average, 2) if average is not None else None,
        "Days_with_data": days_with_data,
        "Days_without_data": expected_days - days_with_data
    }


# ==================================================
# 5. CALCULAR EXTREMOS DE TEMPERATURA
# ==================================================

def calculate_temperature_extremes(data):

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
        "Max_Temperature": highest_temp,
        "Min_Temperature": lowest_temp,
        "Days_with_min_data": len(min_temp),
        "Days_with_max_data": len(max_temp)
    }


# ==================================================
# 6. CALCULAR HUMIDADE MÉDIA
# ==================================================

def calculate_average_humidity(data, expected_days):

    total = 0.0
    days_with_data = 0

    for record in data:

        value = record.get("RH2M")

        if value is not None:
            total += value
            days_with_data += 1

    average = (
        total / days_with_data
        if days_with_data > 0
        else None
    )

    return {
        "Average_Humidity": round(average, 2) if average is not None else None,
        "Days_with_data": days_with_data,
        "Days_without_data": expected_days - days_with_data
    }


# ==================================================
# 7. CALCULAR DIAS CHUVOSOS
# ==================================================

def calculate_rainy_days(data, expected_days):

    rainy_days_count = 0
    days_without_rain = 0
    days_with_data = 0

    for record in data:

        value = record.get("PRECTOTCORR")

        if value is not None:

            days_with_data += 1

            if value > 0:
                rainy_days_count += 1

            else:
                days_without_rain += 1

    days_without_data = expected_days - days_with_data

    return {
        "Rainy_Days": rainy_days_count,
        "Days_without_rain": days_without_rain,
        "Days_without_data": days_without_data
    }


# ==================================================
# 8. EXECUTAR ANÁLISE CLIMÁTICA
# ==================================================

def analyze_climate(data, expected_days):

    precipitation_summary = calculate_total_precipitation(
        data, expected_days
    )

    temperature_summary = calculate_average_temperature(
        data, expected_days
    )

    temperature_extremes = calculate_temperature_extremes(data)

    humidity_summary = calculate_average_humidity(
        data, expected_days
    )

    rainy_summary = calculate_rainy_days(
        data, expected_days
    )

    return {
        "Precipitation": precipitation_summary,
        "Temperature": temperature_summary,
        "Temperature_Extremes": temperature_extremes,
        "Humidity": humidity_summary,
        "Rainy_Days": rainy_summary
    }


# ==================================================
# 9. PREPARAR A ANÁLISE COMPLETA
# ==================================================

def build_climate_result(
    data,
    field_id,
    field_name,
    location,
    start_date,
    end_date
):

    # Gerar calendário esperado
    expected_dates = generate_analysis_dates(
        start_date,
        end_date
    )

    expected_dates_set = set(expected_dates)
    expected_days = len(expected_dates)

    # Verificar estrutura dos dados limpos
    if not isinstance(data, list):
        raise ValueError(
            "Os dados limpos devem estar organizados numa lista."
        )

    # Utilizar apenas registos dentro do período solicitado
    filtered_data = [
        record for record in data
        if record.get("date") in expected_dates_set
    ]

    # Executar cálculos
    climate_results = analyze_climate(
        filtered_data,
        expected_days
    )

    precipitation = climate_results["Precipitation"]
    temperature = climate_results["Temperature"]
    temperature_extremes = climate_results["Temperature_Extremes"]
    humidity = climate_results["Humidity"]

    # Organizar qualidade dos dados
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

    # Calcular cobertura de cada variável
    for variable, quality in variables_quality.items():

        available = quality["available_days"]

        quality["coverage_percentage"] = round(
            (available / expected_days) * 100,
            2
        ) if expected_days > 0 else 0

    # Determinar qualidade geral
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

        "field": {
            "field_id": field_id,
            "field_name": field_name
        },

        "metadata": {
            "source": "NASA POWER",
            "temporal_resolution": "daily",
            "time_standard": "UTC",
            "generated_at": datetime.now(timezone.utc).isoformat()
        },

        "location": location,

        "analysis_period": {
            "start_date": start_date,
            "end_date": end_date,
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

    return result


# ==================================================
# 10. GUARDAR RESULTADO DA ANÁLISE
# ==================================================

def save_climate_analysis(
    cleaned_file,
    field_id,
    field_name,
    location,
    start_date,
    end_date
):

    cleaned_file = Path(cleaned_file)

    if not cleaned_file.exists():
        raise FileNotFoundError(
            f"Ficheiro limpo não encontrado: {cleaned_file}"
        )

    # Carregar dados limpos
    with open(
        cleaned_file,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    # Construir resultado climático
    result = build_climate_result(
        data=data,
        field_id=field_id,
        field_name=field_name,
        location=location,
        start_date=start_date,
        end_date=end_date
    )

    # Criar identificador seguro para o nome do ficheiro
    safe_field_id = "".join(
        char for char in field_id
        if char.isalnum() or char in ("-", "_")
    )

    if not safe_field_id:
        raise ValueError(
            "Identificador da machamba inválido."
        )

    # Construir nome do ficheiro
    filename = (
        f"climate_{safe_field_id}_"
        f"{start_date}_{end_date}.json"
    )

    output_file = PROCESSED_DATA_FOLDER / filename

    # Criar pasta de destino
    PROCESSED_DATA_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )

    # Guardar resultado
    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            result,
            file,
            ensure_ascii=False,
            indent=4,
            allow_nan=False
        )

    print("\nANÁLISE CLIMÁTICA CONCLUÍDA!")
    print(f"Machamba: {field_name}")
    print(f"Período: {start_date} até {end_date}")
    print(f"Qualidade dos dados: {result['data_quality']['status']}")
    print(f"Ficheiro guardado em: {output_file}")

    # Devolver os resultados para a API
    return result
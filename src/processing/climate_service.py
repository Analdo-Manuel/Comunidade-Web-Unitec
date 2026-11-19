
from src.nasa.data_collector import collect_nasa_data
from src.processing.data_validation import validate_nasa_data
from src.processing.data_cleaning import save_cleaned_data
from src.processing.climate_analysis import save_climate_analysis


def run_climate_analysis(
    field_id: str,
    field_name: str,
    location: dict,
    start_date: str,
    end_date: str
) -> dict:

    # 1. Recolher dados da NASA
    raw_file = collect_nasa_data(
        field_id=field_id,
        latitude=location["latitude"],
        longitude=location["longitude"],
        start_date=start_date,
        end_date=end_date
    )

    # 2. Validar os dados recolhidos
    validation = validate_nasa_data(
        raw_file=raw_file,
        start_date=start_date,
        end_date=end_date,
        field_name=field_name
    )

    # 3. Interromper se existirem erros
    if validation["status"] == "error":
        raise ValueError(
            "Os dados recolhidos não passaram na validação."
        )

    # 4. Limpar os dados
    cleaned_file = save_cleaned_data(raw_file)

    # 5. Calcular os indicadores climáticos
    result = save_climate_analysis(
        cleaned_file=cleaned_file,
        field_id=field_id,
        field_name=field_name,
        location=location,
        start_date=start_date,
        end_date=end_date
    )

    return result

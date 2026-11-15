import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

LOCATION_FILE = (
    PROJECT_ROOT / "data" / "input" / "location.json"
)

RAW_DATA_FOLDER = (
    PROJECT_ROOT / "data" / "raw" / "nasa"
)

PROCESSED_DATA_FOLDER = (
    PROJECT_ROOT / "data" / "processed" / "nasa"
)

def get_raw_file():
    """
    Função auxiliar para obter o caminho do ficheiro de dados brutos da NASA.
    """

    # Ler a configuração da machamba
    with open(LOCATION_FILE, "r", encoding="utf-8") as file:
        config = json.load(file)

    period = config["analysis_period"]

    # Construir o nome do ficheiro
    filename = (
        f"nasa_{config['field_id']}_"
        f"{period['start_date']}_"
        f"{period['end_date']}.json"
    )

    return RAW_DATA_FOLDER / filename

def load_raw_data():

    raw_file = get_raw_file()

    with open( raw_file, "r", encoding="utf-8" ) as file:
        data = json.load(file)

    return data

def clear_valuer(value, fill_value):
    """
    Função auxiliar para limpar os valores recebidos da NASA.

    Se o valor for igual a fill_value, retorna None.
    """

    if value == fill_value:
        return None

    return value

def clear_parameters(data: dict):
    
    parameters = data.get("properties", {}).get("parameter", {})
    fill_value = data.get("properties", {}).get("fill_value", -999)
    
    cleaned_data = []
    
    first_parameter = next(iter(parameters.values())) # Acessa o primeiro valor do dicionário
    datas = first_parameter.keys() # Obtém as datas do primeiro parâmetro
    
    for data in datas:
        
        daily_record = { "data": data }
        
        for variavel, daily_valuers in parameters.items():
            valuer = daily_valuers.get(data)
            
            daily_record[variavel] = clear_valuer(valuer, fill_value)
        
        cleaned_data.append(daily_record)   

    return cleaned_data

def save_cleaned_data():
    """
    Função auxiliar para guardar os dados limpos num ficheiro JSON.
    """
    
    # Dados Limpos
    cleaned_data = clear_parameters(load_raw_data())
    
    # Criar a pasta de destino, caso não exista
    PROCESSED_DATA_FOLDER.mkdir(parents=True, exist_ok=True)

    # Construir o nome do ficheiro
    raw_file = get_raw_file()
    filename = raw_file.name.replace(".json", "_cleaned.json")
    output_file = PROCESSED_DATA_FOLDER / filename

    # Guardar os dados limpos
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(
            cleaned_data,
            file,
            ensure_ascii=False,
            indent=4
        )

    print(f"\nDados limpos guardados em: {output_file}")
    
    return output_file

if __name__ == "__main__":
    save_cleaned_data()

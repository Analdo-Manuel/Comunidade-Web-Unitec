
import json
import math
from pathlib import Path
from datetime import datetime, timedelta


# ==================================================
# 1. CONFIGURAÇÕES
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

LOCATION_FILE = (
    PROJECT_ROOT / "data" / "input" / "location.json"
)

RAW_DATA_FOLDER = (
    PROJECT_ROOT / "data" / "raw" / "nasa"
)

EXPECTED_PARAMETERS = [
    "PRECTOTCORR",
    "T2M",
    "T2M_MAX",
    "T2M_MIN",
    "RH2M"
]


# ==================================================
# 2. GERAR AS DATAS ESPERADAS
# ==================================================

def generate_expected_dates(start_date, end_date):

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
# 3. VALIDAR OS DADOS
# ==================================================

def validate_nasa_data():

    errors = 0
    warnings = 0

    # Ler a configuração da machamba
    with open(LOCATION_FILE, "r", encoding="utf-8") as file:
        config = json.load(file)

    period = config["analysis_period"]

    # Construir o nome do ficheiro NASA
    filename = (
        f"nasa_{config['field_id']}_"
        f"{period['start_date']}_"
        f"{period['end_date']}.json"
    )

    raw_file = RAW_DATA_FOLDER / filename

    if not raw_file.exists():

        raise FileNotFoundError(
            f"Ficheiro não encontrado: {raw_file}"
        )

    # Ler os dados originais
    with open(
        raw_file,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    print("\n======================================")
    print("       AGRO INTELLIGENCE")
    print("          NASA DATA VALIDATION")
    print("======================================")

    print(f"\nMachamba: {config['field_name']}")
    print(f"Ficheiro: {filename}")

    # Verificar estrutura principal
    if not isinstance(data, dict):
        raise ValueError("O JSON não contém um objecto válido.")

    properties = data.get("properties", {})
    parameters = properties.get("parameter", {})

    if not isinstance(parameters, dict):
        raise ValueError(
            "Estrutura de parâmetros inválida."
        )

    header = data.get("header", {})
    fill_value = header.get("fill_value", -999)

    # Gerar calendário esperado
    expected_dates = generate_expected_dates(
        period["start_date"],
        period["end_date"]
    )

    print(f"\nPeríodo: {period['start_date']} até {period['end_date']}")
    print(f"Dias esperados: {len(expected_dates)}")
    print(f"Valor de preenchimento: {fill_value}")

    # Verificar cada variável
    for variable in EXPECTED_PARAMETERS:

        print(f"\n--- {variable} ---")

        if variable not in parameters:

            print("[ERRO] Variável não encontrada.")
            errors += 1
            continue

        daily_values = parameters[variable]

        if not isinstance(daily_values, dict):

            print("[ERRO] Estrutura diária inválida.")
            errors += 1
            continue

        received_dates = set(daily_values.keys())
        expected_dates_set = set(expected_dates)

        # Datas que deveriam existir, mas não existem
        missing_dates = (
            expected_dates_set - received_dates
        )

        # Datas recebidas fora do período solicitado
        unexpected_dates = (
            received_dates - expected_dates_set
        )

        missing_values = 0
        invalid_values = 0

        # Analisar cada valor recebido
        for value in daily_values.values():

            if value == fill_value:
                missing_values += 1

            elif (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
            ):
                invalid_values += 1

        print(f"Registos recebidos: {len(daily_values)}")
        print(f"Datas em falta: {len(missing_dates)}")
        print(f"Datas inesperadas: {len(unexpected_dates)}")
        print(f"Valores ausentes: {missing_values}")
        print(f"Valores inválidos: {invalid_values}")

        # Classificar os resultados
        if missing_dates:
            print("[AVISO] Existem datas sem registos.")
            warnings += 1

        if unexpected_dates:
            print("[AVISO] Existem datas fora do período.")
            warnings += 1

        if missing_values:
            print("[AVISO] Existem valores de preenchimento.")
            warnings += 1

        if invalid_values:
            print("[ERRO] Existem valores inválidos.")
            errors += 1

        if (
            not missing_dates
            and not unexpected_dates
            and not missing_values
            and not invalid_values
        ):
            print("[OK] Variável validada.")

    # Resultado final
    print("\n======================================")
    print("             RESULTADO")
    print("======================================")

    print(f"Total de erros: {errors}")
    print(f"Total de avisos: {warnings}")

    if errors > 0:

        print("\nRESULTADO: EXISTEM ERROS.")

    elif warnings > 0:

        print("\nRESULTADO: EXISTEM AVISOS.")

    else:

        print("\nRESULTADO: DADOS VALIDADOS COM SUCESSO.")

    print("\nO ficheiro original permanece inalterado.")


# ==================================================
# 4. EXECUTAR O PROGRAMA
# ==================================================

if __name__ == "__main__":

    validate_nasa_data()

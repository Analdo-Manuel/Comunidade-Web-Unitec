
import json
import math
from pathlib import Path
from datetime import datetime, timedelta


# ==================================================
# 1. CONFIGURAÇÕES
# ==================================================

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
# 3. VALIDAR OS DADOS NASA
# ==================================================

def validate_nasa_data(
    raw_file,
    start_date,
    end_date,
    field_name="Não identificado"
):

    # Converter o caminho recebido para Path
    raw_file = Path(raw_file)

    errors = 0
    warnings = 0

    variable_results = {}

    # Verificar se o ficheiro existe
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

    print(f"\nMachamba: {field_name}")
    print(f"Ficheiro: {raw_file.name}")

    # Verificar estrutura principal
    if not isinstance(data, dict):
        raise ValueError(
            "O JSON não contém um objecto válido."
        )

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
        start_date,
        end_date
    )

    print(
        f"\nPeríodo: {start_date} até {end_date}"
    )

    print(f"Dias esperados: {len(expected_dates)}")
    print(f"Valor de preenchimento: {fill_value}")

    expected_dates_set = set(expected_dates)

    # Verificar cada variável
    for variable in EXPECTED_PARAMETERS:

        print(f"\n--- {variable} ---")

        if variable not in parameters:

            print("[ERRO] Variável não encontrada.")

            errors += 1

            variable_results[variable] = {
                "status": "error",
                "reason": "Variável não encontrada."
            }

            continue

        daily_values = parameters[variable]

        if not isinstance(daily_values, dict):

            print("[ERRO] Estrutura diária inválida.")

            errors += 1

            variable_results[variable] = {
                "status": "error",
                "reason": "Estrutura diária inválida."
            }

            continue

        received_dates = set(daily_values.keys())

        # Datas em falta
        missing_dates = (
            expected_dates_set - received_dates
        )

        # Datas fora do período
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

        # Classificar resultados
        variable_status = "valid"

        if missing_dates:
            print("[AVISO] Existem datas sem registos.")
            warnings += 1
            variable_status = "warning"

        if unexpected_dates:
            print("[AVISO] Existem datas fora do período.")
            warnings += 1
            variable_status = "warning"

        if missing_values:
            print("[AVISO] Existem valores de preenchimento.")
            warnings += 1
            variable_status = "warning"

        if invalid_values:
            print("[ERRO] Existem valores inválidos.")
            errors += 1
            variable_status = "error"

        if variable_status == "valid":
            print("[OK] Variável validada.")

        # Guardar resultado individual da variável
        variable_results[variable] = {
            "status": variable_status,
            "records_received": len(daily_values),
            "missing_dates": len(missing_dates),
            "unexpected_dates": len(unexpected_dates),
            "missing_values": missing_values,
            "invalid_values": invalid_values
        }

    # ==================================================
    # 4. RESULTADO FINAL
    # ==================================================

    if errors > 0:
        overall_status = "error"

    elif warnings > 0:
        overall_status = "warning"

    else:
        overall_status = "valid"

    print("\n======================================")
    print("             RESULTADO")
    print("======================================")

    print(f"Total de erros: {errors}")
    print(f"Total de avisos: {warnings}")

    print(f"\nRESULTADO: {overall_status.upper()}")

    print("\nO ficheiro original permanece inalterado.")

    # Devolver relatório para os próximos módulos
    validation_result = {
        "status": overall_status,
        "total_errors": errors,
        "total_warnings": warnings,
        "expected_days": len(expected_dates),
        "variables": variable_results
    }

    return validation_result

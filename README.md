# Agro Intelligence

API de apoio à análise climática de machambas. Recebe a localização e o período de análise, consulta observações diárias da [NASA POWER](https://power.larc.nasa.gov/), valida e limpa os dados e devolve indicadores de precipitação, temperatura e humidade, com informação sobre a cobertura dos dados.

> **Estado actual:** o repositório contém um serviço de recolha e análise climática. A visão inicial do projecto menciona ainda dados locais do solo, características das culturas e estratégias de rotação, mas essas funcionalidades não estão implementadas nesta versão.

## Índice

- [Funcionalidades](#funcionalidades)
- [Tecnologias](#tecnologias)
- [Estrutura do projecto](#estrutura-do-projecto)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Executar a API](#executar-a-api)
- [Utilizar a API](#utilizar-a-api)
- [Fluxo de uma análise](#fluxo-de-uma-análise)
- [Dados e cache](#dados-e-cache)
- [Validação e interpretação](#validação-e-interpretação)
- [Testes](#testes)
- [Limitações conhecidas](#limitações-conhecidas)
- [Contribuir](#contribuir)

## Funcionalidades

- API HTTP construída com FastAPI.
- Consulta de dados diários da NASA POWER para precipitação corrigida (`PRECTOTCORR`), temperatura média (`T2M`), máxima (`T2M_MAX`), mínima (`T2M_MIN`) e humidade relativa (`RH2M`).
- Cache local da resposta original por coordenadas e período. Um ponto guardado pode ser reutilizado para pedidos num raio de até 5 km; o cache expira após sete dias.
- Verificação da estrutura, das datas e dos valores recebidos.
- Conversão dos valores de preenchimento da NASA para `null` nos dados limpos.
- Cálculo de indicadores climáticos e percentagem de cobertura de cada variável.
- Gravação dos dados limpos e do resultado da análise em ficheiros JSON.
- Documentação interactiva dos endpoints fornecida pelo FastAPI.

## Tecnologias

- Python 3
- FastAPI e Pydantic para a API e validação dos pedidos/respostas
- Uvicorn como servidor ASGI
- Requests para chamadas HTTP à NASA POWER
- NASA POWER Daily Point API como fonte de dados climáticos

As dependências e versões fixadas estão em [`requirements.txt`](requirements.txt). Não é necessário configurar uma chave de API da NASA para o cliente actualmente implementado.

## Estrutura do projecto

```text
.
├── data/
│   ├── cache/nasa/            # Respostas originais e metadados do cache
│   └── processed/
│       ├── nasa/              # Observações limpas por dia
│       └── climate/           # Resultados das análises
├── src/
│   ├── api/
│   │   ├── main.py            # Aplicação FastAPI e endpoints
│   │   └── schemas.py         # Modelos de entrada e saída
│   ├── nasa/
│   │   ├── nasa_client.py     # Cliente HTTP da NASA POWER
│   │   └── data_collector.py  # Cache e recolha de observações
│   └── processing/
│       ├── climate_service.py # Coordena o fluxo de análise
│       ├── data_validation.py # Valida os dados brutos recebidos
│       ├── data_cleaning.py   # Organiza dados e trata valores de preenchimento
│       └── climate_analysis.py# Calcula indicadores e grava o resultado
├── tests/
│   └── test_nasa_client.py    # Script de consulta manual ao cliente NASA
├── .env.example
├── requirements.txt
└── README.md
```

Os directórios dentro de `data/` são criados pelo programa conforme necessário. Os ficheiros existentes são dados de exemplo/resultados locais e não são necessários para iniciar a API.

## Requisitos

- Python 3.9 ou superior (o ambiente actualmente incluído no repositório usa Python 3.9).
- `pip`.
- Acesso à Internet para consultar a NASA POWER quando não houver uma entrada válida no cache.

## Instalação

Na raiz do repositório, crie e active um ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

No Windows PowerShell, active-o com:

```powershell
.venv\Scripts\Activate.ps1
```

Instale as dependências:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Não há variáveis de ambiente obrigatórias nesta versão. O ficheiro `.env.example` está vazio e a aplicação não carrega configuração a partir de um `.env`.

## Executar a API

Na raiz do projecto, com o ambiente virtual activo:

```bash
uvicorn src.api.main:app --reload
```

Por omissão, o servidor fica disponível em `http://127.0.0.1:8000`. O parâmetro `--reload` reinicia o servidor durante o desenvolvimento; para o executar sem recarregamento automático, retire esse parâmetro.

Endpoints auxiliares:

- `GET /` — mensagem de estado e versão da API.
- `GET /health` — estado de saúde do serviço.
- `GET /docs` — documentação interactiva Swagger UI.
- `GET /redoc` — documentação ReDoc.
- `POST /api/v1/climate/analyze` — executa uma análise climática.

## Utilizar a API

Envie um pedido `POST` para `/api/v1/climate/analyze` com um corpo JSON como este:

```json
{
  "field_id": "MACHAMBA_001",
  "field_name": "Machamba de demonstração",
  "location": {
    "country": "Angola",
    "province": "Huambo",
    "municipality": "Huambo",
    "latitude": -12.7761,
    "longitude": 15.7392
  },
  "analysis_period": {
    "start_date": "2026-10-01",
    "end_date": "2026-10-31"
  }
}
```

Exemplo com `curl`:

```bash
curl -X POST 'http://127.0.0.1:8000/api/v1/climate/analyze' \
  -H 'Content-Type: application/json' \
  -d '{
    "field_id": "MACHAMBA_001",
    "field_name": "Machamba de demonstração",
    "location": {
      "country": "Angola",
      "province": "Huambo",
      "municipality": "Huambo",
      "latitude": -12.7761,
      "longitude": 15.7392
    },
    "analysis_period": {
      "start_date": "2026-10-01",
      "end_date": "2026-10-31"
    }
  }'
```

As datas devem usar o formato `AAAA-MM-DD`; a data inicial não pode ser posterior à data final. Latitude e longitude têm de estar nos intervalos geográficos válidos. Os campos de país, província e município são metadados fornecidos pelo chamador: a API não verifica se correspondem às coordenadas.

A resposta inclui a identificação da API e da machamba, a localização, o período, a fonte e o instante de geração, a qualidade/cobertura dos dados e os indicadores climáticos. A documentação em `/docs` apresenta os modelos completos de entrada e saída.

## Fluxo de uma análise

1. `src/api/main.py` recebe o pedido e os modelos de `src/api/schemas.py` validam os campos e as datas.
2. `src/processing/climate_service.py` coordena o processamento.
3. `src/nasa/data_collector.py` procura uma resposta compatível no cache. O período tem de coincidir e a localização tem de estar até 5 km do ponto guardado. Se não encontrar, pede novos dados à NASA POWER através de `src/nasa/nasa_client.py`.
4. A resposta original é guardada em `data/cache/nasa/`, juntamente com metadados de localização e período.
5. `src/processing/data_validation.py` verifica as cinco variáveis esperadas, datas em falta ou fora do período e valores inválidos/de preenchimento. Se encontrar erros, o fluxo é interrompido; avisos de dados incompletos, por si só, não interrompem a análise.
6. `src/processing/data_cleaning.py` transforma os parâmetros da NASA numa lista de registos diários e troca o valor de preenchimento por `null`. Guarda o resultado em `data/processed/nasa/` sem alterar o original.
7. `src/processing/climate_analysis.py` calcula os indicadores e a cobertura, e grava a resposta em `data/processed/climate/`.
8. A API devolve o resultado JSON ao chamador.

## Dados e cache

O cliente consulta a NASA POWER Daily Point API em resolução diária, com comunidade `AG` e padrão temporal `UTC`. As chamadas HTTP têm um timeout de 30 segundos. A data é convertida de `AAAA-MM-DD` para `AAAAMMDD`, formato pedido pela NASA.

O cache é local ao projecto e tem validade de sete dias. A pesquisa só reutiliza uma resposta com o mesmo período e coordenadas até 5 km do pedido actual. Se o cache não corresponder, estiver incompleto ou expirado, é feita uma nova consulta quando possível. Os dados são gravados como JSON nos seguintes locais:

- `data/cache/nasa/`: resposta bruta e ficheiro `.meta.json` associado.
- `data/processed/nasa/`: dados limpos por dia.
- `data/processed/climate/`: resultado agregado por machamba e período.

Os nomes dos ficheiros de cache dependem de um hash das coordenadas e do período. O resultado climático usa o identificador da machamba e as datas. O próprio código cria estas pastas quando necessário.

## Validação e interpretação

As variáveis consideradas são:

| Código | Significado | Unidade usada na resposta |
| --- | --- | --- |
| `PRECTOTCORR` | Precipitação diária corrigida | `mm` |
| `T2M` | Temperatura média diária a 2 m | `°C` |
| `T2M_MAX` | Temperatura máxima diária a 2 m | `°C` |
| `T2M_MIN` | Temperatura mínima diária a 2 m | `°C` |
| `RH2M` | Humidade relativa diária a 2 m | `%` |

Os indicadores agregados incluem precipitação total, dias com e sem dados de precipitação, temperatura média e extremos máximos/mínimos do período, humidade média e contagem de dias com precipitação positiva. Um valor de precipitação igual a zero conta como dia sem chuva. A qualidade geral é `complete` se todas as variáveis tiverem cobertura de 100%, `partial` se pelo menos uma tiver cobertura acima de zero e `unavailable` se nenhuma tiver dados.

Os valores de cobertura são calculados em relação a todos os dias do período, incluindo as datas inicial e final. `null` representa dados ausentes; não deve ser interpretado como zero. A resposta identifica o padrão temporal como `UTC`.

## Testes

O ficheiro `tests/test_nasa_client.py` é um **script de consulta manual**, não uma suite pytest. Ele espera ler `data/input/location.json` e consultar a NASA em tempo real. Esse ficheiro não está presente no repositório actual; por isso, o script não funciona sem criar primeiro um JSON com `field_name`, `location` (`latitude` e `longitude`) e `analysis_period` (`start_date` e `end_date`). A execução seria:

```bash
python -m tests.test_nasa_client
```

Esta execução necessita de acesso à Internet e pode falhar caso o serviço externo esteja indisponível. Não existem actualmente testes automatizados documentados para o pipeline completo.

## Limitações conhecidas

- O serviço analisa clima; ainda não recolhe dados de solo ou preferências/prioridades dos agricultores, nem recomenda culturas ou rotações.
- Não existe interface web, autenticação, base de dados ou configuração de produção no repositório actual.
- As chamadas externas dependem da disponibilidade da NASA POWER e de acesso à Internet.
- A localização administrativa é recebida e devolvida, mas não é cruzada com as coordenadas.
- O endpoint converte erros de validação do pipeline em HTTP 502. Erros de rede e algumas falhas de ficheiros podem resultar em erro interno do servidor; o tratamento desses casos pode ser melhorado.
- A cobertura reflecte a disponibilidade dos valores diários recebidos e não representa, por si só, uma avaliação agronómica da adequação dos dados.

## Contribuir

1. Crie um ambiente virtual e instale `requirements.txt`.
2. Execute a API localmente e use `/docs` para explorar o contrato.
3. Ao adicionar uma variável climática, actualize em conjunto a recolha no cliente NASA, a validação, o processamento e os modelos de resposta, quando aplicável.
4. Evite guardar credenciais, ambientes virtuais ou dados pessoais nos commits. Os dados gerados em `data/` podem conter informação de localização e devem ser avaliados antes de serem partilhados.


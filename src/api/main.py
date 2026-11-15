from fastapi import FastAPI
from src.api.schemas import ClimateAnalysisRequest, ClimateAnalysisResponse

app = FastAPI(
    title="Agro Intelligence API",
    description="API para processamento de dados ambientais.",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Agro Intelligence API is running."}

@app.get("/health")
async def health_check():
    return {
         "status": "healthy",
        "service": "Agro Intelligence API"
        }
    
@app.get("/calculo/{param}")
async def calculo(param: str):
    result = f"Processed {int(param) + 1}"
    return {"param": param, "result": result}

@app.get("/climate")
async def climate(lon: float, lat: float):
    return {"longitude": lon, "latitude": lat, "climate_data": "Sample climate data based on coordinates."}

@app.post("/api/v1/climate/analyze",       response_model=ClimateAnalysisResponse)
async def climate_analysis(request: ClimateAnalysisRequest):
    return {
        "message": "Pedido recebido com sucesso.",

        "field_id": request.field_id,
        "field_name": request.field_name,

        "location": {
            "country": request.location.country,
            "province": request.location.province,
            "municipality": request.location.municipality,
            "latitude": request.location.latitude,
            "longitude": request.location.longitude
        },

        "analysis_period": {
            "start_date": request.analysis_period.start_date,
            "end_date": request.analysis_period.end_date
        }
    }
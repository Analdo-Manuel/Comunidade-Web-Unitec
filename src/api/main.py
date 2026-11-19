
from fastapi import FastAPI, HTTPException

from src.api.schemas import ( ClimateAnalysisRequest, ClimateAnalysisResponse )

from src.processing.climate_service import run_climate_analysis


contador = 0

app = FastAPI(
    title="Agro Intelligence API",
    description="API para recolha e análise de dados ambientais.",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "Agro Intelligence API está activa.",
        "version": "1.0.0",
        "status": "online"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Agro Intelligence API"
    }


@app.post("/api/v1/climate/analyze", response_model=ClimateAnalysisResponse)
def analyze_climate(request: ClimateAnalysisRequest):
    
    global contador  # Declare contador as global to modify it within the function

    try:
        result = run_climate_analysis(
            field_id=request.field_id,
            field_name=request.field_name,
            location=request.location.model_dump(),
            start_date=request.analysis_period.start_date.isoformat(),
            end_date=request.analysis_period.end_date.isoformat()
        )
        
        contador += 1
        print(f"Análise de clima realizada com sucesso. Total de análises: {contador}")

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error)
        ) from error
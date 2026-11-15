from datetime import date
from pydantic import BaseModel, Field, model_validator

class Location(BaseModel):
    country: str = Field(
        min_length=2,
        description="País da localização."
    )
    
    province: str = Field(
        min_length=2,
        description="Província da localização."
    )
    
    municipality: str = Field(
        min_length=2,
        description="Município da localização."
    )
    
    latitude: float = Field(
        ge=-90, 
        le=90, 
        description="Latitude da localização."
    )
    
    longitude: float = Field(
        ge=-180, 
        le=180, 
        description="Longitude da localização."
    )
    
class AnalysisPeriod(BaseModel):
    start_date: date = Field(
        description="Data de início do registro."
    )
    
    end_date: date = Field(
        description="Data final da análise."
    )

    @model_validator(mode='after')
    def validate_period(self):
        if self.start_date > self.end_date:
            raise ValueError("Start date must be before or equal to end date.")
        return self


class ClimateAnalysisRequest(BaseModel):
    field_id: str = Field(
        min_length=1,
        description="Identificador único do campo."
    )
    
    field_name: str = Field(
        min_length=1,
        description="Nome do campo."
    )
    
    location: Location = Field(
        description="Informações de localização do campo."
    )
    
    analysis_period: AnalysisPeriod = Field(
        description="Período de análise para os dados climáticos."
    )
    
class ClimateAnalysisResponse(BaseModel):
    message: str
    field_id: str
    field_name: str
    location: Location
    analysis_period: AnalysisPeriod
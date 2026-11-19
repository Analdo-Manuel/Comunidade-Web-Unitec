
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


# ==========================================
# MODELOS DE ENTRADA
# ==========================================

class Location(BaseModel):
    country: str = Field(min_length=1)
    province: str = Field(min_length=1)
    municipality: str = Field(min_length=1)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class AnalysisPeriod(BaseModel):
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_period(self):
        if self.start_date > self.end_date:
            raise ValueError(
                "A data inicial não pode ser posterior à data final."
            )
        return self


class ClimateAnalysisRequest(BaseModel):
    field_id: str = Field(min_length=1)
    field_name: str = Field(min_length=1)
    location: Location
    analysis_period: AnalysisPeriod


# ==========================================
# MODELOS DE RESPOSTA
# ==========================================

class APIInfo(BaseModel):
    name: str
    version: str


class FieldInfo(BaseModel):
    field_id: str
    field_name: str


class Metadata(BaseModel):
    source: str
    temporal_resolution: str
    time_standard: str
    generated_at: datetime


class ClimateAnalysisPeriod(BaseModel):
    start_date: date
    end_date: date
    total_days: int = Field(ge=1)


class VariableQuality(BaseModel):
    available_days: int = Field(ge=0)
    missing_days: int = Field(ge=0)
    coverage_percentage: float = Field(ge=0, le=100)


class DataQuality(BaseModel):
    status: Literal["complete", "partial", "unavailable"]
    expected_days: int = Field(ge=1)
    variables: dict[str, VariableQuality]


class PrecipitationIndicator(BaseModel):
    total: float
    unit: Literal["mm"]
    days_with_data: int = Field(ge=0)
    days_without_data: int = Field(ge=0)


class TemperatureIndicator(BaseModel):
    average: float
    highest: float
    lowest: float
    unit: Literal["°C"]


class HumidityIndicator(BaseModel):
    average: float
    unit: Literal["%"]


class RainfallIndicator(BaseModel):
    rainy_days: int = Field(ge=0)
    days_without_rain: int = Field(ge=0)
    days_without_data: int = Field(ge=0)


class ClimateIndicators(BaseModel):
    precipitation: PrecipitationIndicator
    temperature: TemperatureIndicator
    humidity: HumidityIndicator
    rainfall: RainfallIndicator


class ClimateAnalysisResponse(BaseModel):
    api: APIInfo
    field: FieldInfo
    metadata: Metadata
    location: Location
    analysis_period: ClimateAnalysisPeriod
    data_quality: DataQuality
    indicators: ClimateIndicators
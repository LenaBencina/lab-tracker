from pydantic import BaseModel, EmailStr, model_validator
from datetime import datetime


class Lab(BaseModel):
    name: str
    email: EmailStr | None = None  # EmailStr validates email format
    address: str | None = None


class Report(BaseModel):
    lab_name: str
    report_number: int | None = None
    file_path: str
    collection_date: datetime


class Test(BaseModel):
    name: str
    category: str


class TestResult(BaseModel):
    test: Test
    reference_min: float | None = None
    reference_max: float | None = None
    unit: str
    result: str
    out_of_range: str | None = None

    @model_validator(mode="after")
    def check_reference_range(self):
        if self.reference_min is None and self.reference_max is None:
            raise ValueError(
                "At least one of reference_min or reference_max must be set"
            )
        return self

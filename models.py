from typing import List, Optional
from pydantic import BaseModel, Field

class EmployeeBase(BaseModel):
    name: str
    department: str
    salary: int
    joining_date: str  # Format: YYYY-MM-DD
    skills: List[str]

class EmployeeCreate(EmployeeBase):
    employee_id: str = Field(..., example="E123")

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    salary: Optional[int] = None
    joining_date: Optional[str] = None
    skills: Optional[List[str]] = None

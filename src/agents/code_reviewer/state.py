from typing import TypedDict
from pydantic import BaseModel, Field

# Structured Outputs
class SecurityReview(BaseModel):
    vulnerabilities: list[str] = Field(description="List of vulnerabilities found in the code", default=None)
    riskLevel: str = Field(description="Risk level of the code based on the vulnerabilities found", default=None)
    suggestions: list[str] = Field(description="List of suggestions to fix the vulnerabilities found in the code", default=None)

class MaintainabilityReview(BaseModel):
    concerns: list[str] = Field(description="List of maintainability concerns found in the code", default=None)
    qualityScore: int = Field(description="The quality score of the code based on the maintainability concerns found from 1 to 10", default=None, ge=1, le=10)
    recommendations: list[str] = Field(description="List of recommendations to improve the maintainability of the code", default=None)

class PerformanceReview(BaseModel):
    bottlenecks: list[str] = Field(description="List of performance bottlenecks found in the code", default=None)
    efficiencyScore: int = Field(description="The efficiency score of the code based on the performance bottlenecks found from 1 to 10", default=None, ge=1, le=10)
    optimizationSuggestions: list[str] = Field(description="List of suggestions to optimize the performance of the code", default=None)

# Definition of State
class State(TypedDict):
    code: str
    security_review: SecurityReview
    maintainability_review: MaintainabilityReview
    performance_review: PerformanceReview
    final_review: str
"""
AssureX Claim Engine - Report & Export Pydantic Schemas
"""

from datetime import date
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ReportGenerationRequest(BaseModel):
    report_type: str = Field(..., max_length=50) # claim_summary, audit_log, fraud_analysis, warranty_expiry
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    format: str = Field("pdf", max_length=10) # pdf, csv, excel
    filters: Optional[Dict[str, Any]] = None


class ReportExportFilter(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None


class ReportMetadataResponse(BaseModel):
    report_id: str
    report_name: str
    file_name: str
    file_format: str
    file_size_bytes: int
    generated_at: str
    download_url: str
from fastapi import APIRouter, HTTPException
from typing import List, Dict
from fastapi.responses import JSONResponse

from core.realtime_processor import RealTimeProcessor
from core.analysis_dashboard import CoastalAnalyticsDashboard

router = APIRouter()

# Instantiate or import your core processor (assuming global singleton or imported)
real_time_processor = RealTimeProcessor()
analytics_dashboard = CoastalAnalyticsDashboard()

@router.get("/regions", response_model=Dict)
async def get_tracked_regions():
    """
    Get all Indian coastal regions and locations that are currently tracked.
    """
    try:
        regions = real_time_processor.all_indian_coastal_regions
        return regions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status", response_model=Dict)
async def get_system_status():
    """
    Get current system live statistics and status.
    """
    try:
        status = real_time_processor.get_live_statistics()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/report", response_model=Dict)
async def get_analytics_report():
    """
    Generate and fetch a comprehensive coastal threat analytics report.
    """
    try:
        report = analytics_dashboard.generate_comprehensive_report()
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/insights", response_model=List[str])
async def get_actionable_insights():
    """
    Get actionable insights based on recent data analytics.
    """
    try:
        insights = analytics_dashboard.generate_actionable_insights()
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def root():
    return JSONResponse({"message": "Coastal Threat Alert API is running"})

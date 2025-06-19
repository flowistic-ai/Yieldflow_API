import asyncio
from app.services.dividend_service import DividendService
from datetime import date, timedelta

async def test():
    service = DividendService()
    result = await service.get_comprehensive_dividend_analysis("GOOGL", include_forecast=True)
    print("Growth:", result.get("growth_analytics", {}).get("average_annual_growth", "N/A"))
    print("Quality:", result.get("growth_analytics", {}).get("growth_quality", "N/A"))
    print("Trend:", result.get("growth_analytics", {}).get("growth_trend", "N/A"))

asyncio.run(test())

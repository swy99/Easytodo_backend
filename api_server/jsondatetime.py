import datetime
from datetime import datetime, timezone, timedelta
from dateutil import parser

def JSONdate2datetime(JSONdate: str) -> datetime:
    return parser.parse(JSONdate)

def datetime2JSON(date_time: datetime) -> str:
    dt = date_time.astimezone(timezone.utc)
    dt.replace(microsecond=0)
    return dt.isoformat()[:-6]+'Z'
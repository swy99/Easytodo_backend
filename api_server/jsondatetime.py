import datetime
from datetime import datetime, timezone, timedelta
from dateutil import parser

def JSONdate2datetime(JSONdate: str) -> datetime:
    return parser.parse(JSONdate)

def datetime2JSON(date_time: datetime) -> str:
    dt = date_time.astimezone(timezone.utc)
    dt = dt.replace(microsecond=0)
    res = dt.isoformat()[:-6]+'Z'

    return res

def datetimenow() -> datetime:
    res = datetime.utcnow().astimezone(timezone.utc)
    res = res.replace(microsecond=0)
    return res

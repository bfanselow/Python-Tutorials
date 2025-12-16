### What is a "naive" datetime object?
When we create a python datetime object from a string or from datetime.now(), we often create a "naive" datetime object, meaning it does not have knowledge of the timezone.
While this can often be inferred, especially in environments where all timestamps are assumed to be UTC, strictly speaking this could cause issues, such as when doing
datetime math on the naive object against other datetime objects.

#### Naive Example 1: creating from timestamp string
```
from datetime import datetime

date_string = "2023-10-27 14:30:00"
date_format = "%Y-%m-%d %H:%M:%S"

naive_dt = datetime.strptime(date_string, date_format)

>>> print(f"Naive datetime object: {naive_dt}")
Naive datetime object: 2023-10-27 14:30:00
>>> print(f"Timezone information (tzinfo): {naive_dt.tzinfo}")
Timezone information (tzinfo): None
```

#### Solution: use replace() method passing tzinfo
```
import pytz # or zoneinfo in Python 3.9+
aware_dt = naive_dt.replace(tzinfo=pytz.utc)

>>> print(f"Aware datetime object: {aware_dt}")
Aware datetime object: 2023-10-27 14:30:00+00:00
>>> print(f"Timezone information (tzinfo): {aware_dt.tzinfo}")
Timezone information (tzinfo): UTC
```

#### Naive Example 2: creating from datetime.datetime.now()
```
from datetime import datetime

naive_now = datetime.now()

>>> print(f"Naive now: {naive_now}")
Naive now: 2025-12-16 07:04:52.401555
>>> print(f"Timezone information (tzinfo): {naive_now.tzinfo}")
Timezone information (tzinfo): None
```

#### Solution: call now() with tzinfo arg
```
from datetime import datetime, timezone

aware_utc_now = datetime.now(timezone.utc)

>>> print(f"Aware UTC now: {aware_utc_now}")
Aware UTC now: 2025-12-16 14:05:52.481588+00:00

>>> print(f"Timezone information (tzinfo): {aware_utc_now.tzinfo}")
Timezone information (tzinfo): UTC
```

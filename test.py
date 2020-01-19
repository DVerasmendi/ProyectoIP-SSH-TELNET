from datetime import datetime
import time

t1=time.time()
print(t1)

fmt = '%Y-%m-%d %H:%M:%S'
d1 = datetime.strptime('2010-01-01 17:31:22', fmt)
d2 = datetime.strptime('2010-01-03 17:31:22', fmt)

minutes_diff = (d2 - d1).total_seconds() / 60.0
print(minutes_diff)

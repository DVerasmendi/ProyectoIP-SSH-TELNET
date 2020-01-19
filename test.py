from datetime import datetime
import time

t1=time.time()
print(t1)

fmt = '%Y-%m-%d %H:%M:%S'
d1 = datetime.strptime('2010-01-01 17:31:22', fmt)
d2 = datetime.strptime('2010-01-03 17:31:22', fmt)

minutes_diff = (d2 - d1).total_seconds() / 60.0
print(minutes_diff)


#!/usr/bin/env python
import psutil
# gives a single float value
cpu=psutil.cpu_percent()
# gives an object with many fields

# you can convert that object to a dictionary 
ram=dict(psutil.virtual_memory()._asdict())
percent=ram.get('percent')
print(ram)
print(percent)
if percent>10:
    print('ok')
print(cpu)
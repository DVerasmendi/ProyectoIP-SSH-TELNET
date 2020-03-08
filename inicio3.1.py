import mysql.connector as mysql

from ping3 import ping, verbose_ping
import time
import mysql.connector as mysql
import requests
import subprocess
import sys

from librouteros import connect
from librouteros.login import plain, token
from librouteros.query import Key
from netaddr import *
import pprint

from colorama import Fore, Back, Style, init

import psutil

def readCPU():
    ps=0
    x=0
    for i, percentage in enumerate(psutil.cpu_percent(percpu=True)):
        ps=ps+percentage
        x=ps/(i+1)
    return x

db = mysql.connect(host="160.20.188.232", user="remote", passwd="M4ndr4g0r4!", database="network")
databases = db.cursor()
query = "SELECT * FROM network.summary;"
databases.execute(query)
records = databases.fetchall()
db.close()

total=0
for row in records:
    total=total+1
    print(row)

print()
t1=time.time()
counter=1
counter_for=1
percent_ref=0
for row in records:
    ip=row[1]
    percent=counter_for*100/total
    t2=time.time()-t1
    text=str(t2/60) + ' ==> ' + str(counter_for) + '/' + str(total) + ' = ' + str(percent) + '%: ' + str(ip)
    print(text)
    subprocess.Popen([sys.executable, "search3.1.py", str(ip)])
    print("search3.py", str(ip))
    counter=counter+1
    counter_for=counter_for+1
    while percent_ref==0:
        ram=dict(psutil.virtual_memory()._asdict())
        percent=ram.get('percent')
        cpu_percent=readCPU()
        #time.sleep(0.2)
        if percent < 75 and cpu_percent < 75:
            print(str(int(percent))+'/'+str(int(cpu_percent)))
            percent_ref=1
        else:
            percent_ref==0
            time.sleep(1)
            print('wait ...')
            print(str(int(percent))+'/'+str(int(cpu_percent)))
    percent_ref=0
    print('counter: '+ str(counter))
print('*** END ***')



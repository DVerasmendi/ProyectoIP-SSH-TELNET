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

api=''
prefix_list = []

del api
api = connect(username='476cbn983f675mvf0sm', password='476cbn983f675mvf0sm', host='160.20.188.1')
mikrotik = api.path('ip', 'route', '').select('.id', 'dst-address').where(Key('received-from') == 'puq-scl-17')
for row in mikrotik:
    prefix = row.get('dst-address')
    if prefix.split('.')[0]!='192':
        prefix_list.append(prefix)
        print('puq: ',prefix,sep='')

del api
api = connect(username='476cbn983f675mvf0sm', password='476cbn983f675mvf0sm', host='160.20.188.1')
mikrotik = api.path('ip', 'route', '').select('.id', 'dst-address').where(Key('received-from') == 'vc-scl-17')
for row in mikrotik:
    prefix = row.get('dst-address')
    if prefix.split('.')[0]!='192':
        prefix_list.append(prefix)
        print('nat: ',prefix,sep='')

print()
print(prefix_list)

# exit()

input('continue?')

print()
counter=1
for prefix in prefix_list:
    ipv4_prefix=IPNetwork(prefix)
    for ip in ipv4_prefix:
        print(ip)
        pid = subprocess.Popen([sys.executable, "proyectoipsshtelnet.py", str(ip)])
        #time.sleep(10)
        counter=counter+1
    time.sleep(60)
print()
print(counter)



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
import mysql.connector as mysql
from colorama import Fore, Back, Style, init
import psutil

while True:

    def readCPU():
        ps=0
        x=0
        for i, percentage in enumerate(psutil.cpu_percent(percpu=True)):
            ps=ps+percentage
            x=ps/(i+1)
        return x

    print(Style.RESET_ALL)

    api=''
    prefix_list = []
    prefix_list_out = []

    del api
    api = connect(username='476cbn983f675mvf0sm', password='476cbn983f675mvf0sm', host='160.20.188.1')
    mikrotik = api.path('ip', 'route', '').select('.id', 'dst-address').where(Key('received-from') == 'puq-scl-17')
    for row in mikrotik:
        prefix = row.get('dst-address')
        prefix_split_mask=prefix.split('/')
        mask=int(prefix_split_mask[1])
        if mask>=24:
            if prefix.split('.')[0]!='192':
                prefix_list.append(prefix)
                print('puq: ',prefix,sep='')
            if '/23' in prefix:
                print(prefix)
                #input('continue?')
            if '/22' in prefix:
                print(prefix)
                #input('continue?')
        else:
            prefix_list_out.append(prefix)

    del api
    api = connect(username='476cbn983f675mvf0sm', password='476cbn983f675mvf0sm', host='160.20.188.1')
    mikrotik = api.path('ip', 'route', '').select('.id', 'dst-address').where(Key('received-from') == 'vc-scl-17')
    for row in mikrotik:
        prefix = row.get('dst-address')
        prefix_split_mask=prefix.split('/')
        mask=int(prefix_split_mask[1])
        if mask>=24:
            if prefix.split('.')[0]!='192':
                prefix_list.append(prefix)
                print('nat: ',prefix,sep='')
            if '/23' in prefix:
                print(prefix)
                #input('continue?')
            if '/22' in prefix:
                print(prefix)
                #input('continue?')
        else:
            prefix_list_out.append(prefix)


    print()
    print(prefix_list)

    for data in prefix_list:
        db = mysql.connect(host="160.20.188.232", user="remote", passwd="M4ndr4g0r4!", database="network")
        databases = db.cursor()
        query = "INSERT INTO `network`.`redes` (`red`) VALUES (%s);"
        values = (data,)
        databases.execute(query, values)
        db.commit()

    #input('continue?')

    counter=1
    print('calculating ...')
    for prefix in prefix_list:
        ipv4_prefix=IPNetwork(prefix)
        for ip in ipv4_prefix:
            counter=counter+1
    total=counter
    print('TOTAL: '+str(counter))

    print()
    print('=================')
    for p1 in prefix_list_out:
        print(p1)
    print('=================')
    print()

    print('=================')
    #input('begin?')

    prefix_list=[]
    db = mysql.connect(host="160.20.188.232", user="remote", passwd="M4ndr4g0r4!", database="network")
    databases = db.cursor()
    query = "SELECT DISTINCT red FROM `network`.`redes`;"
    databases.execute(query)
    data = databases.fetchall()
    for row in data:
        prefix_list.append(row[0])

    print()
    t1=time.time()
    counter=1
    counter_for=1
    percent_ref=0
    for prefix in prefix_list:
        ipv4_prefix=IPNetwork(prefix)
        for ip in ipv4_prefix:
            percent=counter_for*100/total
            t2=time.time()-t1
            text=str(t2/60) + ' ==> ' + str(counter_for) + '/' + str(total) + ' = ' + str(percent) + '%: ' + str(ip)
            print(text)
            dont_run = 0
            for pr in psutil.process_iter():
                if 'python3' in pr.name():
                    pinfo = pr.as_dict(attrs=['cmdline'])
                    cmdline = pinfo.get('cmdline')
                    # print(cmdline)
                    if ip in cmdline:
                        print(Fore.YELLOW, '')
                        print('************************')
                        print('dont_run', ip, sep=': ')
                        print('************************')
                        print(Style.RESET_ALL)
                        dont_run = 1
            if dont_run == 0:
                subprocess.Popen([sys.executable, "just-scan_2.1.py", str(ip)])
            counter=counter+1
            counter_for=counter_for+1
            while percent_ref==0:
                ram=dict(psutil.virtual_memory()._asdict())
                percent=ram.get('percent')
                cpu_percent=readCPU()
                if percent < 85 and cpu_percent < 85:
                    print(str(int(percent))+'/'+str(int(cpu_percent)))
                    percent_ref=1
                else:
                    percent_ref==0
                    time.sleep(1)
                    print(str(int(percent))+'/'+str(int(cpu_percent)))
            percent_ref=0
        print('counter: '+ str(counter))
    print('*** END ***')

    print()
    print('restarting ...')
    time.sleep(60)
# API
from librouteros import connect
from librouteros.login import plain, token
from librouteros.query import Key
import pprint
import paramiko
import requests
import telnetlib
import time
from colorama import Fore, Back, Style, init
import locale
import sys
import mysql.connector as mysql
import socket
from colorama import Fore, Back, Style, init
from pythonping import ping


def to_MySQL_summary(ip, puertos):

    ping_status = puertos[0]
    api = puertos[1]
    ssh = puertos[2]
    port8291 = puertos[3]
    port8299 = puertos[4]
    port8292 = puertos[5]

    db = mysql.connect(host="160.20.188.232", user="remote", passwd="M4ndr4g0r4!", database="network")
    databases = db.cursor()

    query = 'DELETE FROM network.summary WHERE ip ="'+ip+'"'

    databases.execute(query)
    db.commit()

    query = "INSERT INTO summary (ip, ping, ssh, api, port_8291, port_8292, port_8299) VALUES (%s,%s,%s,%s,%s,%s,%s)"
    values = (ip, ping_status, ssh, api, port8291, port8292, port8299)
    databases.execute(query, values)
    db.commit()

    return ''


def writelog(data):
    try:
        f = open("mikrotik_" + ip + ".txt", "a")
        f.write(data+'\n')
        f.close()
        return
    except:
        return


def check_port(ip):

    port_list = [8728, 22, 8291, 8299, 8292]
    port_list_result = [0, 0, 0, 0, 0, 0]

    response_list = ping(ip, size=40, count=5)
    tf=response_list.rtt_avg_ms
    if tf<2000:
        port_list_result[0] = 1
        return port_list_result

    counter = 1
    for port in port_list:
        for x in range(3):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((ip, port))
            if result == 0:
                sock.close()
                port_list_result[counter] = 1
                return port_list_result
        counter = counter+1

    return port_list_result


ip = ''
# ip ='10.200.54.2'
# ip = '10.143.68.254'
ip = '10.18.12.254'
# ip = '10.0.4.176'
if ip == '':
    if len(sys.argv) == 2:
        ip = sys.argv[1]
    else:
        exit()

try:

    print(' ++ '+ip)
    puertos = check_port(ip)
    print(ip, puertos, sep=' ==> ')

    #[ping, 8728, 22, 8291, 8299, 8292]
    ping = puertos[0]
    api = puertos[1]
    ssh = puertos[2]
    port8291 = puertos[3]
    port8299 = puertos[4]
    port8292 = puertos[5]

    active=0
    for x in puertos:
        if x == 1:
            active = 1

    if active == 1:
        to_MySQL_summary(ip, puertos)

    exit()

except:
    if 'SystemExit' in str(sys.exc_info()[0]):
        exit()
    print(Fore.YELLOW, '')
    print('************************')
    print(ip+' ==> ** ERROR APP **:')
    error_data = ''
    for row in sys.exc_info():
        print(row)
        error_data = error_data+str(row)
    writelog(error_data)
    print('************************')
    print(Style.RESET_ALL)

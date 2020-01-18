# API
from librouteros import connect
from librouteros.login import plain, token
from librouteros.query import Key
import pprint
import paramiko
from ping3 import ping, verbose_ping
import requests
import telnetlib
import time
from colorama import Fore, Back, Style, init
import locale
import sys
import mysql.connector as mysql
import socket
from colorama import Fore, Back, Style, init


def get_data_from_api(user, password, ip, method_type):

    try:

        api = ''
        mikrotik = ''

        identity = ''
        group = ''
        version = ''
        model = ''

        del api
        del mikrotik
        api = connect(username=user, password=password, host=ip, login_method=method_type)
        mikrotik = api.path('system', 'identity')
        for row in mikrotik:
            identity = row.get('name')

        del api
        del mikrotik
        api = connect(username=user, password=password, host=ip, login_method=method_type)
        mikrotik = api.path('user').select('name', 'group').where(Key('name') == user)
        for row in mikrotik:
            group = row.get('group')

        del api
        del mikrotik
        api = connect(username=user, password=password, host=ip, login_method=method_type)
        mikrotik = api.path('system', 'resource')
        for row in mikrotik:
            version = row.get('version')

        del api
        del mikrotik
        api = connect(username=user, password=password, host=ip, login_method=method_type)
        mikrotik = api.path('system', 'routerboard')
        for row in mikrotik:
            model = row.get('model')

        if group != '' and group != 'full':
            to_MySQL((ip, user, password, group_ssh, identity_ssh, version_ssh, modelo_ssh, '8728'), puertos)

        result = (ip, user, password, identity, group, version, model, '8728')
        return result

    except:
        print_error(sys.exc_info()[0])
        return 'error'


def get_data_from_ssh(user, password, ip):

    try:

        cmd0 = '/user print terse where name="'+user+'"'
        cmd1 = '/system identity print without-paging'
        cmd2 = '/system resource print without-paging'
        cmd3 = '/ip service enable [find where name=api]'
        cmd4 = '/system routerboard print without-paging'

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, 22, user, password)

        # GRUPO
        stdin, stdout, stderr = ssh.exec_command(cmd0)
        outlines = stdout.readlines()
        outlines = outlines[0]
        if 'group=full' in outlines:
            group_ssh = 'full'
            stdin, stdout, stderr = ssh.exec_command(cmd3)
            api_on = stdout.readlines()
        else:
            group_ssh = ''

        # IDENTITY SSH
        stdin, stdout, stderr = ssh.exec_command(cmd1)
        identity_ssh = stdout.readlines()
        identity_ssh = identity_ssh[0]
        identity_ssh = identity_ssh.split('name: ')[1].strip()

        # VERSION
        stdin, stdout, stderr = ssh.exec_command(cmd2)
        version_ssh = stdout.readlines()
        for row in version_ssh:
            if 'version' in row:
                version_ssh = row.split('version:')[1].strip()
                break

        # Modelo
        stdin, stdout, stderr = ssh.exec_command(cmd4)
        modelo_ssh = stdout.readlines()
        for row in modelo_ssh:
            if 'model' in row:
                modelo_ssh = row.split('model:')[1].strip()
                break

        if group_ssh != '' and group_ssh != 'full':
            to_MySQL((ip, user, password, group_ssh, identity_ssh, version_ssh, modelo_ssh, '22'), puertos)

        result = (ip, user, password, identity_ssh, group_ssh, version_ssh, modelo_ssh, '22')
        return result

    except:
        print_error(sys.exc_info()[0])
        return 'error'


def api_request(ip):

    for row in user_password_list:

        user = row[0].strip()
        password = row[1].strip()

        print(ip+' ==> '+user + '@' + password)

        result = get_data_from_api(user, password, ip, plain)
        if result == 'error':
            result = get_data_from_api(user, password, ip, token)

        if result[4] == 'full':
            return result

    return ''


def ssh_request(ip):

    for row in user_password_list:

        user = row[0].strip()
        password = row[1].strip()

        result = ''

        print(ip+' ==> '+user + '@' + password)
        result = get_data_from_ssh(user, password, ip)
        # print(result)

        if result != 'error' and 'full' in result:
            return result

    return ''


def to_MySQL(status, puertos):

    try:

        # ('10.200.54.2', 'admin', 'N0s31717', 'RB962 VILLASAUCE', 'full', '6.38.7 (bugfix)', 'RouterBOARD 962UiGS-5HacT2HnT', '8728')
        # (1, 1, 1, 1, 0, 0)
        #[ping, 8728, 22, 8291, 8299, 8292]

        ip = status[0]
        user = status[1]
        password = status[2]
        identity = status[3]
        group = status[4]
        version = status[5]
        modelo = status[6]
        puerto = status[7]

        ping_status = puertos[0]
        api = puertos[1]
        ssh = puertos[2]
        port8291 = puertos[3]
        port8299 = puertos[4]
        port8292 = puertos[5]

        db = mysql.connect(host="160.20.188.232", user="remote", passwd="M4ndr4g0r4!", database="network")
        databases = db.cursor()

        query = 'DELETE FROM network.devices WHERE ip ="'+ip+'"'

        databases.execute(query)
        db.commit()

        print(ip, identity, sep=' ==> ')

        query = "INSERT INTO devices (identity, ip,user ,password, version, modelo ,grupo, puertoacceso, ping_status, ssh_status, api_status, var_port_8291, var_port_8299, var_port_8292) VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (identity, ip, user, password, version, modelo, group, puerto, ping_status, ssh, api, port8291, port8299, port8292)
        databases.execute(query, values)
        db.commit()

        print(values)
        return ''

    except:
        print_error(sys.exc_info()[0])
        return ''


def print_error(data):
    data = str(data)
    if 'librouteros.exceptions.FatalError' in data:
        return
    if 'librouteros.exceptions.TrapError' in data:
        return
    if 'paramiko.ssh_exception.AuthenticationException' in data:
        return
    print(Fore.YELLOW, '')
    print('************************')
    print(ip+' ==> ** ERROR **: '+data)
    print('************************')
    print(Style.RESET_ALL)


def check_port(ip):

    port_list = [8728, 22, 8291, 8299, 8292]
    port_list_result = [0, 0, 0, 0, 0, 0]

    counter = 1
    for port in port_list:
        for x in range(3):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((ip, port))
            if result == 0:
                sock.close()
                port_list_result[counter] = 1
                break
        counter = counter+1

    for x in range(3):
        ping_response = ping(ip)
        if isinstance(ping_response, float):
            port_list_result[0] = 1
            break

    return (port_list_result)


# ip='10.200.54.2'
ip = '10.143.68.254'
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

    user_password_list = []
    for i in ['admin', 'tfa', 'austro', 'jedis']:
        for j in ['N0s31717', 'N0s31717!', 'austro2018', 'austro2019', 'B9s31717!!.', 'B0s31818!!.', 'B8s31717!!.', 'austro']:
            user_password_list.append((i, j))

    status = ''

    if puertos == (0, 0, 0, 0, 0, 0):
        exit()
    elif (ssh == 0 and api == 0) and (ping == 1 or port8291 == 1 or port8299 == 1 or port8292 == 1):
        # Insertar en MySQL
        exit()
    else:
        if api == 1 and ssh == 1:
            status = api_request(ip)
            if status != '':
                to_MySQL(status, puertos)
                exit()
            else:
                status = ssh_request(ip)
                if status != '':
                    to_MySQL(status, puertos)
                    exit()
                else:
                    to_MySQL((ip, '', '', '', '', '', '', ''), puertos)
                    exit()
        elif api == 1:
            status = api_request(ip)
            if status != '':
                to_MySQL(status, puertos)
            else:
                to_MySQL((ip, '', '', '', '', '', '', ''), puertos)
            exit()
        elif ssh == 1:
            status = ssh_request(ip)
            if status != '':
                to_MySQL(status, puertos)
            else:
                to_MySQL((ip, '', '', '', '', '', '', ''), puertos)
            exit()
        else:
            exit()

except:
    if 'SystemExit' in str(sys.exc_info()[0]):
        exit()
    print(Fore.YELLOW, '')
    print('************************')
    print(ip)
    print(' ==> ** ERROR APP **:')
    for row in sys.exc_info():
        print(row)
    print('************************')
    print(Style.RESET_ALL)

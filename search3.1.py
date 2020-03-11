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
        print_error(sys.exc_info())
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
        print_error(sys.exc_info())
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
        db.close()

        print(ip, identity, sep=' ==> ')

        db = mysql.connect(host="160.20.188.232", user="remote", passwd="M4ndr4g0r4!", database="network")
        databases = db.cursor()
        query = "INSERT INTO devices (identity, ip,user ,password, version, modelo ,grupo, puertoacceso, ping_status, ssh_status, api_status, var_port_8291, var_port_8299, var_port_8292) VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (identity, ip, user, password, version, modelo, group, puerto, ping_status, ssh, api, port8291, port8299, port8292)
        databases.execute(query, values)
        db.commit()
        db.close()

        print(values)
        return ''

    except:
        print_error(sys.exc_info())
        return ''


def to_MySQL_update(status, puertos):

    try:

        # ('10.200.54.2', 'admin', 'N0s31717', 'RB962 VILLASAUCE', 'full', '6.38.7 (bugfix)', 'RouterBOARD 962UiGS-5HacT2HnT', '8728')
        # (1, 1, 1, 1, 0, 0)
        #[ping, 8728, 22, 8291, 8299, 8292]

        ip = status[0]
        user = status[1]
        password = status[2]
        identity = status[3]
        grupo = status[4]
        version = status[5]
        modelo = status[6]
        puertoacceso = status[7]

        ping_status = str(puertos[0])
        api_status = str(puertos[1])
        ssh_status = str(puertos[2])
        var_port_8291 = str(puertos[3])
        var_port_8299 = str(puertos[4])
        var_port_8292 = str(puertos[5])

        var_MySQL = ['identity', 'user', 'password', 'modelo', 'version', 'grupo', 'puertoacceso', 'ping_status', 'ssh_status', 'api_status', 'var_port_8291', 'var_port_8292', 'var_port_8299']
        var_data = [identity, user, password, modelo, version, grupo, puertoacceso, ping_status, ssh_status, api_status, var_port_8291, var_port_8292, var_port_8299]

        db = mysql.connect(host="160.20.188.232", user="remote", passwd="M4ndr4g0r4!", database="network")
        databases = db.cursor()

        print(ip, identity, sep=' ==> ')

        counter = 0
        for row in var_MySQL:
            query = "UPDATE devices SET " + row + "='" + var_data[counter] + "' WHERE ip='" + ip + "'" + "; "
            databases.execute(query)
            db.commit()
            counter = counter+1
        
        db.close()
        return ''

    except:
        print_error(sys.exc_info())
        return ''


def to_MySQL_summary(ip, puertos):

    try:

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
        db.close()

        db = mysql.connect(host="160.20.188.232", user="remote", passwd="M4ndr4g0r4!", database="network")
        databases = db.cursor()
        query = "INSERT INTO summary (ip, ping, ssh, api, port_8291, port_8292, port_8299) VALUES (%s,%s,%s,%s,%s,%s,%s)"
        values = (ip, ping_status, ssh, api, port8291, port8292, port8299)
        databases.execute(query, values)
        db.commit()
        db.close()

        return ''

    except:
        print_error(sys.exc_info())
        return ''

def count_MySQL_IP_full(ip):

    try:

        db = mysql.connect(host="160.20.188.232", user="remote", passwd="M4ndr4g0r4!", database="network")
        databases = db.cursor()
        query = "SELECT COUNT(*) as total FROM network.devices WHERE ip='"+ip+"' AND grupo='full'"
        databases.execute(query)
        data = databases.fetchall()
        db.close()
        for row in data:
            if row[0]==0:
                return 0
            else:
                return 1

        return 0

    except:
        print_error(sys.exc_info())
        return ''


def print_error(data):
    error0 = str(data[0])
    if 'librouteros.exceptions.FatalError' in error0:
        return
    if 'librouteros.exceptions.TrapError' in error0:
        return
    if 'paramiko.ssh_exception.AuthenticationException' in error0:
        return
    if 'paramiko.ssh_exception.SSHException' in error0:
        print(Fore.RED, '')
        print('************************')
        print(ip+' ==> ** ERROR **')
        error_data = ''
        for row in data:
            print(row)
            error_data = error_data+str(row)
        writelog(error_data)
        print('************************')
        print(Style.RESET_ALL)
        return
    print(Fore.YELLOW, '')
    print('************************')
    print(ip+' ==> ** ERROR **')
    error_data = ''
    for row in data:
        print(row)
        error_data = error_data+str(row)
    writelog(error_data)
    print('************************')
    print(Style.RESET_ALL)
    return


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

    response_list = ping(ip, size=40, count=5)
    tf=response_list.rtt_avg_ms
    if tf<2000:
        port_list_result[0] = 1

    return (port_list_result)


def writelog(data):
    try:
        f = open("mikrotik_" + ip + ".txt", "a")
        f.write(data+'\n')
        f.close()
        return
    except:
        return


ip = ''
# ipi='10.200.54.2'
# ip = '10.143.68.254'
# ip = '10.18.12.254'
# ip='10.23.15.250'

if ip == '':
    if len(sys.argv) == 2:
        ip = sys.argv[1]
    else:
        exit()

try:

    check_MySQL=count_MySQL_IP_full(ip)
    if check_MySQL==1:
        exit()

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
    active = 0

    for x in puertos:
        if x == 1:
            active = 1

    if active == 1:
        to_MySQL((ip, '', '', '', '', '', '', ''), puertos)
        to_MySQL_summary(ip, puertos)

    if puertos == (0, 0, 0, 0, 0, 0):
        exit()
    elif (ssh == 0 and api == 0) and (ping == 1 or port8291 == 1 or port8299 == 1 or port8292 == 1):
        exit()
    else:
        if api == 1 and ssh == 1:
            status = api_request(ip)
            if status != '':
                to_MySQL_update(status, puertos)
                exit()
            else:
                status = ssh_request(ip)
                if status != '':
                    to_MySQL_update(status, puertos)
                exit()
        elif api == 1:
            status = api_request(ip)
            if status != '':
                to_MySQL_update(status, puertos)
            exit()
        elif ssh == 1:
            status = ssh_request(ip)
            if status != '':
                to_MySQL_update(status, puertos)
            exit()
        else:
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
    tb = sys.exc_info()[2]
    print('line:',tb.tb_lineno)
    print('************************')
    print(Style.RESET_ALL)

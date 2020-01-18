# API
from librouteros import connect
from librouteros.login import plain, token
from librouteros.query import Key
import pprint
# SHH
import paramiko
# PING
from ping3 import ping, verbose_ping
import requests
# telnet
import telnetlib
import time
from colorama import Fore, Back, Style, init
import locale
import sys
import mysql.connector as mysql
import socket
################################   Función para validar puerto abierto   ######################


def port_open(ip):

    api = 0
    api = 0
    ssh = 0
    ping_value = 0
    port8291 = 0
    port8299 = 0
    port8292 = 0

    try:
        for x in range(3):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((ip, 8728))
            if result == 0:
                sock.close()
                api = 1
                break
    except:
        sock.close()
        api = 0

    try:
        # Valida puerto SSH
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((ip, 22))

        if result == 0:
            #print("SSH is open")
            ssh = 1
        else:
            #print("SSH is close")
            sock.close()
            ssh = 0

    except:
        #print ('SSH is close 2')
        ssh = 0

    try:
        # Valida PING
        ping_response = ping(ip)
        if isinstance(ping_response, float):
            # print("PING--->UP")
            ping_value = 1
        else:
            # print("PING--->DOWN")
            ping_value = 0
    except:
        #print ('PING--->DOWN 2')
        ping_value = 0

    # Validar puerto 8291
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((ip, 8291))

        if result == 0:
            #print("Wimbox-8291 is open")
            sock.close()
            port8291 = 1
        else:
            #print("Wimbox-8291 is close")
            sock.close()
            port8291 = 0

    except:
        #print ('Wimbox-8291 is close 2')
        sock.close()
        port8291 = 0

    # Validar puerto 8299
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((ip, 8299))

        if result == 0:
            #print("Wimbox-8299 is open")
            sock.close()
            port8299 = 1
        else:
            #print("Wimbox-8299 is close")
            sock.close()
            port8299 = 0

    except:
        #print ('Wimbox-8299 is close 2')
        sock.close()
        port8299 = 0

    # Validar puerto 8292
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((ip, 8292))

        if result == 0:
            #print("Wimbox-8292 is open")
            sock.close()
            port8292 = 1
        else:
            #print("Wimbox-8292 is close")
            sock.close()
            port8292 = 0

    except:
        #print ('Wimbox-8292 is close 2')
        sock.close()
        port8292 = 0

    return (api, ssh, ping_value, port8291, port8299, port8292)

############################## LLENAR BASE DE DATOS #############################################


def insertBD(identity, ip, user, password, version, modelo, group, puerto, ping_status, ssh, api, port8291, port8299, port8292):
    db = mysql.connect(
        host="160.20.188.232",
        user="remote",
        passwd="M4ndr4g0r4!",
        database="network"  # Con esto se valida que la base de datos existe, de no existir, arroja error
    )
    databases = db.cursor()  # Mi puntero para ubicarme en la BD

    # databases.execute("SHOW DATABASES")# preparate para ejecutar esta linea
    # databases = databasesfetchall() #no tengo idea aun ;) hehe xd
    # print(databases)

    # for x in databases:
    #     print(x)

    query = 'DELETE FROM network.devices WHERE ip ="'+ip+'"'
   # '/user print terse where name="'+username+'"'
    databases.execute(query)
    db.commit()

    print(ip, identity, sep=': ')

    query = "INSERT INTO devices (identity, ip,user ,password, version, modelo ,grupo, puertoacceso, ping_status, ssh_status, api_status, var_port_8291, var_port_8299, var_port_8292) VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    values = (identity, ip, user, password, version, modelo, group, puerto, ping_status, ssh, api, port8291, port8299, port8292)
    databases.execute(query, values)  # Ejecuta la tarea indicada
    db.commit()  # Deja de forma permanente los cambios efectuados anteriormente, los guarda como los equipos UBNT
    # print(databases.rowcount, "record inserted") #imprime cuantas filas fueron modificadas

############################ VALIDAR USER GROUP POR API#############################################


def user_group_api(ip, user, password):
   # API
    try:
        api = ''
        mikrotik = ''
        name = user
        print(ip)
        print(user)
        print(password)
        # print(type(ip))
        # print(type(user))
        # print(type(passord2))
        # Extraccion identity
        del api
        del mikrotik
        api = connect(username=user, password=password, host=ip)
        mikrotik = api.path('system', 'identity')
        for row in mikrotik:
            identity = row.get('name')
            print('IDENTITY:'+identity)
        # Extraccion version
        del api
        del mikrotik
        api = connect(username=user, password=password, host=ip)
        mikrotik = api.path('system', 'resource')
        for row in mikrotik:
            version = row.get('version')
            print('version--->'+version)

        # Extraccion Modelo
        del api
        del mikrotik
        api = connect(username=user, password=password, host=ip)
        mikrotik = api.path('system', 'routerboard')
        for row in mikrotik:
            model = row.get('model')
            print('Modelo--->'+model)

        # Extraccion grupo
        del api
        del mikrotik
        api = connect(username=user, password=password, host=ip)
        mikrotik = api.path('user').select('name', 'group').where(Key('name') == name)
        for row in mikrotik:
            group = row.get('group')
            print('GROUP--->'+group)

        if identity != '' and group != '':
            return group, identity, version, model

    except:
        print('*******ERROR  al loggear con API PLAIN************')
        api = ''
        mikrotik = ''
        name = user
        print(ip)
        print(user)
        print(password)
        # print(type(ip))
        # print(type(user))
        # print(type(passord2))
        # Extraccion identity
        del api
        del mikrotik
        api = connect(username=user, password=password, host=ip, login_method=token)
        mikrotik = api.path('system', 'identity')
        for row in mikrotik:
            identity = row.get('name')
            print('IDENTITY:'+identity)
        # Extraccion version
        del api
        del mikrotik
        api = connect(username=user, password=password, host=ip, login_method=token)
        mikrotik = api.path('system', 'resource')
        for row in mikrotik:
            version = row.get('version')
            print('version--->'+version)

        # Extraccion Modelo
        del api
        del mikrotik
        api = connect(username=user, password=password, host=ip, login_method=token)
        mikrotik = api.path('system', 'routerboard')
        for row in mikrotik:
            model = row.get('model')
            print('Modelo--->'+model)

        # Extraccion grupo
        del api
        del mikrotik
        api = connect(username=user, password=password, host=ip, login_method=token)
        mikrotik = api.path('user').select('name', 'group').where(Key('name') == name)
        for row in mikrotik:
            group = row.get('group')
            print('GROUP--->'+group)

        if identity != '' and group != '':
            return group, identity, version, model
        return None
############################ VALIDAR USER GROUP POR SSH #############################################


def user_group_ssh(ip, user, password):
    # SSH
    try:
        ip = ip
        username = user
        password = password
        cmd = '/user print terse where name="'+username+'"'
        cmd1 = '/system identity print'
        cmd2 = '/system resource print'
        cmd3 = '/ip service enable [find where name=api]'
        cmd4 = '/system routerboard print'
        ################################################################
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, 22, username, password)

        # Encendiendo API
        stdin, stdout, stderr = ssh.exec_command(cmd3)
        api_on = stdout.readlines()

        # GRUPO
        stdin, stdout, stderr = ssh.exec_command(cmd)
        outlines = stdout.readlines()
        outlines = outlines[0]

        # IDENTITY SSH
        stdin, stdout, stderr = ssh.exec_command(cmd1)
        identity_ssh = stdout.readlines()
        identity_ssh = identity_ssh[0]
        identity_ssh = identity_ssh.split('name: ')[1].strip()
        print('IDENTITY SSH:' + identity_ssh)

        # VERSION
        stdin, stdout, stderr = ssh.exec_command(cmd2)
        version_ssh = stdout.readlines()
        version_ssh = version_ssh[1].split('version:')[1].strip()
        print('VERSION SSH:' + version_ssh)

        try:
            # Modelo
            stdin, stdout, stderr = ssh.exec_command(cmd4)
            modelo_ssh = stdout.readlines()
            modelo_ssh = modelo_ssh[2].split('model:')[1].strip()
            print('MODELO SSH:' + modelo_ssh)
        except:
            print('****************No pudo traer Modelo')
            # Modelo
            stdin, stdout, stderr = ssh.exec_command(cmd4)
            modelo_ssh = stdout.readlines()
            modelo_ssh = modelo_ssh[1].split('model:')[1].strip()
            print('MODELO SSH:' + modelo_ssh)

        if 'group=full' in outlines:
            group_ssh = 'full'
            print('GRUPO : FULL')
            return group_ssh, identity_ssh, version_ssh, modelo_ssh

    except:
        print('****************ERROR SSH')

###############################  LOGIN  ######################################


def login(ip, api, ssh, ping, port8291, port8299, port8292):
    try:

        user_password_list = []
        for i in ['admin', 'xxx', 'tfa', 'austro', 'jedis']:
            for j in ['N0s31717', 'xxx', 'N0s31717!', 'N0s31717', 'austro2018', 'austro2019', 'B9s31717!!.', 'B0s31818!!.', 'B8s31717!!.', 'austro']:
                user_password_list.append((i, j))

        for row in user_password_list:
            user = row[0].strip()
            password = row[1].strip()
            print(user+'-->'+password)
            grupo_identity_tupla = ''

            if api == 1:

                grupo_identity_tupla = user_group_api(ip, user, password)
                # USER group me trae grupo, identity, version, modelo
                print(grupo_identity_tupla)

                if grupo_identity_tupla is None:
                    print('No es posible conectar con este usuario y contraseña')
                    return 0

                else:
                    grupo = grupo_identity_tupla[0]
                    identity = grupo_identity_tupla[1]
                    version = grupo_identity_tupla[2]
                    modelo = grupo_identity_tupla[3]
                    print('<----------------- LOGIN ----------------->')
                    print('IP: '+ip)
                    print('PASSWORD: '+password)
                    print('IDENTITY: ' + identity)
                    print('GROUP: ' + grupo)
                    print('VERSION: ' + version)
                    print('MODELO: ' + modelo)

                    if grupo == 'full':
                        insertBD(identity, ip, user, password, version, modelo, grupo, '8728', ping, ssh, api, port8291, port8299, port8292)
                        break

            else:
                print('ENTRO EN SSH ELSE')
                grupo_identity_tupla2 = user_group_ssh(ip, user, password)
                # USER group SSH me trae grupo, identity, version, modelo por SSH y ACTIVA LA API
                print(grupo_identity_tupla2)

                if grupo_identity_tupla2 is None:
                    print('No es posible conectar con este usuario y contraseña')

                else:
                    grupossh = grupo_identity_tupla2[0]
                    identityssh = grupo_identity_tupla2[1]
                    versionssh = grupo_identity_tupla2[2]
                    modelossh = grupo_identity_tupla2[3]

                    print('GROUP:' + grupossh)
                    print('IDENTITY:' + identityssh)
                    print('VERSION:' + versionssh)
                    print('MODELO: ' + modelossh)
                    print('IP: '+ip)
                    print('PASSWORD: '+password)

                    insertBD(identityssh, ip, user, password, versionssh, modelossh, grupossh, '22', ping, ssh, api, port8291, port8299, port8292)
                    break

    except:
        print('*****', ip, sep=': ')
        print('**** ERROR LOGIN ****')
        e = sys.exc_info()[0]
        print("<p>Error: %s</p>" % e)
        return 0
################################################################################


#####################################################

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

        result = (ip, user, password, group_ssh, identity_ssh, version_ssh, modelo_ssh, '22')
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

        identity = status[3]
        ip = status[0]
        user = status[1]
        password = status[2]
        version = status[5]
        modelo = status[6]
        group = status[4]
        puerto = status[7]
        ping_status = puertos[2]
        ssh = puertos[1]
        api = puertos[0]
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
    print(ip+' ==> ** ERROR **: '+data)


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
ip = ''
if ip == '':
    if len(sys.argv) == 2:
        ip = sys.argv[1]
    else:
        sys.exit()

print(' ++ '+ip)
puertos = check_port(ip)
print(ip, puertos, sep=' ==> ')

api = puertos[0]
ssh = puertos[1]
ping = puertos[2]
port8291 = puertos[3]
port8299 = puertos[4]
port8292 = puertos[5]

user_password_list = []
for i in ['admin', 'tfa', 'austro', 'jedis']:
    for j in ['N0s31717', 'N0s31717!', 'austro2018', 'austro2019', 'B9s31717!!.', 'B0s31818!!.', 'B8s31717!!.', 'austro']:
        user_password_list.append((i, j))

status = ''

if puertos == (0, 0, 0, 0, 0, 0):
    sys.exit()
elif (ssh == 0 and api == 0) and (ping == 1 or port8291 == 1 or port8299 == 1 or port8292 == 1):
    # Insertar en MySQL
    sys.exit()
else:
    if api == 1 and ssh == 1:
        status = api_request(ip)
        if status != '':
            to_MySQL(status, puertos)
            sys.exit()
        else:
            status = ssh_request(ip)
            if status != '':
                to_MySQL(status, puertos)
                sys.exit()
            else:
                to_MySQL((ip, '', '', '', '', '', '', ''), puertos)
                sys.exit()
    elif api == 1:
        status = api_request(ip)
        if status != '':
            to_MySQL(status, puertos)
        else:
            to_MySQL((ip, '', '', '', '', '', '', ''), puertos)
        sys.exit()
    elif ssh == 1:
        status = ssh_request(ip)
        if status != '':
            to_MySQL(status, puertos)
        else:
            to_MySQL((ip, '', '', '', '', '', '', ''), puertos)
        sys.exit()
    else:
        sys.exit()

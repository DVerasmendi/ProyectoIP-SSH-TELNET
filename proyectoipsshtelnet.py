#API
from librouteros import connect
from librouteros.login import plain, token
from librouteros.query import Key
import pprint
#SHH
import paramiko
#PING
from ping3 import ping, verbose_ping
import requests
#telnet
import telnetlib
import time
from colorama import Fore, Back, Style, init
import locale
import sys
import mysql.connector as mysql
import socket
################################    TELNET   ######################################    
def telnet(ip, user, password):
    
    try:
        HOST = ip
        user = user
        password = password
        PORT='23' # getpass.getpass()

        command='/ system identity print'
        command_2='quit'
        tn=''
        del tn
        tn=telnetlib.Telnet(HOST,PORT)

        #input user
        tn.read_until(b"Login: ")
        tn.write(user.encode('UTF-8') + b"\r")
        #input password
        tn.read_until(b"Password: ")
        tn.write(password.encode('UTF-8') + b"\r")
        tn.read_until(b'>')
        tn.write(command.encode('UTF-8')+b"\r")
        tn.read_until(b'>')
        tn.write(b"\r")
        tn.write(command_2.encode('UTF-8')+b"\r")
        name= tn.read_all().split(b'\r\r\n\r\r\r\r')[0].split(b'\r\n\r')[1]

        if name !="":
            print('TELNET = OK')
            return 1

        else:
            print ('TELNET = NOT OK')
            return 0  

        tn.close()

    except:
        print ('TELNET = NOT OK')
        return 0
   
################################   Función para validar puerto abierto   ######################
def port_open(ip):
    # Validar puerto 8291
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((ip,8291))

        if result == 0:
            print("Wimbox-8291 is open")
            port_8291=1
        else:
            print("Wimbox-8291 is close")
            sock.close()
            port_8291=0

    except:
        print ('Puerto = NOT OK')
        port_8291=0

    # Validar puerto 8299
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((ip,8299))

        if result == 0:
            print("Wimbox-8299 is open")
            port_8299=1
        else:
            print("Wimbox-8299 is close")
            sock.close()
            port_8299=0

    except:
        print ('Puerto = NOT OK')
        port_8299=0

    # Validar puerto 8292
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((ip,8292))

        if result == 0:
            print("Wimbox-8292 is open")
            port_8292=1
        else:
            print("Wimbox-8292 is close")
            sock.close()
            port_8292=0

    except:
        print ('Puerto = NOT OK')
        port_8292=0


    # Validar puerto API
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((ip,8728))

        if result == 0:
            print("API is open")
            api=1
        else:
            print("API is close")
            sock.close()
            api=0

    except:
        print ('Puerto = NOT OK')
        api=0

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((ip,22))

        if result == 0:
            print("SSH is open")
            ssh=1
        else:
            print("SSH is close")
            sock.close()
            ssh=0

    except:
        print ('Puerto = NOT OK')
        ssh=0  

    try:
        ping_response = ping(ip)
        if isinstance(ping_response, float):
            print("PING--->UP")
            ping_status=1
        else:
            print("PING--->DOWN")
            ping_status=0
    except:
        print ('PING = NOT OK')
        ping_status=0

    return (api,ssh,ping_status,port_8291, port_8299, port_8292)    
          
############################## LLENAR BASE DE DATOS #############################################   
def insertBD (identity, ip, user1 , password, version, modelo, group, puerto, ping_status, var_ssh, var_api, var_port_8291, var_port_8299, var_port_8292):

    db = mysql.connect(
        host = "160.20.188.232",
        user = "remote",
        passwd = "M4ndr4g0r4!",
        database ="network" #Con esto se valida que la base de datos existe, de no existir, arroja error
    )

    databases = db.cursor() #Mi puntero para ubicarme en la BD

    databases.execute("SHOW DATABASES")# preparate para ejecutar esta linea
    #databases = databasesfetchall() #no tengo idea aun ;) hehe xd
    #print(databases)

    for x in databases:
        print(x)

    query = 'DELETE FROM network.devices WHERE ip ="'+ip+'"'
   # '/user print terse where name="'+username+'"'
    databases.execute(query)
    db.commit()

    query = "INSERT INTO devices (identity, ip,user ,password, version, modelo ,grupo, puertoacceso, ping_status, ssh_status, api_status, var_port_8291, var_port_8299, var_port_8292) VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    values = (identity, ip, user1 , password, version, modelo, group, puerto, ping_status, var_ssh, var_api, var_port_8291, var_port_8299, var_port_8292)
    databases.execute(query, values) #Ejecuta la tarea indicada
    db.commit() #Deja de forma permanente los cambios efectuados anteriormente, los guarda como los equipos UBNT
    print(databases.rowcount, "record inserted") #imprime cuantas filas fueron modificadas

############################ VALIDAR USER GROUP #############################################   
def user_group(ip,user1,password):
   #API
    try:
        api=''
        mikrotik=''
        name=user1
        group=''
        identity=''

        #Extraccion identity
        del api
        del mikrotik
        api = connect(username=user1, password=password, host=ip)
        mikrotik = api.path('system', 'identity')
        for row in mikrotik:
            identity=row.get('name')

        #Extraccion version
        del api
        del mikrotik
        api = connect(username=user1, password=password, host=ip)
        mikrotik = api.path('system', 'resource')
        for row in mikrotik:
            version=row.get('version')
            #print('version--->'+version)

        #Extraccion Modelo
        del api
        del mikrotik
        api = connect(username=user1, password=password, host=ip)
        mikrotik = api.path('system', 'resource')
        for row in mikrotik:
            model=row.get('board-name')
            #print('Board Name--->'+model)

        #Extraccion grupo
        del api
        del mikrotik
        api = connect(username=user1, password=password, host=ip)
        mikrotik = api.path('user').select('name', 'group').where(Key('name') == name)
        for row in mikrotik:
            group=row.get('group')
            #print('GROUP--->'+group)
            break
        
        if identity!='' and group!='' and version!='' and model!='':
            return group, identity, version, model
            
    except:
        # SSH  para encender API#
        ip= ip
        username= user1
        password= password
        cmd = '/ip service enable [find where name=api]'
        
        ssh=paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip,22,username,password)
     
        #Encendiendo API
        stdin,stdout,stderr=ssh.exec_command(cmd)
        api_on=stdout.readlines()

## SSH
    try:
        
        # SSH #
        ip= ip
        username= user1
        password= password
        cmd = '/user print terse where name="'+username+'"'
        cmd1 = '/system identity print'
        cmd2 = '/system resource print'
        
        ssh=paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip,22,username,password)
     

        #GRUPO
        stdin,stdout,stderr=ssh.exec_command(cmd)
        outlines=stdout.readlines()
        outlines=outlines[0]
        

        #IDENTITY SSH
        stdin,stdout,stderr=ssh.exec_command(cmd1)
        identity_ssh=stdout.readlines()
        identity_ssh=identity_ssh[0]
        identity_ssh=identity_ssh.split('name: ')[1]

        #VERSION
        stdin,stdout,stderr=ssh.exec_command(cmd2)
        version_ssh=stdout.readlines()
        version_ssh=version_ssh[1].split('version:')[1].strip()

        #Modelo
        stdin,stdout,stderr=ssh.exec_command(cmd2)
        modelo_ssh=stdout.readlines()
        modelo_ssh=modelo_ssh[13]
        modelo_ssh=modelo_ssh.split('board-name:')[1].strip()
        
        if 'group=full' in outlines:
            group='full'
            return group, identity_ssh, version_ssh, modelo_ssh

    except:
        print ('') 

###############################  LOGIN  ######################################

def login(ip, puerto,ping_status):
    try:
        user_password_list = []
        for i in ['admin','tfa','austro','jedis']:#'xxx',
            for j in ['N0s31717!','N0s31717','austro2018','austro2019','B9s31717!!.','B0s31818!!.','B8s31717!!.','austro']:
                user_password_list.append((i,j))
                
        
        for row in user_password_list:
            user1=row[0]
            password=row[1]
            print(user1+'-->'+password)

            grupo_identity_tupla = user_group(ip, user1, password)

            if grupo_identity_tupla is None:
                print('No es posible conectar con este usuario y contraseña')

                if ping_status!='':
                    insertBD ('Sin identity', ip, 'Ningun user funciona' , 'Ningun Password funciona','NoVersion','NoModel','None', '--', ping_status, var_ssh, var_api, var_port_8291, var_port_8299, var_port_8292)
            else: 
                grupo1=grupo_identity_tupla[0]
                identity1=grupo_identity_tupla[1]
                version=grupo_identity_tupla[2]
                modelo=grupo_identity_tupla[3]
                print('GROUP: '+ grupo1)
                print('IDENTITY: '+ identity1)
                print('VERSION: '+ version)
                print('MODELO: '+ modelo)



                if grupo1=='full':
                    insertBD (identity1, ip, user1 , password, version, modelo, grupo1, puerto, ping_status, var_ssh, var_api, var_port_8291, var_port_8299, var_port_8292)
                    break       
                    #exit()
          

    except:
        print ('')
        return 0        
################################################################################

# if len(sys.argv) == 2:
#     ip=sys.argv[1]
#     puertos=port_open(ip)
#     ping_status=puertos[2]
# else:
#     exit()
ip='2.3.4.5'
puertos=port_open(ip)
var_api=puertos[0]
var_ssh=puertos[1]
var_ping=puertos[2]
var_port_8291=puertos[3]
var_port_8299=puertos[4]
var_port_8292=puertos[5] 

if puertos==(0,0,0):
    #print('API= OFF, SSH= OFF, PING= OFF')
    exit()

elif puertos==(0,0,1):
    #print ('PING-->OK')
    insertBD ('Sin Identity',ip, "Sin Usuario" , "Sin clave","NoVersion","NoModel", "Sin grupo", 0, var_ping, var_ssh, var_api, var_port_8291, var_port_8299, var_port_8292)
    exit()

elif puertos[0]==1:
    #print('API--> OK')
    login(ip,8728, var_ping)

elif puertos[1]==1:
    #print('SSH--> OK')
    login(ip,22, var_ping)


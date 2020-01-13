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

############################# API ############################################    
def api1(ip, user, password):

    try:

        api = connect(
                username= user,
                password= password,
                host= ip
            )

        #Extraccion identity
        identity_api = api.path('system', 'identity')
        identity_api = list( identity_api)
        
        for  x in identity_api:
            identity_api=x
            print(identity_api)
        
        if identity_api !="":
            print('API = OK')
            return 1
            
        else:
            print ('API = NOT OK')
            return 0
    except:
        print ('API = NOT OK')
        return 0

##########################  SSH   ######################################       
def ssh(ip, user, password):
    
    try:
            
        # MikroTik #
        ip= ip
        port=22
        username= user
        password= password

        cmd = '/system identity print'

        ssh=paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip,port,username,password)

        stdin,stdout,stderr=ssh.exec_command(cmd)
        outlines=stdout.readlines()
        resp=''.join(outlines)
        #print(resp)

        if resp !="":
            print('SSH = OK')
            return 1

        else:
            print ('SSH = NOT OK')
            return 0    
            
    except:
        print ('SSH = NOT OK')
        return 0

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

    return (api,ssh,ping_status)    
          
############################ LLENAR BASE DE DATOS #############################################   
def insertBD (identity, ip, user1 , password, group, puerto, ping_status, var_ssh, var_ping):

    db = mysql.connect(
        host = "10.67.125.241",
        user = "root",
        passwd = "root",
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

    query = "INSERT INTO devices (identity, ip,user ,password ,grupo , puertoacceso, ping_status, ssh_status, api_status) VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s)"
    values = (identity, ip, user1 , password, group, puerto, ping_status, var_ssh, var_ping)
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
        del api
        del mikrotik
        api = connect(username=user1, password=password, host=ip)

         #Extraccion identity
        identity_api = api.path('system', 'identity')
        identity_api = list( identity_api)
        
        for  x in identity_api:
            identity_api=x
            identity_api= identity_api.get('name')

        #user = api.path('user')
        mikrotik = api.path('user').select('name', 'group').where(Key('name') == name)
        for item in mikrotik:
           
            group=item.get('group')
            print('GROUP--->'+group)
            return group, identity_api
            
    except:
        print ('')
## SSH
    try:
        # SSH #
        ip= ip
        username= 'xxx'#user1
        password= 'xxx'#password
        cmd = '/user print terse where name="'+username+'"'
        cmd1 = '/system identity print'

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
        
        print(identity_ssh)
        if 'group=full' in outlines:
            print('Entra3')
            group='full'
            print('GROUP-->' +group)
            return group, identity_ssh

    except:
        print ('') 

###############################  LOGIN  ######################################

def login(ip, puerto,ping_status):
    try:
        user_password_list = []
        for i in ['admin','tfa','austro','jedis']:
            for j in ['N0s31717!','N0s31717','austro2018','austro2019','B9s31717!!.','B0s31818!!.','B8s31717!!.','austro','austro2018','austro2019']:
                user_password_list.append((i,j))
                
        
        for row in user_password_list:
            user1=row[0]
            password=row[1]
            print(user1+'-->'+password)

            grupo =user_group(ip, user1, password)
            print (grupo)
            print(type(grupo))
            grupo=grupo[0]
            #####TERMINAR 
            print(grupo)
            print(identity)


            if grupo=='full':
                insertBD (identity, ip, user1 , password, grupo, puerto, ping_status, var_ssh, var_api)
            
                break       

    except:
        print ('')
        return 0        
################################################################################

# if len(sys.argv) == 2:
#     ip=sys.argv[1]
#     puertos=port_open('2.3.4.5')
#     ping_status=puertos[2]
# else:
#     exit()
ip='2.3.4.5'
puertos=port_open(ip)
var_api=puertos[0]
var_ssh=puertos[1]
var_ping=puertos[2]

if puertos==(0,0,0):
    print('API= OFF, SSH= OFF, PING= OFF')
    exit()

elif puertos==(0,0,1):
    print ('PING-->OK')
    insertBD (ip, "Sin Usuario" , "Sin clave", "Sin grupo", 0,var_ping,var_ssh,var_api)
    exit()

elif puertos[0]==1:
    print('API--> OK')
    login(ip,8728, var_ping)

elif puertos[1]==1:
    print('SSH--> OK')
    login(ip,22, var_ping)
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

        #Extraccion de address list:
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
def insertBD (ip, user1 , password, group, puerto, ping_status):

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

    query = "INSERT INTO devices (ip,user ,password ,grupo ,puerto,ping_status) VALUES (%s, %s, %s, %s, %s, %s)"
    values = (ip, user1 , password, group, puerto, ping_status)
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
        #user = api.path('user')
        mikrotik = api.path('user').select('name', 'group').where(Key('name') == name)
        for item in mikrotik:
           
            group=item.get('group')
            print('GROUP--->'+group)
            return group
            
    except:
        print ('')
## SSH
    try:
        # SSH #
        ip= ip
        username= user1
        password= password
        print("Entra")
        cmd = 'user print terse where name="'+user1+'"'

        ssh=paramiko.SSHClient()
        
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        ssh.connect(ip,22,username,password)
       
        stdin,stdout,stderr=ssh.exec_command(cmd)
        outlines=stdout.readlines()

        if 'group=full' in outlines:
            #ddsadxsasd

        grupo_ssh=''.join(outlines)
        print(grupo_ssh)
        grupo_ssh=grupo_ssh.split(' ')
        print(grupo_ssh)
        print(type(grupo_ssh))
        print(type(tupla))
     
        print('GROUP--->'+grupo_ssh)
        return group
            
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

            grupo =user_group(ip, 'xxx', 'xxx')

            if grupo=='full':
                insertBD (ip, user1 , password, grupo, puerto,ping_status)
                break
            
                
        # if acceso =='ok':
        #     exit()
    
        # else:
        #     return 

            # ping_value= check_host_ping(ip)
            # api_value= api1 (ip, user1, password)
            # ssh_value= ssh (ip, user1, password)
            
            # cont=ping_value+api_value+ssh_value+port_open1
            # #telnet_value= telnet(ip, user1, password)
            

            # if api_value == 1 or ssh_value ==1 or ping_value==1:
            #     insertBD (ip, user1 , password, api_value, ssh_value, ping_value,port_open1 , cont)            

    except:
        print ('')
        return 0        
################################################################################

# if len(sys.argv) == 2:
#     ip=sys.argv[1]
#     login('2.3.4.5')
ip='2.3.4.5'
puertos=port_open(ip)
ping_status=puertos[2]



if puertos==(0,0,0):
    print('API= OFF, SSH= OFF, PING= OFF')
    exit()

elif puertos==(0,0,1):
    print ('PING-->OK')
    insertBD (ip, "Sin Usuario" , "Sin clave", "Sin grupo", 0, ping_status)
    exit()

elif puertos[0]==1:
    print('API--> OK')
    login(ip,8728, ping_status)

elif puertos[1]==1:
    print('SSH--> OK')
    login(ip,22, ping_status)
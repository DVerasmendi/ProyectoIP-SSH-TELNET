#API
from librouteros import connect
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
#############################
ip='2.3.4.5'
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
################################    Función para hacer ping    ################################
def check_host_ping (domain=""): 
    try:
        ping_response = ping(domain)
        if isinstance(ping_response, float):
            print("PING--->UP")
            return (1)
        else:
            print("PING--->DOWN")
            return (0)
    except:
        print ('PING = NOT OK')
        return 0       
################################   Función para validar puerto abierto   ######################
def port_open(ip):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((ip,8291))
        if result == 0:
            print("Port is open")
            return 1
        else:
            print("Port is close")
            sock.close()
            return 0
    except:
        print ('PING = NOT OK')
        return 0        
############################ LLENAR BASE DE DATOS #############################################   
def insertBD (ip, user1 , password, api_value, ssh_value, ping_value, port_open, cont):

    db = mysql.connect(
        host = "127.0.0.1",
        user = "root",
        passwd = "",
        database ="network" #Con esto se valida que la base de datos existe, de no existir, arroja error
    )

    databases = db.cursor() #Mi puntero para ubicarme en la BD

    databases.execute("SHOW DATABASES")# preparate para ejecutar esta linea
    #databases = databases.fetchall() #no tengo idea aun ;) hehe xd
    #print(databases)

    for x in databases:
        print(x)

    query = "INSERT INTO devices (ip,user ,password ,api ,ssh ,ping, port_open, cont) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    values = (ip, user1 , password, api_value, ssh_value, ping_value, port_open, cont)
    databases.execute(query, values) #Ejecuta la tarea indicada
    db.commit() #Deja de forma permanente los cambios efectuados anteriormente, los guarda como los equipos UBNT
    print(databases.rowcount, "record inserted") #imprime cuantas filas fueron modificadas



###############################  LOGIN  ######################################

def login(ip):
    try:
        user_password_list = []
        for i in ['admin','tfa','austro','jedis']:
            for j in ['N0s31717!','N0s31717','austro2018','austro2019','B9s31717!!.','B0s31818!!.','B8s31717!!.','austro','austro2018','austro2019']:
                user_password_list.append((i,j))
                
        
        #print(user_password_list)

        for row in user_password_list:
            user1=row[0]
            password=row[1]
            print(user1+'-->'+password)
            ping_value= check_host_ping(ip)
            api_value= api1 (ip, user1, password)
            ssh_value= ssh (ip, user1, password)
            port_open1= port_open(ip)
            cont=ping_value+api_value+ssh_value+port_open1
            #telnet_value= telnet(ip, user1, password)
            

            if api_value == 1 or ssh_value ==1 or ping_value==1:
                insertBD (ip, user1 , password, api_value, ssh_value, ping_value,port_open1 , cont)
                

    except:
        print ('')
        return 0        
################################################################################
login(ip)

# Import del modulo dei socket
import socket 
import sys
# import moduli thread
from _thread import *
import threading 
import time

#Lettura cache
def readFile():
    try:
        f = open("msg.txt","r")
        for x in f:
            #print(x)
            archivio.append(x)
        f.close()
    except :
        return
        
        
#Invio del messaggio in broadcast (solo ai client connessi all'attuale server)

def broadcast(messageToSend,conn):
    for clients in list_of_clients: 
        #Controllo se il client a cui mandare il messaggio e' diverso da quello della connessione
        if clients!=conn: 
            try: 
                clients.send(messageToSend.encode('utf-8')) 
            except: 
                '''
                Se non riuscissi ad inviare il messaggio chiudo la connessione ed elimino il client
                Questo significa che il client ha perso la connessione con me
                '''
                clients.close() 
                list_of_clients.remove(clients) 
                                    
                                    
                                    
#Funzione che gestisce tutta la connessione del client     
def send(msg,client):
    print("SEND")
    lista = list_of_clients.copy()
    lista.pop(0)
    for y in lista:
        if(y!=client):
            try:
                y.send((msg).encode('utf-8')) 
            except: 
                #NON C'E' NESSUN CLIENT
                y.close() 
                list_of_clients.remove(y) 
                lista.remove(y)
               # print(len(list_of_clients))
                print("EXCEPT")       
                
def clientthread(conn, addr,backup): 
    try:
        num = len(list_of_clients)#Prendo il numero dei client connessi
            
        if(num >= 2):#Se maggiore di due, poiche' uno slot sara' sempre occupato dal server di backup
            if(conn != backup):
                print("numero di client",num)#debug
                conn.send(num.to_bytes(1,byteorder="big"))#Invio il numero in modo da poter gestire lato client
        #Prendo il nick del client che si vuole connettere
        nick = conn.recv(2048).decode('utf-8')
        
        if(nick.lower() != "backup"):
            #Gli do il benvenuto 
            msg = "BENVENUTO NELLA CHAT "+nick.upper()+"!!\n"
            conn.send(msg.encode('utf-8'))
            if len(archivio):
                for x in archivio:
                    y = x+"\n"
                    conn.send(y.encode('utf-8'))
        else:
            print("CONNESSIONE DI BACKUP")
        
    except:
        print("startup connessione")
     

        
    #Ciclo infinito per gestire tutti i messaggi
    while True: 

            try:
                message = conn.recv(2048) 
                if len(message): 
                    #print(message.decode('utf-8')!= "exit")
                    if message.decode('utf-8') != "exit":
                        #Se c'e' un messaggio vado avanti e' formatto il messaggio da visualizzare
                        messageToSend = "<" + nick + "> " + message.decode('utf-8')
                        #stampo per debug il messaggio da visualizzare
                        print (messageToSend)
                        archivio.append(messageToSend)
                        #prova di cache DEBUG
                        f = open("msg.txt","a")
                        f.write(messageToSend+"\n")
                        f.close() 
                        print(archivio)
                        #Invio in modo broadcast il messaggio a tutti i clients
                        broadcast(messageToSend,conn)
                    else:
                        #Negozio la chiusura
                        x = "exit"
                        conn.send(x.encode('utf-8')) 
                        conn.close()
                        list_of_clients.remove(conn)
                        #Controllo ci siano ancora client
                        if not len(list_of_clients):
                            print("NESSUN CLIENT CHIUDO TUTTO")
                            break
                else:                   
                    #Ci sara' stato un errore nella connessione e/o nella ricezione del messaggio quindi scarto il client
                    list_of_clients.remove(conn)
                              
            except: 
                continue
def sync (client):
    try:
        client.connect((hostOutput, int(outputPort)))
        return True        
    except:
        print("BACKUP NON CONNESSO")
        

#Serve per la sincronizzazione dei messaggi in ricezione e sfrutta un altro thread
def syncro(client):
    while True:
        try:
            x = client.recv(1024).decode('utf-8')
            archivio.append(x)
            print(archivio)
            msgLen = len(archivio)
            print(msgLen)
            send(x,client)
        except : 
            continue
       
nomeScript,address, inputPort,addressOutput, outputPort = sys.argv
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
archivio = []
readFile()
msgLen = 0

""" 
Lego il server ad uno specifico IP ed una specifica porta
Il client avra' questi parametri
"""
hostInput = address 
hostOutput = addressOutput
server.bind((hostInput, int(inputPort))) 



#Il server puo' ascoltare fino a 100 utenti contemporanemente dopodiche' la connessione verra' rifiutata

server.listen(100) 
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
list_of_clients = [] 

while sync(client) != True :
    print("BACKUP NON CONNESSO CONNETTERE PREGO ")
    time.sleep(2)
    
#list_of_clients.append(client) 
client.send("backup".encode('utf-8'))
#archivio.clear()
print(archivio)
while True: 
    
    '''
    Accetto tutte le richieste e le conservo in due parametri
    conn che mi rappresenta il socket per l'utente ed addr che rappresenta l'indirizzo
    '''
    conn, addr = server.accept() 
    
    #Faccio una lista di client cosi poi da mandare in broadcast a tutti i messaggi
    list_of_clients.append(conn) 
    #print(list_of_clients)
    
    #Stampo per debug la porta di chi si e' connesso
    print (addr[1], " connected")
  
    # Creo un thread per ogni client che si connette  
    start_new_thread(clientthread,(conn,addr,client)) 
    time.sleep(2)
    start_new_thread(syncro,(client,))
    
#Chiudo le connessioni
conn.close() 
server.close() 
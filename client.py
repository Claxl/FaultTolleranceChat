from tkinter import Tk, Frame, Scrollbar, Label, END, Entry, Text, VERTICAL, Button, messagebox #Tkinter Python Module for GUI  
import socket 
import threading 
import sys

nomeScript, address,port, swapArg = sys.argv #Prendo gli argv dalla linea di comando


class GUI:
    clientSocket = None
    
    def __init__(self, master):
        self.root = master
        self.textBoxLayer = None
        self.username = None
        self.chatBoxLayer = None
        self.joinButton = None
        self.PORT = 0
        self.HOST = ""
        self.initialize_socket(1)
        self.gui_Initializer()
        self.receive_Thread()
        
    #Serve per cambiare le porte
    def port_Switch(self):
        if(self.PORT == 8080):
                self.PORT = 8081
        elif(self.PORT == 8081):
                self.PORT = 8080
    #Serve per avere il nuovo indirizzo di connessione
    def new_Address(self):
        self.HOST = input("Inserisci il nuovo indizzo")
        
    #Inizializza il socket
    def initialize_socket(self,status):
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.HOST = address # IP address 
        if(status == 1):
            self.PORT = int(port) #Metto la porta presa dalla linea di comand 
        else:
            self.port_Switch()
            print("First")
            print(self.PORT)
            if(int(swapArg)>0):
                self.new_Address()
        print("Second")
        print(self.PORT)
        self.clientSocket.connect((self.HOST, self.PORT)) #mi connetto alla socket
        x = int.from_bytes(self.clientSocket.recv(2048),byteorder ="big")#Vedo quanti utenti ci sono connessi
        print(x)#Debug
        if(x>50):#Numero limite di gestione congestione
            self.clientSocket.close()#chiusura connessione
            if(int(swapArg) == 0):
                #Swap di porte
                self.port_Switch()
                #nuova creazione di socket
            elif(int(swapArg) == 1):
                self.new_Address()
                self.port_Switch()
            else:
                self.new_Address()
            self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # initialazing socket with TCP and IPv4
            self.clientSocket.connect((self.HOST, self.PORT)) #connect to the remote server
    
    # Serve ad inizializzare la grafica
    def gui_Initializer(self): 
        self.root.title("Progetto Reti") 
        self.chatBox()
        self.username_Section()
        self.textBox()
    #Funzione per startare il tread
    def receive_Thread(self):
        thread = threading.Thread(target=self.receive_Message) 
        thread.start()

    #Funzione per ricevere tutti i messaggi, viene invocata dalla funzione sopra, questo thread riceve i messaggi
    #e li stampa nella textBox
    def receive_Message(self, ):
        try:
            self.clientSocket.settimeout(200)
            while True:
                try:
                    buffer = self.clientSocket.recv(256)
                    if not buffer:
                        break
                    message = buffer.decode('utf-8')
                    #il server ha accettato la chiusura
                    if(message == 'exit'):
                        #termino tutto
                        sys.exit()
                    self.textBoxLayer.insert('end', message + '\n')
                    self.textBoxLayer.yview(END)
                except:#Significa che e' scaduto il timeout                 
                    print("EXCEPT")
        except:
            self.clientSocket.close()
            self.initialize_socket(0)#inizializzo il socket affinche' si connetti al nuovo server
                
    #Creazione della casella dove scrivere il nome
    def username_Section(self):
        frame = Frame()#casella
        Label(frame, text='NOME UTENTE:', font=("Helvetica", 16)).pack(side='left', padx=10)#scritta
        self.username = Entry(frame, width=50, borderwidth=2)
        self.username.pack(side='left', anchor='e')
        self.joinButton = Button(frame, text="ENTRA", width=10, command=self.on_NameSend).pack(side='left')
        frame.pack(side='top', anchor='nw')
        
    #Creazione della casella dove verra' visualizzato il messaggio
    def textBox(self):
        frame = Frame()
        self.textBoxLayer = Text(frame, width=60, height=10, font=("Serif", 12))
        scrollbar = Scrollbar(frame, command=self.textBoxLayer.yview, orient=VERTICAL)
        self.textBoxLayer.pack(side='left', padx=10)
        scrollbar.pack(side='right', fill='y')
        frame.pack(side='top')
        
    #Creazione della casella dove scrivere il messaggio 
    def chatBox(self):
        frame = Frame()
        self.chatBoxLayer = Text(frame, width=60, height=3, font=("Serif", 12))
        self.chatBoxLayer.pack(side='left', pady=15)
        self.chatBoxLayer.bind('<Return>', self.on_TextSend)
        self.sendButton = Button(frame, text="INVIO", width=10, command=self.on_TextSend).pack(side='left')
        frame.pack(side='top')
        
        
    #Gestione invio dell nome
    def on_NameSend(self):
        self.username.config(state='disabled')
        self.clientSocket.send((self.username.get()).encode('utf-8'))
        
        
    #viene invocata alla pressione del button invio cosi da attivare la procedura di gestione
    def on_TextSend(self):
        self.send_MSG()
        self.clear_ChatBox()
    #pulizia textBox
    def clear_ChatBox(self):
        self.chatBoxLayer.delete(1.0, 'end')
    #Gestione textBox per invio messaggi
    def send_MSG(self):
        try:
            senders_name = self.username.get().strip() + ": "
            data = self.chatBoxLayer.get(1.0, 'end').strip()
            if(data == "exit"):
                self.root.destroy()
                self.clientSocket.close()
                exit(0)
            message = data.encode('utf-8')
            self.textBoxLayer.insert('end', (senders_name + data) + '\n')
            self.textBoxLayer.yview(END)
            self.clientSocket.send(message)
            self.chatBoxLayer.delete(1.0, 'end')
            return 'break'
        except:
            self.clientSocket.close()
            self.initialize_socket(0)


root = Tk()
gui = GUI(root)
root.mainloop()
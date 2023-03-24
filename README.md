# REALIZZAZIONE DI UN SERVIZIO DI CHAT COOPERATIVO CON DUE SERVER CHE GARANTISCONO BILANCIAMENTO DEL CARICO E FAUL TOLERANCE




Il progetto consiste nella creazione di un’applicazione Client e di un’applicazione Server che realizzano il servizio di Chat su spazio condiviso tra gli utenti.

Il programma Client è a conoscenza dell’indirizzo del Server, per cui la connessione è completamente trasparente all’utente del servizio.
Quando avviene la connessione, il processo server la gestisce attraverso un processo leggero thread creato per tale funzione, l’astrazione di canale di comunicazione è definita attraverso una Socket  di tipo TCP.
I messaggi che pervengono dai vari Client sono memorizzati dal Server in un’area di memoria comune a tutti i thread in modo che ciascun nuovo messaggio possa essere poi spedito dai gestori dei singoli canali di comunicazione ai relativi Client per poi essere letto dagli utenti.

L’archivio dei messaggi si può pensare che sia strutturato in modo sequenziale con accesso random sfruttando l’indice che permette di accedere a qualunque messaggio nella posizione individuata dall’indice stesso.
E’ possibile pensarlo come ad una matrice costituita da due colonne di cui ciascuna riga costituisce un messaggio della Chat.
La prima colonna rappresenta il proprietario del messaggio, la seconda colonna di dimensioni molto più estese rappresenta il corpo del messaggio.

Ciascun processo thread sul Server possiede due contatori:
il primo contatore chiamato Messaggi Archivio (MA) conta i messaggi presenti nell’archivio comune, ed è sempre aggiornato allorché sopraggiungano al Server uno o più  nuovi messaggi;
il secondo contatore chiamato Messaggi Trasferiti (MT) conta i messaggi giunti dal Client o trasmessi al Client.
Affinché un Client sia aggiornato con tutti i messaggi pervenuti alla Chat i due contatori devono contenere lo stesso valore, il quale poi è anche il numero totale dei messaggi contenuti nell’archivio.

Quando giunge un nuovo messaggio il processo che lo riceve lo deposita nell’area di memoria comune e segnala tale evento in modo che ciascun altro thread presente sul server può andarlo a leggerlo.
Quando un nuovo Client si collega gli vengono mandati tutti i messaggi dell’archivio.



Si ipotizza che quando il servizio entra in funzione entrambi i Server sono attivi e questi possono essere sulla stessa macchina oppure su due macchine diverse.
La gestione del servizio può essere così strutturata: un Client si connette sempre utilizzando un indirizzo che si può pensare attribuito al Server Primario ma comunque è a conoscenza anche dell’indirizzo del Server Secondario.
Se al primo Server sono connessi meno di 100 utenti (parametro questo variabile) il Client mantiene la connessione con questo gestore altrimenti è data indicazione di connettersi al secondo.
Entrambi i Server forniscono lo stesso servizio e devono essere allineati come numero di messaggi, per questo quando si attivano creano un canale di comunicazione tra loro per scambiarsi i messaggi in arrivo dalle rispettive connessioni con i Client che poi saranno salvati nella loro memoria archivio.
Quando uno dei due Server riceve un messaggio da un Client questo è spedito all’altro gestore che provvede ad inserirlo nel proprio archivio e a segnalare tale evento ai propri thread che lo leggeranno per poi spedirlo ai propri Client.
Così facendo entrambi i Server cooperano per fornire il servizio di messaggeria e con il protocollo sopra esposto riescono a bilanciarsi il carico in termini di numero massimo di clienti.
Con questo tipo di gestione esistono due tipologie di flusso di dati:
il primo flusso inerente lo scambio di messaggi tra Server ovvero singolo thread sul gestore e Client remoto;
il secondo flusso tra i due Server che scambiandosi i messaggi pervenuti dai rispettivi Client garantiscono che sui due archivi sono memorizzati gli stessi messaggi.

Se in un certo istante uno dei due gestori “cade” le entità che sentono tale evento sono i Client ad esso connessi e l’altro gestore (quest’ultimo rilevando l’interruzione del collegamento chiude il canale che lo connetteva all’altro suo pari). A seguito di tale guasto i Client che gli erano connessi possono automaticamente ricollegarsi all’altro Server. 
Infatti ciascun Client possiede entrambi gli indirizzi dei due Server per cui a seconda di quello che stava utilizzando nella connessione, per ripristinare il collegamento utilizza l’altro.
Nel momento in cui il Client si ricollega al Server funzionante riceve nuovamente tutti i messaggi dell’archivio della macchina a cui si è collegato, si ipotizza infatti che quando un Client interrompe il collegamento con il proprio gestore resetta la propria memoria locale dei messaggi.
In una situazione di questo tipo viene effettuato il recovery del servizio a seguito della caduta di uno dei due Server ma ovviamente si perde il bilanciamento del carico poiché un solo gestore si fa carico di tutto il traffico con i Client e della gestione del Servizio.

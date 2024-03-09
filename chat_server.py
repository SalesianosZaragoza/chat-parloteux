import socket
import threading
import psutil

# Configuración del servidor
host = ''
port = 65000

# Crear un socket del servidor
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))


# Función para para filtrar las direcciones IP
def filter_address(item):
    if item[1][0].address in ['127.0.0.1', 'localhost'] or item[1][0].family != socket.AF_INET or item[1][0].netmask == '255.255.0.0':
        # ___TEMPORAL___ el bloqueo de las IPs con mascara de red 255.255.0.0 es temporal mientras desarrollemos la app
        return False
    else:
        return True


# print("Servidor iniciado con la dirección IP: " + )
server.listen()
host_addr = psutil.net_if_addrs()
print("Servidor iniciado con las direcciones IP: ")
try:
    filtered_addresses = filter(filter_address, host_addr.items())
except Exception as e:
    print(e)
for address in filtered_addresses:
    print(address[0], address[1][0].address)


# Lista para almacenar clientes conectados
clients = []
usernames = []

#Constantes

RESET = "\x1b[0m"
BOLD = "\x1b[1m"
BLACK = "\x1b[30m"
RED = "\x1b[31m"
GREEN = "\x1b[32m"
YELLOW = "\x1b[33m"
BLUE = "\x1b[34m"
MAGENTA = "\x1b[35m"
CYAN = "\x1b[36m"
WHITE = "\x1b[37m"
BGBLACK = "\x1b[40m"
BGRED = "\x1b[41m"
BGGREEN = "\x1b[42m"
BGYELLOW = "\x1b[43m"
BGBLUE = "\x1b[44m"
BGMAGENTA = "\x1b[45m"
BGCYAN = "\x1b[46m"
BGWHITE = "\x1b[47m"

SAVE_CURSOR = "\x1b7"
RESTORE_CURSOR = "\x1b8"
MOVE_CURSOR_BEGINNING_PREVIOUS_LINE = "\x1b[F"
CLEAR_ENTIRE_LINE = "\x1b[2K"

colours = [GREEN, YELLOW, BLUE, MAGENTA, CYAN]

# Función para enviar mensajes a todos los clientes
def broadcast(clientMessage, clientUsername, client):
    for c in clients:
        messageFormatted = SAVE_CURSOR + MOVE_CURSOR_BEGINNING_PREVIOUS_LINE + CLEAR_ENTIRE_LINE
        if c != client:
            if clientUsername == "Server":
                messageFormatted += RED + BOLD 
            else:
                i = usernames.index(clientUsername) % len(colours)
                messageFormatted += colours[i] + BOLD
        else:
            messageFormatted += WHITE

        messageFormatted += clientUsername + ':' + RESET + ' ' + clientMessage  + RESTORE_CURSOR
        
        try:
            c.send(messageFormatted.encode('utf-8'))
        except:
            # Eliminar el cliente si hay un problema al enviar el mensaje
            remove(c)


#Función para enviar un mensaje a un sólo cliente

def soloMessage(message, client):
    # en orden: guardar la posición del cursor, mover el cursor al principio de la línea anterior (la línea en blanco encima),
    # escribir el mensaje a enviar y volver a poner el cursor donde estaba (el principio de una línea, a mitad de escribir...)
    messageFormatted = SAVE_CURSOR + MOVE_CURSOR_BEGINNING_PREVIOUS_LINE + message + RESTORE_CURSOR
    try:
        messageFormatted = messageFormatted.encode('utf-8')
        client.send(messageFormatted)
    except Exception as e:
        print(f"Se produjo una excepcion mientras se mandaba un mensaje al cliente {client}: {e}")
        remove(client)


# Función para enviar mensajes a un cliente como respuesta a sus acciones, antes de soloMessage para tener más
# flexibilidad y quitar la lógica de formateo de mensajes de las demás funciones funciones
def clientFeedback(message, client):
    message = RED + message + RESET
    soloMessage(message, client)


# Función para manejar la conexión de un cliente
def handle(client):
    while True:
        try:
            # Recibir mensaje del cliente
            message = client.recv(1024)

            # Verificar si el mensaje está vacío, lo que indica que la conexión se ha cerrado
            if not message:
                # Eliminar y cerrar la conexión del cliente
                remove(client)
                break

            # Decodificar y procesar el mensaje
            message = message.decode('utf-8')
            clientUsername = message.split(': ', 1)[0]
            clientMessage = message.split(': ', 1)[1]

            """ Prints de debug para la separación de mensajes
            print("message:", message)
            print(
                f"cliente {clientUsername} envía el mensaje: {clientMessage}")
            print("client:", client)
            print("clientUsername:", clientUsername)
            print("clientMessage:", clientMessage)
            print("clients:", clients)
            """
            print(f"cliente {clientUsername} envía el mensaje: {clientMessage}")
            print("Clientes conectados:", len(clients))

            
            if clientMessage.startswith('/'):
                checkCommand(clientMessage, clientUsername, client)
            else:
                clientMessage = checkContent(clientMessage)
                broadcast(clientMessage, clientUsername, client)

        except Exception as e:
            print(f"Error en handle: {e}")
            if client not in clients:
                break

# Función de control de comandos


def checkCommand(clientMessage, clientUsername, client):
    print("es un comando")

    totalMessage = str.split(clientMessage, '/', 1)[1]
    # command, data = totalMessage.split(' ', 1)
    # print(command, data)

    if str.__contains__(totalMessage, ' '):
        command, data = totalMessage.split(' ', 1)
    else:
        command = totalMessage
        data = ""

    match command:
        case "susurrar":
            buildSusurro(clientMessage, data, clientUsername, client)

        case "testSolo":
            if clients.count != 0:
                soloMessage("testMensajeUnico", clients[0])
        
        case "cambioNombre":
            cambiarNombre(clientMessage, data, clientUsername, client)
        
        case "exit":
            remove(client)
        case _:
            broadcast(clientMessage, clientUsername, client)


# Función para recoger el remitente de un mensaje privado, formatear el mensaje y llamar a soloMessage()

def buildSusurro(clientMessage, data, clientUsername, client):
    if not str.__contains__(data, " "):
        print("formato de susurro incorrecto:" + clientMessage)
        clientFeedback("Formato de susurro incorrecto. El formato es '/susurrar < usernameReceptor > < mensaje >'", client)
        return
    
    receptorName: str = data.split(' ', 1)[0]
    message: str = data.split(' ', 1)[1]
    receptorIndex = -1
    
    #print("receptorName: _", receptorName,"_")
    try:
        receptorIndex = usernames.index(receptorName)
    except:
        print(f"usuario {receptorName} no encontrado")
        print("usernames:")
        print(usernames)
        clientFeedback("Usuario destinatario no encontrado", client)
        return
    
    messageFinal = "(" + clientUsername + " te susurra: " + message + ")"
    
    try:
        receptorClient = clients[receptorIndex]
    except:
        print("error asignando el client receptor, el index puede ser erróneo")
        print(f"{clientUsername} INTENTÓ susurrar a {receptorName} con el index {receptorIndex} el mensaje {messageFinal}")
        clientFeedback("Hubo un error inesperado mandando el mensaje", client)
        return
    
    print(f"{clientUsername} susurra a {receptorName} con el index {receptorIndex} el mensaje {messageFinal}")
    soloMessage(messageFinal, receptorClient)

# Función para comprobar el contenido del mensaje
def checkContent(clientMessage):
    clientMessage = checkEmoji(clientMessage)
    clientMessage = checkFuck(clientMessage)
    return clientMessage

#Diccionario de Emojis
EMOJI_DICT = {
    ":)": "😀",
    ":(": "😞",
    ":D": "😃",
    ":p": "😛",
    ":O": "😲",
    ";)": "😉",
    "<3": "❤️",
    ":*": "😘",
    ":'(": "😢",
    ":|": "😐",
    ":/": "😕",
    ":s": "😕",
    ":$": "🤑",
    ":L": "😆",
    ":U": "🙃",
    "XD": "😆",
    ":B": "😎",
    ":X": "🤐",
    ":P": "😜",
    ":T": "😓",
    "8)": "😎",
    ":o": "😮",
    "O:)": "😇",
    ":/": "😕",
    ":]": "😊",
    ":}": "😊",
    ":caca": "💩",
    ":fuego": "🔥",
}

#Función para comprobar emojis
def checkEmoji(clientMessage):
    for key, value in EMOJI_DICT.items():
        clientMessage = clientMessage.replace(key, value)
    return clientMessage

#Diccionario de palabras malsonantes
BAD_WORDS = {
    'joder' : 'practicar deporte en horizontal',
    'follar' : 'hacer bebes',
    'puta': 'persona con un trabajo complicado',
    'coño': 'la parte entre el ombligo y las rodillas (en femenino)',
    'chúpamela': 'no estoy de acuerdo contigo',
    'mierda': 'excremento',
    'cabrón': 'persona con mucho carácter',
    'gilipollas': 'persona con mucho carácter',
    'polla': 'ave',
    'pene': 'miembro viril',
    'verga': 'palo',
    'coger': 'agarrar',
    'culo': 'parte trasera',
    'zorra': 'animal',
    'maricón': 'persona con mucha sensibilidad',
    'puto': 'persona con un trabajo complicado',
    'Gorka': 'Dios',
    'Agustín': 'Un poco menos que Dios',
    'salesianos': 'la mejor escuela del mundo',
    'salesiano': 'persona con mucha suerte',
    'salesiana': 'persona con mucha suerte'
}
#Función para comproobar palabras malsonantes
def checkFuck(clientMessage):
    for word, replacement in BAD_WORDS.items():
        clientMessage = clientMessage.replace(word, replacement)
    return clientMessage


# Función para eliminar un cliente de la lista
def remove(client):
    if client in clients:
        index = clients.index(client)
        clients.remove(client)
        client.close()
        username = usernames[index]
        clientUsername = "Server"
        clientMessage = (f'{colours[index] + username + RESET} ha abandonado el chat.')
        broadcast(clientMessage, clientUsername, client)
        print(f'{colours[index] + username + RESET} ha habandonado el chat.')
        usernames.remove(username)

# Función principal para aceptar conexiones de clientes
        

def cambiarNombre(clientMessage, data, clientUsername, client):
    if str.__contains__(data, " "):
        print("Formato de cambio de nombre incorrecto:" + clientMessage)
        clientFeedback("Formato de cambio de nombre incorrecto. El formato es '/cambioNombre <NuevoNombre>'", client)
        return
    
    new_username = data.split(' ', 1)[0]
    try:
        index = clients.index(client)
    except ValueError:
        print("Cliente no encontrado en la lista.")
        return
    
    old_username = usernames[index]
    usernames[index] = new_username
    
    # Notificar a todos los clientes sobre el cambio de nombre
    message = f"{old_username} ha cambiado su nombre a {new_username}."
    broadcast(message, "Server", client)
    # Actualizar el nombre de usuario para el cliente
    soloMessage(f"Tu nombre ha sido cambiado a: {new_username}", client)




def main():
    while True:
        # Aceptar conexión del cliente
        client, address = server.accept()
        print(f"Conexión establecida con {str(address)}")

        # Solicitar y almacenar el nombre de usuario del cliente
        client.send('Ingresa tu nombre de usuario:'.encode('utf-8'))
        username = client.recv(1024).decode('utf-8')
        usernames.append(username)
        clients.append(client)

        # Anunciar la conexión del nuevo cliente a todos los clientes
        print(f"Usuario conectado: {colours[len(usernames)-1]+username+RESET}")
        clientUsername = "Server"
        clientMessage = (f'{colours[len(usernames)-1]+username+RESET} se ha unido al chat.')
        broadcast(clientMessage, clientUsername, client)

        # Iniciar un hilo para manejar la conexión del cliente
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


if __name__ == "__main__":
    main()

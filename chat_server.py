import socket
import threading
import time
import psutil
import random

from chat_canales import Canal 

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


# Lista para almacenar Clientes conectados
clients = []
usernames = []
canales = {}

#Constantes

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
    'salesiana': 'persona con mucha suerte',
    'comunista': '☭'
    
}

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
MOVE_CURSOR_END_EMOJIS = "\x1b["+str(len(EMOJI_DICT))+"B"

colours = [GREEN, YELLOW, BLUE, MAGENTA, CYAN]

# Función para enviar mensajes a todos los Clientes
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
            # Eliminar el Cliente si hay un problema al enviar el mensaje
            remove(c)


#Función para enviar un mensaje a un sólo cliente

def soloMessage(message, client, isEmoji = False):
    # en orden: guardar la posición del cursor, mover el cursor al principio de la línea anterior (la línea en blanco encima),
    # escribir el mensaje a enviar y volver a poner el cursor donde estaba (el principio de una línea, a mitad de escribir...)
    messageFormatted = SAVE_CURSOR + MOVE_CURSOR_BEGINNING_PREVIOUS_LINE + message + RESTORE_CURSOR
    if isEmoji:
        messageFormatted += MOVE_CURSOR_END_EMOJIS
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
            # Recibir mensaje del Cliente
            message = client.recv(1024)

            # Verificar si el mensaje está vacío, lo que indica que la conexión se ha cerrado
            if not message:
                # Eliminar y cerrar la conexión del Cliente
                remove(client)
                break

            # Decodificar y procesar el mensaje
            message = message.decode('utf-8')
            clientUsername = message.split(': ', 1)[0]
            clientMessage = message.split(': ', 1)[1]

            """ Prints de debug para la separación de mensajes
            print("message:", message)
            print(
                f"Cliente {clientUsername} envía el mensaje: {clientMessage}")
            print("client:", client)
            print("clientUsername:", clientUsername)
            print("clientMessage:", clientMessage)
            print("clients:", clients)
            """
            print(f"Cliente {clientUsername} envía el mensaje: {clientMessage}")
            print("Clientes conectados:", len(clients))

            
            if clientMessage.startswith('/'):
                checkCommand(clientMessage, clientUsername, client)
            else:
                clientMessage = checkContent(clientMessage)
                #broadcast(clientMessage, clientUsername, client)
                if (esta_en_algun_canal(client)) :
                    enviar_a_Canal(clientMessage, clientUsername, client, Cliente_en_que_canal_esta(client))
                else:
                    broadcast(clientMessage, clientUsername, client)
                    

        except Exception as e:
            print(f"Error en handle: {e}")
            if client not in clients:
                break


admin = 'alberto'


# Función de control de comandos


def checkCommand(clientMessage, clientUsername, client):
    global admin
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

        case "users" | "usuarios":
            soloMessage(usernames.__str__(), client)
        
        case "emojis" | "emoji":
            listEmojis(client)
            
        case "testSolo":
            if clients.count != 0:
                soloMessage("testMensajeUnico", clients[0])
        
        case "exit":
            remove(client)
            
                
        case "kick":
            if clientUsername == admin:
                kick_usuario(data, clientUsername, client)
            else:
                client.send('No tienes permiso para realizar esta acción. \n'.encode('utf-8'))
        
        case "admin":
            if admin:
                client.send(f'El administrador actual es {admin} \n'.encode('utf-8'))
            else:
                client.send('No hay administrador, que triste. \n'.encode('utf-8'))
                
        case  "darAdmin":
            if admin:
                cambiar_admin(data, client)
            else:
                client.send('No hay administrador, que triste. \n'.encode('utf-8'))
                
        case "gacha":
            personaje = random.choices(personajes, weights=[prob for _, prob in personajes], k=1)[0][0]
            broadcast(f'{clientUsername} obtuvo {personaje}!', 'Server', None)

                
        case "ayuda":
            command_list = "\n".join(f"{command}, {description}" for command, description in commands.items())
            command_list += "\n"  
            client.send(command_list.encode('utf-8'))
            
        case "clear" :
            limpiar_terminal(client)
            
        case "listaPokemon":
            pokemon_list = "\n".join(name for name, _ in personajes)
            pokemon_list += "\n"  
            client.send(pokemon_list.encode('utf-8'))
        
        case "newCanal" | "new"  :
            if(tiene_mas_de_una_palabra(data)):
                soloMessage("Error: El nombre del canal no puede tener espacios", client)
            else:
                crear_canal(clientMessage, client)
        case "Canal" | "canal" :
            print(clientMessage)
            if(clientMessage.split(' ')[1] in canales):
                unirse_a_canal(clientMessage.split(' ')[1], client)
            else:
                mensaje = f"Error:No se reconoce el canal '{clientMessage.split(' ')[1]}' como válido"
                soloMessage(mensaje, client)
        case "Canales" | "canales" | "listarCanales"| "listaCanales":
            listar_canales(client)
        case "eliminarCanal" | "deleteCanal" | "del" :
            eliminar_canal(clientMessage, client)
        case "salirCanal" | "exitCanal" | "ec" | "eC" :
            salir_de_canal(Cliente_en_que_canal_esta(client),client)
        case "listClientesCanal" | "lc" | "Lc" | "LC" :
            listar_clients_de_canal(client)
        case "all" | "allClients" | "allclients" | "todoslosClientes":
            listar_clients(client)
        case "allc":
            listar_clients_de_canales(clientMessage, clientUsername, client)
        
        
        case _:
            if (esta_en_algun_canal(client)) :
                enviar_a_Canal(clientMessage, clientUsername, client, Cliente_en_que_canal_esta(client))
            else:
                broadcast(clientMessage, clientUsername, client)


# Diccionario de comandos y sus descripciones
commands = {
    "/ayuda": "Ver la lista de comandos disponibles",
    "/susurrar": "Susurra un mensaje a un usuario",
    "/usuarios | /users": "Ver los usuarios conectados",
    "/emojis | /emoji": "Ver la lista de emojis",
    "/testsolo": "Mandar un mensaje a un solo usuario para comprobar que funciona el comando /soloMessage",
    "/exit": "Salir del chat",
    "/kick": "Expulsar a un usuario",
    "/admin": "Ver el administrador actual",
    "/daradmin": "Dar el rol de administrador a un usuario",
    "/gacha": "Hacer un gacha",
    "/listapokemon": "Ver la lista de pokemons disponibles",
    "/clear" : "Limpiar la terminal",
}

# Lista de personajes y sus probabilidades para el comando /gacha
personajes = [
    ("Pikachu", 0.1),
    ("Dragonite", 0.1),
    ("Articuno", 0.05),
    ("Zapdos", 0.05),
    ("Moltres", 0.05),
    ("Mewtwo", 0.05),
    ("Mew", 0.05),
    ("Charizard", 0.1),
    ("Blastoise", 0.1),
    ("Venusaur", 0.1),
    ("Gengar", 0.1),
    ("Alakazam", 0.1),
    ("Machamp", 0.1),
    ("Golem", 0.1),
    ("Lapras", 0.1),
    ("Snorlax", 0.1),
    ("Jolteon", 0.1),
    ("Vaporeon", 0.1),
    ("Flareon", 0.1),

]


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
    
# Funcion para cambiar el administrador
def cambiar_admin(nuevo_admin, client):
    global admin
    if nuevo_admin in usernames:  
        admin = nuevo_admin  
        client.send(f'El nuevo administrador es {admin}\n'.encode('utf-8'))
    else:
        client.send('El usuario proporcionado no existe.\n'.encode('utf-8'))

#Función para expulsar a un usuario
def kick_usuario(name, clientUsername, client):
    if clientUsername != admin:
        client.send('No tienes permiso para realizar esta acción.'.encode('utf-8'))
        return

    if name in usernames:
        name_index = usernames.index(name)
        client_to_kick = clients[name_index]
        clients.remove(client_to_kick)
        client_to_kick.send(f'Has sido expulsado por {admin}.'.encode('utf-8'))
        client_to_kick.close()
        usernames.remove(name)
        broadcast(f'{name} ha sido expulsado del chat por {admin}.', 'Server', client)
        client.send(f'El usuario {name} ha sido expulsado con éxito.\n'.encode('utf-8'))
    else:
        client.send('Error: Nombre de usuario no válido'.encode('utf-8'))

# Función para comprobar el contenido del mensaje
def checkContent(clientMessage):
    clientMessage = checkEmoji(clientMessage)
    clientMessage = checkFuck(clientMessage)
    return clientMessage


#Función para comprobar emojis
def checkEmoji(clientMessage):
    for key, value in EMOJI_DICT.items():
        clientMessage = clientMessage.replace(key, value)
    return clientMessage

def listEmojis(clientMessage):
    totalString = "Esta es la lista de emojis, se sustituyen automáticamente\n"
    for key, value in EMOJI_DICT.items():
        totalString = totalString + key + " --> " + value + '\n'
        
    totalString += '\n\n'
    soloMessage(totalString, clientMessage, True)

#Función para comproobar palabras malsonantes
def checkFuck(clientMessage):
    for word, replacement in BAD_WORDS.items():
        clientMessage = clientMessage.replace(word, '['+ replacement +']')
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


# Mostrar los comandos relacionados con los canales
comandosCanales = {
    "newCanal | new": "Crear un nuevo canal",
    "Canal | canal": "Unirse a un canal",
    "Canales | canales": "Listar los canales existentes",
    "deleteCanal | del": "Eliminar un canal",
    "exitCanal | ec": "Salir del canal",
    "listClientesCanal | lc": "Listar los clientes del canal",
    "allc": "Listar todos los clientes de todos los canales"
}
def mostrar_comandos_canales():
    print("\nComandos relacionados con los canales:\n")
    for comando, descripcion in comandosCanales.items():
        print(f"{comando}: {descripcion}" + "\n")


# Función para añadir un Cliente al canal
def unirse_a_canal(canal, client):
    # print(canal)
    if(Cliente_en_que_canal_esta(client) != None):
        if(esta_en_el_canal(client, canal)):
            mensaje = f"Ya estás en el canal '{canal}'"
            soloMessage(mensaje, client)
            return
        else:
            canaldelusuario = Cliente_en_que_canal_esta(client)
            # mensaje = f"Estás en el canal '"+canaldelusuario+"'.  "
            # soloMessage(mensaje, client)
            salir_de_canal(canaldelusuario, client)
    # return
    
    for c in canales:
        if c == canal:
            mensaje = f"Ha entrado al canal '{usernames[clients.index(client)]}'"
            enviar_a_Canal(mensaje,"Server",client,canal)
            canales[canal].agregar_cliente(client)
            mensaje = f"Te has unido al canal '{canal}'"
            soloMessage(mensaje, client)
            return

    mensaje = f"Error:No se reconoce el canal '{canal}' como válido"
    soloMessage(mensaje, client)
    print( mensaje)


# Función para añadir un Cliente al canal
def salir_de_canal(canal, client):
    for c in clients:
        if c == client:
            canales[canal].eliminar_cliente(c)
            mensaje = f"Te has salido del canal '{canal}'"
            soloMessage(mensaje, client)
            mensaje = f"Ha salido del canal '{usernames[clients.index(client)]}'"
            enviar_a_Canal(mensaje,"Server",client,canal)
            print("Cliente "+usernames[clients.index(client)]+": " + mensaje)
            return
    mensaje = f"No te has salido del canal '{canal}'"

# Función para enviar mensajes al CANAL
def enviar_a_Canal(clientMessage, clientUsername, client, canal):
    for c in clients:
        messageFormatted = SAVE_CURSOR + MOVE_CURSOR_BEGINNING_PREVIOUS_LINE + CLEAR_ENTIRE_LINE
        if c != client and c in canales[canal].clientes:
            if clientUsername == "Server":
                messageFormatted += RED + BOLD 
            else:
                i = usernames.index(clientUsername) % len(colours)
                messageFormatted += colours[i] + BOLD
        else:
            messageFormatted += WHITE

        messageFormatted += clientUsername + ':' + RESET + ' ' + "[" + canal + "]: " + clientMessage  + RESTORE_CURSOR
        
        # print("LLega antes de enviar")
        if c in canales[canal].clientes:
            # print("enviando...")
            try:
                c.send(messageFormatted.encode('utf-8'))
            except:
                # Eliminar el Cliente si hay un problema al enviar el mensaje
                remove(c)

#Funciones para gestionar CANALES y ClienteS
#Función que mira si el Cliente esta en algun canal
def esta_en_algun_canal(client):
    for canal in canales.values():
        if canal.encontrar_cliente(client) != None:
            return True
    return False
#Función que mira si el Cliente esta en EL Canal
def esta_en_el_canal(client, canal):
    if canales[canal].encontrar_cliente(client) != None:
        return True
    else:
        return False
#Funcion que devuelve el canal donde esta el Cliente
def Cliente_en_que_canal_esta(client):
    for canal in canales:
        if canales[canal].encontrar_cliente(client) != None:
            return canales[canal].nombre
    return None

# Funciones de control y creacion de canales
def crear_canal(clientMessage, client):
    print("creando_el_canal")
    if str.__contains__(clientMessage, ' '):
        command, nombreCanal = clientMessage.split(' ', 1)
    else:
        command = clientMessage
        nombreCanal = ""
        mensaje = ("commando:" + command + " pero no es valido el nombre del canal")
        soloMessage(mensaje, client)
        
    if nombreCanal == "" or nombreCanal == " " or nombreCanal == "newCanal":
        print("No se ha ingresado el nombre del canal o el nombre del canal no es valido", nombreCanal)
        mensaje = f"No se ha ingresado el nombre del canal o el nombre del canal no es valido; {nombreCanal}"
        soloMessage(mensaje, client)
        return
    else:
        if nombreCanal in canales:
            print("El canal ya existe")
            mensaje = f"Nombre: '{nombreCanal}' no es válido; Canales existentes: {', '.join(canales.keys())}"
            soloMessage(mensaje, client)
            return
        else:
            canales[nombreCanal] = Canal(nombreCanal)
            exito = f"Canal '{nombreCanal}' creado con éxito; Canales existentes: {', '.join(canales.keys())}"
            # print(exito)
            print(f"Canal '{nombreCanal}' creado con éxito")
            soloMessage(exito , client)

def tiene_mas_de_una_palabra(cadena):
    palabras = cadena.split()
    return len(palabras) > 1


def listar_canales(client):
    print("listando_canales")
    if len(canales) == 0:
        mensaje = "No hay canales creados"
        soloMessage(mensaje, client)
        return
    else:
        mensaje = f"Canales existentes: {', '.join(canales.keys())}"
        soloMessage(mensaje, client)
        return

#Funcion de desarrollador o admin que lista de TODOS los canales TODOS los usuarios
def listar_clients_de_canales(clientMessage, clientUsername, client):
    for canal in canales.keys():
        # print("LLEGA")
        canalClientes = canales[canal].clientes
        # for client in clients:
        for canalCliente in canalClientes:
            # print("LLEGA2"+str(canalCliente))
            index = clients.index(canalCliente)
            username = usernames[index]
            message = "En canal ["+ str(canal) +"] Cliente : "+ username
            print(f""+message)
            soloMessage(f""+message, client)
    return

#Funcion para lista los clients del canal donde esta el usuario
def listar_clients_de_canal(client):
    for canal in canales:
        if canales[canal].encontrar_cliente(client) != None:
            canalClientes = canales[canal].clientes
            for canalCliente in canalClientes:
                index = clients.index(canalCliente)
                username = usernames[index]
                mensaje = f"Canal '{canal}', Cliente : '{username}'"
                soloMessage(mensaje, client)
                print(mensaje)
            # return
        else:
            mensaje = f"No estas en un canal. Unete"
            soloMessage(mensaje, client)
            listar_canales(client)
    return

def listar_clients(client):
    for client2 in clients:
        index = clients.index(client2)
        username = usernames[index]
        mensaje = "Cliente " + str(index) + " : " + username
        soloMessage(mensaje, client)
        print(mensaje)

def eliminar_canal(clientMessage, client):
    print("eliminando_el_canal")
    if str.__contains__(clientMessage, ' '):
        command, nombreCanal = clientMessage.split(' ', 1)
    if nombreCanal == "" or nombreCanal == " ":
        mensaje = ("Error:'" + nombreCanal + "' no es valido el nombre del canal")
        soloMessage(mensaje, client)
        return
    else:
        if nombreCanal in canales:
            if canales[nombreCanal].clientes != []:
                mensaje = f"Error: No se puede eliminar el canal '{nombreCanal}' porque hay clientes en él"
                soloMessage(mensaje, client)
                return
            else:
                canalClientes = canales[nombreCanal].vaciar_canal()
                for canalClient in canalClientes:
                    canalClient.send("El canal ha sido eliminado, te has movido al chat general".encode('utf-8'))
                    #clients.append(canalClient)#   Mira esta linea si hay un error
                del canales[nombreCanal]
                mensaje = f"Eliminado: '{nombreCanal}'  ; Canales existentes: {', '.join(canales.keys())}"
                soloMessage(mensaje, client)
                return
        else:
            exito = f"Canal '{nombreCanal}' no Existe; Canales existentes: {', '.join(canales.keys())}"
            print(f"Error: Canal '{nombreCanal}' no Existe")
            soloMessage(exito , client)





# Función principal para aceptar conexiones de Clientes


# Metodo para limpiar la terminal 
def limpiar_terminal(client):
    MOVES = "\033[H" 
    # CLEAR = "\033[J"
    # BORRAR = MOVES +CLEAR 
    BORRAR = "\033[2J"
    # comandoBorrar = MOVES +CLEAR+ BORRAR
    if client in clients:
        index = clients.index(client)
        username = usernames[index]
        
        soloMessage("\033[J"+ BORRAR + MOVES, client)
        print(f'{colours[index] + username + RESET} ha limpiado la terminal.')

def main():
    while True:
        # Aceptar conexión del Cliente
        client, address = server.accept()
        print(f"Conexión establecida con {str(address)}")

        while True:
            # Solicitar y almacenar el nombre de usuario del cliente
            client.send('Ingresa tu nombre de usuario:'.encode('utf-8'))
            username = client.recv(1024).decode('utf-8')
        
            # Comprobar si el usuario ya existe
            if username in usernames:
                client.send('Nombre de usuario ya está en uso. Por favor, elige otro.'.encode('utf-8'))
            else:
                break
        
        usernames.append(username)
        clients.append(client)

        # Anunciar la conexión del nuevo Cliente a todos los Clientes
        print(f"Usuario conectado: {colours[len(usernames)-1]+username+RESET}")
        clientUsername = "Server"
        clientMessage = (f'{colours[len(usernames)-1]+username+RESET} se ha unido al chat.')
        broadcast(clientMessage, clientUsername, client)

        # Iniciar un hilo para manejar la conexión del Cliente
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


if __name__ == "__main__":
    main()
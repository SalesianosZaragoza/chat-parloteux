import socket
import threading
import psutil
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


# Lista para almacenar clientes conectados
clients = []
usernames = []
canales = {}

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


# Función para enviar un mensaje a un sólo cliente

def soloMessage(message, client):
    try:
        message = message + "\n"
        # Si no va - > quitar el if
        if client in clients:
            message = message.encode('utf-8')
            client.send(message)
    except Exception as e:
        print(
            f"Se produjo una excepcion mientras se mandaba un mensaje al cliente {client}: {e}")
        remove(client)


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
            receptorName = data.split(' ', 1)[0]
            print("receptorName", receptorName)
            try:
                receptor = clients.index(receptorName)
            except:
                print("El usuario ", receptorName, " no existe")
                # return
            messageFinal = data.split(' ', 1)[1]
            print(
                f"{clientUsername} susurra a {receptorName} el mensaje {messageFinal}")
        case "testSolo":
            if clients.count != 0:
                soloMessage("testMensajeUnico", clients[0])
        case "exit":
            remove(client)
        case "newCanal" | "new"  :
            crear_canal(clientMessage, client)
        case "Canal" | "canal" :
            unirse_a_canal(clientMessage.split(' ')[1], client)
        case "Canales" | "canales" | "list":
            listar_canales(client)
        case "eliminarCanal" | "deleteCanal" | "del" :
            eliminar_canal(clientMessage, client)
        case "clear" :
            limpiar_terminal(client)
        case _:
            if (esta_en_algun_canal(client)) :
                enviar_a_Canal(clientMessage, clientUsername, client, cliente_en_que_canal_esta(client))
                print("llega")
            else:
                broadcast(clientMessage, clientUsername, client)


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



# Función para añadir un cliente al canal
def unirse_a_canal(canal, client):
    print(canal)
    if(cliente_en_que_canal_esta(client) != None):
        print(cliente_en_que_canal_esta(client))
        salir_de_canal(cliente_en_que_canal_esta(client), client)
    print("LLEGA " + canal)
    for c in clients:
        if c == client:
            if(esta_en_el_canal(client, canal)):
                mensaje = f"Ya estás en el canal '{canal}'"
                soloMessage(mensaje, client)
                return
            else:
                canales[canal].agregar_cliente(c)
                mensaje = f"Te has unido al canal '{canal}'"
                soloMessage(mensaje, client)
                clientes = canales[canal].clientes
                for c in clients:
                    for e in clientes:
                        if c == e:
                            index = clients.index(c)
                            username = usernames[index]
                            print("Cliente " + index + " "+username+", ")
                if client in clients:
                    index = clients.index(client)
                    username = usernames[index]
                    print("Cliente "+username+": " + mensaje)
                return
        else:
            mensaje = f"No te has unido al canal '{canal}'"
            soloMessage(mensaje, client)

# Función para añadir un cliente al canal
def salir_de_canal(canal, client):
    for c in clients:
        if c == client:
            canales[canal].eliminar_cliente(c)
            mensaje = f"Te has salido del canal '{canal}'"
            soloMessage(mensaje, client)
            print("Cliente "+client+": " + mensaje)
            return
        else:
            mensaje = f"No te has salido del canal '{canal}'"
            soloMessage(mensaje, client)

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

        messageFormatted += clientUsername + ':' + RESET + ' ' + clientMessage  + RESTORE_CURSOR
        
        try:
            c.send(messageFormatted.encode('utf-8'))
        except:
            # Eliminar el cliente si hay un problema al enviar el mensaje
            remove(c)

#Funciones para gestionar CANALES y CLIENTES
#Función que mira si el cliente esta en algun canal
def esta_en_algun_canal(client):
    for canal in canales.values():
        if canal.encontrar_cliente(client) != None:
            return True
    return False
#Función que mira si el cliente esta en EL Canal
def esta_en_el_canal(client, canal):
    if canales[canal].encontrar_cliente(client) != None:
        return True
    else:
        return False
#Funcion que devuelve el canal donde esta el cliente
def cliente_en_que_canal_esta(client):
    for canal in canales:
        if canales[canal].encontrar_cliente(client) != None:
            return canal.nombre
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
            # Gestionar si los clientes se deben meter al chat General o a donde !!!!!!!!!!!!!!!!!!!!!!!!
            # No gestiono el array username para evitar errores de usuarios repetidos
            canalClientes = canales[nombreCanal].vaciar_canal()
            for canalClient in canalClientes:
                canalClient.send("El canal ha sido eliminado, te has movido al chat general".encode('utf-8'))
                clients.append(canalClient)
            del canales[nombreCanal]
            mensaje = f"Eliminado: '{nombreCanal}'  ; Canales existentes: {', '.join(canales.keys())}"
            soloMessage(mensaje, client)
            return
        else:
            exito = f"Canal '{nombreCanal}' no Existe; Canales existentes: {', '.join(canales.keys())}"
            print(f"Error: Canal '{nombreCanal}' no Existe")
            soloMessage(exito , client)

# metodo para limpiar la terminal 
def limpiar_terminal(client):
    MOVES = "\033[H" 
    CLEAR = "\033[J"
    # BORRAR = MOVES +CLEAR
    BORRAR = "\033[2J" + MOVES
    # comandoBorrar = MOVES +CLEAR+ BORRAR
    if client in clients:
        index = clients.index(client)
        username = usernames[index]
        
        soloMessage(BORRAR, client)
        print(f'{colours[index] + username + RESET} ha limpiado la terminal.')



# Función principal para aceptar conexiones de clientes


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

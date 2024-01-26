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

#print("Servidor iniciado con la dirección IP: " + )
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

# Función para enviar mensajes a todos los clientes


def broadcast(message, client):
    for c in clients:
        if c != client:
            try:
                c.send(message)
            except:
                # Eliminar el cliente si hay un problema al enviar el mensaje
                remove(c)




# Función para manejar la conexión de un cliente
def handle(client):
    while True:
        try:
            # Recibir mensaje del cliente
            message = client.recv(1024)
            
            # Verificar si el mensaje está vacío, lo que indica que la conexión se ha cerrado
            if not message:
                # Eliminar y cerrar la conexión del cliente
                index = clients.index(client)
                username = usernames[index]
                message = f'{username} ha abandonado el chat.'.encode('utf-8')
                broadcast(message, client)
                remove(client)
                break

            # Decodificar y procesar el mensaje
            message = message.decode('utf-8')
            clientUsername = message.split(': ', 1)[0]
            clientMessage = message.split(': ', 1)[1]

            """ Prints de debug para la separación de mensajes"""
            print("message:", message)
            print(f"cliente {clientUsername} envía el mensaje: {clientMessage}")
            print("client:", client)
            print("clientUsername:", clientUsername)
            print("clientMessage:", clientMessage)
            print("clients:", clients)

            if clientMessage.startswith('/'):
                checkCommand(clientMessage, clientUsername, client)
            else:
                broadcast(message.encode('utf-8'), client)

        except Exception as e:
            print(f"Error en handle: {e}")
            # Eliminar y cerrar la conexión del cliente
            

            break

# Función de control de comandos

def checkCommand(clientMessage, clientUsername, client):
    print("es un comando")

    totalMessage = str.split(clientMessage, '/', 1)[1]
    command, data = totalMessage.split(' ', 1)
    
    print(command, data)

    match command:
        case "susurrar":
            receptorName = data.split(' ', 1)[0]
            print("receptorName", receptorName)
            try:
                receptor = clients.index(receptorName)
            except:
                print("El usuario ", receptorName, " no existe")
                return
            messageFinal = data.split(' ', 1)[1]
            print(f"{clientUsername} susurra a {receptorName} el mensaje {messageFinal}")
        case _:
            rebuiltMessage = clientUsername + ": " + clientMessage
            broadcast(rebuiltMessage.encode('utf-8'), client)
    


# Función para eliminar un cliente de la lista


def remove(client):
    if client in clients:
        index = clients.index(client)
        clients.remove(client)
        client.close()
        username = usernames[index]
        broadcast(f'{username} ha abandonado el chat.'.encode('utf-8'), client)
        usernames.remove(username)

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
        print(f"Usuario conectado: {username}")
        broadcast(f'{username} se ha unido al chat.'.encode('utf-8'), client)

        # Iniciar un hilo para manejar la conexión del cliente
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


if __name__ == "__main__":
    main()

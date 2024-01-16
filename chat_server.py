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
        return False
    else:
        return True

#print("Servidor iniciado con la dirección IP: " + )
server.listen()
host_addr = psutil.net_if_addrs()
print("Servidor iniciado con las direcciones IP: ")
filtered_addresses = filter(filter_address, host_addr.items())
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
            message = str(client.recv(1024).decode('utf-8'))
            clientUsername = message.split(': ', 1)[0]
            clientMessage = message.split(': ', 1)[1]
            print(f"cliente {clientUsername} envia el mensaje: {clientMessage}")
            print("client:", client)
            print("clientUsername:",clientUsername)
            print("clientMessage",clientMessage)
            if clientMessage.startswith('/') :
                checkCommand(clientMessage, clientUsername, client)
            else:
                broadcast(message, client)
        except:
            # Eliminar el cliente si hay un problema al recibir el mensaje
            index = clients.index(client)
            clients.remove(client)
            client.close()
            username = usernames[index]
            broadcast(f'{username} ha abandonado el chat.'.encode(
                'utf-8'), client)
            usernames.remove(username)
            break


# Función de control de comandos

def checkCommand(clientMessage, clientUsername, client):
    print("es un comando")
    totalMessage = str.split(clientMessage, '/', 1)[1]
    command, data = totalMessage.split(' ', 1)
    print(command, data)

    match command:
        case "susurrar":
            receptor = data.split(' ', 1)[0]
            messageFinal = data.split(' ', 1)[1]
            print(f"{clientUsername} susurra a {receptor} el mensaje {messageFinal}")
        case _:
            messageTotal = clientUsername + ": " + clientMessage
            broadcast(messageTotal, client)
    


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
        client.send('NICK'.encode('utf-8'))
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

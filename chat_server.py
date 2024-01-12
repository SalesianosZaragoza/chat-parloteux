import socket
import threading

# Configuración del servidor
host = '127.0.0.1'
port = 80

# Crear un socket del servidor
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

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
            broadcast(message, client)
        except:
            # Eliminar el cliente si hay un problema al recibir el mensaje
            index = clients.index(client)
            clients.remove(client)
            client.close()
            username = usernames[index]
            broadcast(f'{username} ha abandonado el chat.'.encode('utf-8'), client)
            usernames.remove(username)
            break

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

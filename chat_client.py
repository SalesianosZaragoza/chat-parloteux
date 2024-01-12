import socket
import threading

# Configuración del cliente
host = input("Ingresa la dirección IP del servidor: \nEn caso de dejarlo en blanco se asignará localhost\n")
if host == '':
    host = '127.0.0.1'
port = 65000

# Nombre de usuario
username = input("Ingresa tu nombre de usuario: ")

# Crear un socket del cliente
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.connect((host, port))


# Función para recibir mensajes del servidor
def receive():
    while True:
        try:
            # Recibir y mostrar mensajes del servidor
            message = client.recv(1024).decode('utf-8')
            print(message)
        except:
            # Cerrar la conexión si hay un problema al recibir el mensaje
            print("Ha ocurrido un error. Saliendo...")
            client.close()
            break

# Función para enviar mensajes al servidor
def send():
    while True:
        message = f'{username}: {input("")}'
        client.send(message.encode('utf-8'))

# Iniciar hilos para recibir y enviar mensajes simultáneamente
receive_thread = threading.Thread(target=receive)
receive_thread.start()

send_thread = threading.Thread(target=send)
send_thread.start()


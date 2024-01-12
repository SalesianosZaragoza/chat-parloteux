import socket
import threading
import time

# Configuración del cliente
host = input("Ingresa la dirección IP del servidor: \nEn caso de dejarlo en blanco se asignará localhost\n")
if host == '':
    host = '127.0.0.1'
port = 65000

# Nombre de usuario
username = input("Ingresa tu nombre de usuario: ")

# Crear un socket del cliente
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

#Variable para almacenar el tiempo del último mensaje
last_message_time = time.time()

#Función para verificar la inactividad del usuario
def check_inactivity():
    global last_message_time
    while True:
            
        if time.time() - last_message_time > 5 * 60:  # 5 minutos
            print("Llevas demasiado tiempo inactivo, cerrando conexión...")
            client.close()
            break
        if time.time() - last_message_time > 4 * 60:  # 4 minutos
            print("Si no escribes un mensaje dentro de un minuto, se cerrará la conexión.")
            
        time.sleep(60)  # Comprobar cada minuto

# Instanciar un hilo para verificar la inactividad del usuario
inactivity_thread = threading.Thread(target=check_inactivity)
inactivity_thread.start()

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
    global last_message_time
    while True:
        message = f'{username}: {input("")}'
        client.send(message.encode('utf-8'))
        last_message_time = time.time()  # Update the last message time

# Iniciar hilos para recibir y enviar mensajes simultáneamente
receive_thread = threading.Thread(target=receive)
receive_thread.start()

send_thread = threading.Thread(target=send)
send_thread.start()


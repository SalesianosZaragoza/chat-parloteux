import socket
import threading
import time
import sys

# Configuración del cliente
host = input("Ingresa la dirección IP del servidor: \nEn caso de dejarlo en blanco se asignará localhost\n")
if host == '':
    host = '127.0.0.1'
port = 65000


# Crear un socket del cliente
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))


# Nombre de usuario
username = 'null'

# Función para eliminar clientes
end = False


#Variable para almacenar el tiempo del último mensaje
last_message_time = time.time()

#Función para verificar la inactividad del usuario
def check_inactivity():
    global last_message_time
    global end
    while True:
            
        if time.time() - last_message_time > 5 * 60:  # 5 minutos
            print("Llevas demasiado tiempo inactivo, cerrando conexión...")
            close_message = f'{username} se ha desconectado por inactividad'
            client.send(close_message.encode('utf-8'))
            end = True
            time.sleep(1)
            close()
            return
        if time.time() - last_message_time > 4 * 60:  # 4 minutos
            print("Si no escribes un mensaje dentro de un minuto, se cerrará la conexión.")
            
        time.sleep(60)  # Comprobar cada minuto

# Instanciar un hilo para verificar la inactividad del usuario
inactivity_thread = threading.Thread(target=check_inactivity)
inactivity_thread.start()

# Función para recibir mensajes del servidor
def receive():
    global end
    while True:
        if end:
            break
        try:
            # Recibir y mostrar mensajes del servidor
            message = client.recv(1024).decode('utf-8')
            print(message)
        except Exception as e:
            # Cerrar la conexión si hay un problema al recibir el mensaje
            print(f"Error en handle: {e}")
            
            continue

# Función para enviar mensajes al servidor
def send():
    global end
    global last_message_time
    global username
    while True:
        if end:
            break
        if username == 'null':
            username = input("username: ")
            message = f'{username}'
        else:    
            message = f'{username}: {input("")}'
        client.send(message.encode('utf-8'))
        last_message_time = time.time()  # Update the last message time

# Iniciar hilos para recibir y enviar mensajes simultáneamente
receive_thread = threading.Thread(target=receive)
receive_thread.start()

send_thread = threading.Thread(target=send)
send_thread.start()

# Función para cerrar la conexión
def close():
    client.close()
    sys.exit()

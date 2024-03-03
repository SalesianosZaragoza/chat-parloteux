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
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect((host, port))


# Nombre de usuario
username = 'null'

quit = False


#Variable para almacenar el tiempo del último mensaje
last_message_time = time.time()

#Función para cerrar la conexión con el server
def close_connection():
    #print("Cerrando conexión...")
    quit = True
    server.close()
    time.sleep(1)
    #print("Conexión cerrada.\nPresiona ctrl+c para salir.")


#Función para verificar la inactividad del usuario
def check_inactivity():
    global last_message_time
    global quit
    while not quit:   
        if time.time() - last_message_time > 5 * 60:  # 5 minutos
            print("Llevas demasiado tiempo inactivo")
            close_connection()
            break
        if time.time() - last_message_time > 4 * 60:  # 4 minutos
            print("Si no escribes un mensaje dentro de un minuto, se cerrará la conexión.")
            
        time.sleep(60)  # Comprobar cada minuto



# Función para recibir mensajes del servidor
def receive():
    global quit
    while not quit:
        try:
            # Recibir y mostrar mensajes del servidor
            message = server.recv(1024).decode('utf-8')
            print(message)
        except Exception as e:
            # Cerrar la conexión si hay un problema al recibir el mensaje
            #print(f"Error en receive: {e}")
            print("Cerrando conexión...")
            close_connection()
            print("Conexión cerrada.\nPresiona ctrl+c para salir.")
            break       

#Constantes secuencias de escape
MOVES_CURSOR_1_LINE_UP = "\x1b[1A" 
CLEAR_ENTIRE_LINE = "\x1b[2K"


# Función para enviar mensajes al servidor
def send():
    global end
    global last_message_time
    global username
    global quit
    while not quit:
        if username == 'null':
            username = input("username: ")
            message = f'{username}'
            data = ''
        else:
            data = input("")    
            message = f'{username}: {data}'
        try:
            server.send(message.encode('utf-8'))
            print(MOVES_CURSOR_1_LINE_UP+CLEAR_ENTIRE_LINE+MOVES_CURSOR_1_LINE_UP)
            #print("\033[A                                                                                \033[A") # Limpiar la línea de entrada de texto 80 caracteres
            if data == '/exit':
                close_connection()
                break
            last_message_time = time.time()  # Update the last message time
        except Exception as e:
            #print(f'Error en send: {e}')
            server.close()
            break       

# Instanciar un hilo para verificar la inactividad del usuario
inactivity_thread = threading.Thread(target=check_inactivity)
inactivity_thread.start()
# Iniciar hilos para recibir y enviar mensajes simultáneamente
receive_thread = threading.Thread(target=receive)
receive_thread.start()

send_thread = threading.Thread(target=send)
send_thread.start()

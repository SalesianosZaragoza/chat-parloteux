import socket
import threading
import time
import sys
from chat_canales import Canal

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
    print("Cerrando conexión...")
    quit = True
    server.close()
    time.sleep(1)
    print("Conexión cerrada.\nPresiona ctrl+c para salir.")


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
    global username
    global duplicateUsername
    while not quit:
        try:
            # Recibir y mostrar mensajes del servidor
            message = server.recv(1024).decode('utf-8')
            if message == 'Nombre de usuario ya está en uso. Por favor, elige otro.':
                duplicateUsername = username
                username = 'null'
                time.sleep(1)  # Clear the username
            elif message == 'Has sido expulsado por un administrador.':
                print("Has sido expulsado del servidor.")
                close_connection()
                break
            print(message)
        except Exception as e:
            # Cerrar la conexión si hay un problema al recibir el mensaje
            #print(f"Error en receive: {e}")
            #print("Cerrando conexión...")
            close_connection()
            #print("Conexión cerrada.\nPresiona ctrl+c para salir.")
            break       

#Constantes secuencias de escape
MOVES_CURSOR_1_LINE_UP = "\x1b[1A" 
CLEAR_ENTIRE_LINE = "\x1b[2K"

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
    'agustín': 'Un poco menos que Dios',
    'salesianos': 'la mejor escuela del mundo',
    'salesiano': 'persona con mucha suerte',
    'salesiana': 'persona con mucha suerte',
    'comunista': ' ☭ ',
    'Nacho': ' ☭ ',
    'nacho': ' ☭ ',
    'Fuck': 'F***',
}

# Función para enviar mensajes al servidor
def send():
    global end
    global last_message_time
    global username
    global quit
    while not quit:
        if username == 'null':
            while True:  # Keep asking for a username until a valid one is entered
                username = input("username: ")
                if ' ' in username:
                    print("Nombre de usuario no puede tener espacios. Utiliza solo una palabra.")
                    username == 'null'
                elif username == '':
                    print("Nombre de usuario no puede estar vacío.")
                    username == 'null'
                elif any(bad_word in username.lower() for bad_word in BAD_WORDS):
                    print("Nombre de usuario no puede contener la palabra prohibida.")
                    username == 'null'
                elif len(username) > 1:
                    print("El nombre de usuario no puede tener más de una palabra")
                    username == 'null'
                else:
                    message = f'{username}'
                    server.send(message.encode('utf-8'))  # Send the username to the server
                    time.sleep(1)  # Wait for a response from the server
                    if username != 'null':  # If the server accepted the username, break the loop
                        break
            data = ''
        else:
            data = input("")    
            message = f'{username}: {data}'
        try:
            server.send(message.encode('utf-8'))
            print(MOVES_CURSOR_1_LINE_UP+CLEAR_ENTIRE_LINE+MOVES_CURSOR_1_LINE_UP)
            if data == '/exit':
                close_connection()
                break
            last_message_time = time.time()  # Update the last message time
        except Exception as e:
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

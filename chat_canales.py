class Canal:
    def __init__(self, nombre):
        self.nombre = nombre # Nombre del canal
        self.clientes = []  # Clientes del canal
        self.mensajes = []  # lista de mensajes del canal

    # Para agregar un nuevo cliente al canal
    def agregar_cliente(self, cliente):
        self.clientes.append(cliente)

    # Para eliminar un cliente del canal
    def eliminar_cliente(self, cliente):
        self.clientes.remove(cliente)
    
    # Para enviar mensaje a TODOS los clientes del canal
    def enviar_mensaje(self, mensaje):
        self.mensajes.append(mensaje)

    # Obtienes los últimos 10 mensajes cuando te conectas POR PRIMERA VEZ
    # También se puede usar para borrar los mensajes que tienes en la pantalla con /clear 
    # Y volver a cargar los últimos 10 mensajes
    def obtener_ultimos_mensajes(self):
        return self.mensajes[-10:]
    
    # eliminar canal de forma segura
    def vaciar_canal(self):
        clientesCanal = self.clientes
        self.clientes = []
        self.mensajes = []
        return clientesCanal
    
    #Encontrar un cliente
    def encontrar_cliente(self, cliente):
        for client in self.clientes:
            if client == cliente:
                return client
        return None
    
    
    
    
    # Como no funciona se puede borrar
    # def __str__(self):
    #     return self.nombre + 'se ha empleado este metodo'
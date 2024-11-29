import socket
import threading
import sqlite3
import json

class ServidorChat:
    
    def __init__(self, host='127.0.0.1', puerto=12345):
        self.servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servidor.bind((host, puerto))
        self.servidor.listen(5)
        self.clientes = []
        self.sockets_usuarios={}
        self.configurar_base_de_datos()
    
    def configurar_base_de_datos(self):
        self.conexion = sqlite3.connect('servidor_chat.db', check_same_thread=False)
        self.cursor = self.conexion.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                               username TEXT NOT NULL UNIQUE,
                               password TEXT NOT NULL)''')
        self.conexion.commit()

    def manejar_cliente(self, socket_cliente):
        while True:
            try:
                mensaje = socket_cliente.recv(1024).decode('utf-8')
                if mensaje:
                    mensaje_json = json.loads(mensaje)
                    if mensaje_json['tipo'] == 'login':
                        self.iniciar_sesion(socket_cliente, mensaje_json)
                    elif mensaje_json['tipo'] == 'registro':
                        self.registrar_usuario(socket_cliente, mensaje_json)
                    elif mensaje_json['tipo'] == 'desconexion':
                        usuario = self.sockets_usuarios.pop(socket_cliente, None)  # Elimina del mapeo
                        if socket_cliente in self.clientes:
                            self.clientes.remove(socket_cliente)
                        socket_cliente.close()
                        self.enviar_lista_usuarios_a_todos()  # Enviar lista actualizada al desconectar
                        print(f"Usuario desconectado: {usuario}")
                        break
                    else:
                        self.broadcast(mensaje, socket_cliente)
            except:
                if socket_cliente in self.clientes:
                    self.clientes.remove(socket_cliente)
                    self.sockets_usuarios.pop(socket_cliente, None)  # Remueve el usuario del mapeo
                    self.enviar_lista_usuarios_a_todos()  # Enviar lista actualizada al desconectar
                socket_cliente.close()
                break
    
    def iniciar_sesion(self, socket_cliente, mensaje):
        username = mensaje['username']
        password = mensaje['password']
        self.cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = self.cursor.fetchone()
        if user:
            respuesta = json.dumps({"tipo": "login", "estado": "exito"})
            socket_cliente.send(respuesta.encode('utf-8'))
            self.clientes.append(socket_cliente)
            self.sockets_usuarios[socket_cliente] = username  # Mapea el socket con el usuario
            self.enviar_lista_usuarios_a_todos() # Enviar la lista actualizada de usuarios conectados    else:
        else:
            respuesta = json.dumps({"tipo": "login", "estado": "fallo"})
            socket_cliente.send(respuesta.encode('utf-8'))

    def registrar_usuario(self, socket_cliente, mensaje):
        username = mensaje['username']
        password = mensaje['password']
        try:
            self.cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            self.conexion.commit()
            respuesta = json.dumps({"tipo": "registro", "estado": "exito"})
        except sqlite3.IntegrityError:
            respuesta = json.dumps({"tipo": "registro", "estado": "fallo"})
        socket_cliente.send(respuesta.encode('utf-8'))
    
    def enviar_lista_usuarios_a_todos(self):
        usuarios_activos = list(self.sockets_usuarios.values())
        respuesta = json.dumps({"tipo": "listar_usuarios", "usuarios": usuarios_activos})
        for cliente in self.clientes:
            try:
                cliente.send(respuesta.encode('utf-8'))
            except:
                self.clientes.remove(cliente)
                cliente.close()
    
    def broadcast(self, mensaje, socket_cliente):
        mensaje = json.loads(mensaje)

        if mensaje['tipo'] == 'broadcast':
            # Mensaje para todos los clientes excepto el remitente
            for cliente in self.clientes:
                if cliente != socket_cliente:
                    try:
                        cliente.send(json.dumps(mensaje).encode('utf-8'))
                    except:
                        self.clientes.remove(cliente)
                        self.sockets_usuarios.pop(cliente, None)
                        cliente.close()
        elif mensaje['tipo'] == 'privado':
            # Mensaje privado
            destino = mensaje['destino']
            print(f"Mensaje privado de {mensaje['origen']} para {destino}: {mensaje['mensaje']}")
            mensaje_json = json.dumps({
                "tipo": "privado",
                "origen": self.sockets_usuarios.get(socket_cliente, "Desconocido"),
                "mensaje": mensaje['mensaje']
            })
            # Buscar el socket del destinatario en el mapeo `sockets_usuarios`
            for cliente_socket, usuario in self.sockets_usuarios.items():
                if usuario == destino:
                    try:
                        cliente_socket.send(mensaje_json.encode('utf-8'))
                    except:
                        self.clientes.remove(cliente_socket)
                        self.sockets_usuarios.pop(cliente_socket, None)
                        cliente_socket.close()
                    break

    def iniciar(self):
        print("Servidor iniciado...")
        while True:
            socket_cliente, addr = self.servidor.accept()
            hilo_cliente = threading.Thread(target=self.manejar_cliente, args=(socket_cliente,))
            hilo_cliente.start()

if __name__ == "__main__":
    servidor = ServidorChat()
    servidor.iniciar()

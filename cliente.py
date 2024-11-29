import socket
import threading
import tkinter as tk
from tkinter import messagebox
import json

def centrar_ventana(ventana, ancho, alto):
    ancho_pantalla = ventana.winfo_screenwidth()
    alto_pantalla = ventana.winfo_screenheight()
    x = (ancho_pantalla // 2) - (ancho // 2)
    y = (alto_pantalla // 2) - (alto // 2)
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

class ClienteChat:

    def __init__(self, host='127.0.0.1', puerto=12345):
        self.cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cliente.connect((host, puerto))
        self.chats_privados = {}
        
        self.ventana_principal = tk.Tk()
        self.ventana_principal.title("Cliente de Chat")
        self.ventana_principal.configure(bg="lightblue")
        centrar_ventana(self.ventana_principal, 400, 300)
        
        tk.Label(self.ventana_principal, text="Usuario:", font=("Arial", 12, "bold"), bg="lightblue").pack(pady=5)
        self.entrada_usuario = tk.Entry(self.ventana_principal, font=("Arial", 10))
        self.entrada_usuario.pack()
        
        tk.Label(self.ventana_principal, text="Contraseña:", font=("Arial", 12, "bold"), bg="lightblue").pack(pady=5)
        self.entrada_contrasena = tk.Entry(self.ventana_principal, show="*", font=("Arial", 10))
        self.entrada_contrasena.pack(pady=5)
        
        self.boton_login = tk.Button(self.ventana_principal, text="Iniciar Sesión", command=self.iniciar_sesion,font=("Arial", 10,"bold"),bg="#023e8a", fg="white")
        self.boton_login.pack(pady=10)
        self.ventana_principal.bind('<Return>', lambda event: self.iniciar_sesion())
        
        self.boton_registro = tk.Button(self.ventana_principal, text="Registrar", command=self.ventana_registro,font=("Arial", 10,"bold"), bg="#4CAF50",fg="white")
        self.boton_registro.pack(pady=10)
        
        self.ventana_principal.protocol("WM_DELETE_WINDOW", self.cerrar_ventana)
        self.ventana_principal.mainloop()
        

    def iniciar_sesion(self):
        self.boton_login.config(state="disabled")
        usuario = self.entrada_usuario.get()
        contrasena = self.entrada_contrasena.get()
        mensaje_json = json.dumps({"tipo": "login", "username": usuario, "password": contrasena})
        self.cliente.send(mensaje_json.encode('utf-8'))
        respuesta = self.cliente.recv(1024).decode('utf-8')
        respuesta_json = json.loads(respuesta)
        self.boton_login.config(state="normal")

        if respuesta_json["estado"] == "exito":
            self.usuario_actual = usuario
            self.ventana_principal.withdraw()
            self.abrir_chat()
        else:
            messagebox.showerror("Error", "Cliente no registrado. Por favor, intente nuevamente o registrese.")

    def ventana_registro(self):
        self.ventana_reg = tk.Toplevel(self.ventana_principal)
        self.ventana_reg.title("Registro")
        self.ventana_reg.configure(bg="lightblue")
        centrar_ventana(self.ventana_reg, 400, 300)
        tk.Label(self.ventana_reg, text="Registro de Usuario", font=("Arial", 14, "bold"), bg="lightblue").pack(pady=10)
        
        tk.Label(self.ventana_reg, text="Usuario:", font=("Arial",12,"bold"), bg="lightblue").pack(pady=5)
        self.reg_usuario = tk.Entry(self.ventana_reg, font=("Arial", 10))
        self.reg_usuario.pack(pady=5)
        
        tk.Label(self.ventana_reg, text="Contraseña:", font=("Arial",12,"bold"), bg="lightblue").pack(pady=5)
        self.reg_contrasena = tk.Entry(self.ventana_reg, show="*", font=("Arial",10))
        self.reg_contrasena.pack(pady=5)
        
        self.boton_reg = tk.Button(self.ventana_reg, text="Registrar", command=self.registrar, font=("Arial", 10,"bold"), bg="#4CAF50", fg="white")
        self.boton_reg.pack(pady=15)

    def registrar(self):
        usuario = self.reg_usuario.get()
        contrasena = self.reg_contrasena.get()
        mensaje_json = json.dumps({"tipo": "registro", "username": usuario, "password": contrasena})
        self.cliente.send(mensaje_json.encode('utf-8'))
        respuesta = self.cliente.recv(1024).decode('utf-8')
        respuesta_json = json.loads(respuesta)
        if respuesta_json["estado"] == "exito":
            self.ventana_reg.destroy()
            messagebox.showinfo("Éxito", "Usuario registrado con éxito. Ahora puedes iniciar sesión.")
        else:
            messagebox.showerror("Error", "Registro fallido. El usuario ya existe.")
    
    def abrir_chat(self):
        self.ventana_chat = tk.Toplevel(self.ventana_principal, bg="lightgreen")
        self.ventana_chat.title("Chat")
        self.ventana_chat.geometry("900x700")
        
        frame_izquierdo = tk.Frame(self.ventana_chat, bg="lightgreen")
        frame_izquierdo.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        frame_derecho = tk.Frame(self.ventana_chat, bg="lightgrey", width=200)
        frame_derecho.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        
        tk.Label(frame_izquierdo, text=(f"Hola {self.usuario_actual}, bienvenido al chat"),font=("Arial", 12, "bold"), bg="lightgreen").pack(anchor="w")
        self.area_texto = tk.Text(frame_izquierdo, state="disabled", bg="white", fg="black", font=("Arial", 10), wrap=tk.WORD)
        self.area_texto.pack(fill=tk.BOTH, expand=True, pady=5)

        tk.Label(frame_izquierdo, text="Escribe un mensaje:", font=("Arial", 10, "bold"),bg="lightgreen").pack(anchor="w", pady=5)
        self.entrada = tk.Text(frame_izquierdo, font=("Arial", 10), height=5)
        self.entrada.pack(fill=tk.X, pady=5)
        self.entrada.bind('<Return>', self.enviar_mensaje)

        self.boton_enviar = tk.Button(frame_izquierdo, text="Enviar",width=10, height=2, command=self.enviar_mensaje)
        self.boton_enviar.pack(anchor="e", pady=10)
        
        tk.Label(frame_derecho, text="Conectados", font=("Arial", 12, "bold"), bg="lightgrey").pack(pady=5)
        self.lista_usuarios = tk.Listbox(frame_derecho, font=("Arial", 12,"italic"))
        self.lista_usuarios.pack(fill=tk.BOTH, expand=True, pady=5)
        self.lista_usuarios.bind('<Double-1>', self.abrir_chat_privado)  # Agregar el binding para doble clic

        self.hilo = threading.Thread(target=self.recibir_mensajes)
        self.hilo.start()
        self.ventana_chat.protocol("WM_DELETE_WINDOW", self.cerrar_ventana)

    def actualizar_lista_usuarios(self, usuarios):
        self.lista_usuarios.delete(0, tk.END)
        for usuario in usuarios:
            self.lista_usuarios.insert(tk.END, usuario)

    def recibir_mensajes(self):
        while True:
            try:
                mensaje = self.cliente.recv(1024).decode('utf-8')
                if mensaje:
                    mensaje_json = json.loads(mensaje)
                    if mensaje_json["tipo"] == "listar_usuarios":
                        # Actualizar automáticamente la lista de usuarios
                        usuarios = mensaje_json["usuarios"]
                        self.ventana_chat.after(0, self.actualizar_lista_usuarios, usuarios)
                    elif mensaje_json["tipo"] == "broadcast":
                        origen = mensaje_json.get("origen", "Desconocido")
                        contenido = mensaje_json.get("mensaje", "")
                        self.ventana_chat.after(0, self.actualizar_area_texto, f"{origen}: {contenido}")
                    elif mensaje_json["tipo"] == "privado":
                        origen = mensaje_json.get("origen", "Desconocido")
                        contenido = mensaje_json.get("mensaje", "")
                        # Si el chat privado con el remitente no existe, crearlo
                        if origen not in self.chats_privados:
                            self.crear_ventana_privada(origen)
                        ventana, area_mensajes = self.chats_privados[origen]
                        self.ventana_chat.after(0, self.actualizar_area_texto_privado, area_mensajes, f"{origen}: {contenido}")
            except Exception as e:
                print(f"Error receiving message: {e}")
                self.cliente.close()
                break
 
    def actualizar_area_texto(self, mensaje):
        self.area_texto.config(state="normal")
        self.area_texto.insert(tk.END, mensaje + '\n')
        self.area_texto.config(state="disabled")
    
    def enviar_mensaje(self, event=None):
        mensaje = self.entrada.get("1.0", tk.END).strip()  # Obtener el mensaje sin espacios extra
        if mensaje:
            mensaje_json = json.dumps({"tipo": "broadcast", "origen": self.entrada_usuario.get(), "mensaje": mensaje})
            self.cliente.send(mensaje_json.encode('utf-8'))
            
            # Mostrar el mensaje enviado en el área de texto
            self.actualizar_area_texto(f"Yo: {mensaje}")
            
            # Limpiar el campo de entrada
            self.entrada.delete("1.0", tk.END)
        
            # Evitar el salto de línea automático en el widget Text
        if event:
            return "break"

    def abrir_chat_privado(self, event):
        # Obtener el nombre del usuario seleccionado
        seleccion = self.lista_usuarios.curselection()
        if seleccion:
            usuario_destino = self.lista_usuarios.get(seleccion[0])
            if usuario_destino != self.entrada_usuario.get():
                self.crear_ventana_privada(usuario_destino)
            else:
                messagebox.showinfo("Información", "No puedes enviarte mensajes privados a ti mismo.")

    def crear_ventana_privada(self, usuario_destino):
        # Crear una nueva ventana para el chat privado
        ventana_privada = tk.Toplevel(self.ventana_chat, bg="orange")
        ventana_privada.title(f"Chat Privado con {usuario_destino}")
        ventana_privada.geometry("400x500")

        tk.Label(ventana_privada, text=f"Chat Privado con {usuario_destino}", font=("Arial", 12, "bold"),bg="orange").pack(pady=10)

        # Área de texto para mensajes
        area_mensajes = tk.Text(ventana_privada, state="disabled", bg="white", fg="black", font=("Arial", 10), wrap=tk.WORD)
        area_mensajes.pack(fill=tk.BOTH, expand=True, pady=5)

        # Entrada de mensaje
        entrada_mensaje = tk.Text(ventana_privada, font=("Arial", 10), height=5)
        entrada_mensaje.pack(fill=tk.X, pady=5)

        # Evitar que el salto de línea predeterminado ocurra al presionar Enter
        entrada_mensaje.bind('<Return>', lambda event: self.enviar_mensaje_privado(entrada_mensaje, area_mensajes, usuario_destino) or "break")
        # Almacenar referencias de la ventana y el área de mensajes en un diccionario
        self.chats_privados[usuario_destino] = (ventana_privada, area_mensajes)

    def enviar_mensaje_privado(self, entrada_mensaje, area_mensajes, usuario_destino):
        # Obtener el mensaje de la entrada
        mensaje = entrada_mensaje.get("1.0", tk.END).strip()
        if mensaje:
            mensaje_json = json.dumps({
                "tipo": "privado",
                "origen": self.entrada_usuario.get(),
                "destino": usuario_destino,
                "mensaje": mensaje
            })
            self.cliente.send(mensaje_json.encode('utf-8'))

            # Mostrar el mensaje enviado en el área de mensajes
            self.actualizar_area_texto_privado(area_mensajes, f"Yo: {mensaje}")

            # Limpiar el campo de entrada
            entrada_mensaje.delete("1.0", tk.END)

    def actualizar_area_texto_privado(self, area_mensajes, mensaje):
        area_mensajes.config(state="normal")
        area_mensajes.insert(tk.END, mensaje + '\n')
        area_mensajes.config(state="disabled")


    def cerrar_ventana(self):
        try:
            # Enviar mensaje de desconexión al servidor
            self.cliente.send(json.dumps({"tipo": "desconexion"}).encode('utf-8'))
        except Exception as e:
            print(f"Error during disconnect: {e}")
        finally:
            # Cerrar el socket
            self.cliente.close()
            # Destruir todas las ventanas
            self.ventana_principal.destroy()


if __name__ == "__main__":
    cliente = ClienteChat()

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import networkx as nx
import random
import colorsys
import json
import os

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class SocialNetworkApp:
    def _init_(self, root):
        self.root = root
        self.root.title("Visualizador de Comunidad - Grafo Social")
        self.root.geometry("1200x800")

        # Datos principales
        self.usuarios = []
        self.grafo = nx.DiGraph()
        self.conexiones = {}  # lista de adyacencia con pesos

        self.layout_actual = tk.StringVar(value="spring")
        self.umbral_peso = 4

        self.crear_interfaz()
        self.generar_red_inicial()

    def crear_interfaz(self):
        panel = ttk.Frame(self.root)
        panel.pack(fill="both", expand=True, padx=10, pady=10)

        # Controles
        controles = ttk.Frame(panel)
        controles.pack(fill="x", pady=5)

        ttk.Button(controles, text="Crear Red Aleatoria", command=self.generar_red_inicial).pack(side="left", padx=5)
        ttk.Button(controles, text="Agregar Nodo", command=self.agregar_usuario).pack(side="left", padx=5)
        ttk.Button(controles, text="Conectar Nodos", command=self.conectar_usuarios).pack(side="left", padx=5)
        ttk.Button(controles, text="Guardar Red", command=self.guardar_red).pack(side="left", padx=5)
        ttk.Button(controles, text="Cargar Red", command=self.cargar_red).pack(side="left", padx=5)

        # Opciones extra
        ttk.Label(controles, text="Layout:").pack(side="left", padx=5)
        layout_combo = ttk.Combobox(controles, textvariable=self.layout_actual, values=["spring", "circular", "random"])
        layout_combo.pack(side="left", padx=5)
        layout_combo.bind("<<ComboboxSelected>>", lambda e: self.actualizar_grafo())

        # Umbral
        self.umbral_var = tk.IntVar(value=self.umbral_peso)
        ttk.Label(controles, text="Umbral:").pack(side="left", padx=5)
        umbral_slider = ttk.Scale(controles, from_=1, to=10, orient="horizontal", variable=self.umbral_var, command=self.cambiar_umbral)
        umbral_slider.pack(side="left", padx=5)

        # Información
        self.info = tk.Text(panel, height=6)
        self.info.pack(fill="x", pady=5)

        # Gráfico
        self.fig = Figure(figsize=(8, 6))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=panel)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def generar_red_inicial(self):
        self.usuarios = [f"Persona_{i}" for i in range(15)]
        self.conexiones = {u: {} for u in self.usuarios}

        for usuario in self.usuarios:
            amigos = random.sample(self.usuarios, random.randint(2, 5))
            for amigo in amigos:
                if amigo != usuario:
                    peso = random.randint(1, 10)
                    self.conexiones[usuario][amigo] = peso

        self.actualizar_grafo()
        self.mostrar_info("Red inicial generada.")

    def actualizar_grafo(self):
        self.grafo.clear()
        for u in self.usuarios:
            self.grafo.add_node(u)

        for u, vecinos in self.conexiones.items():
            for v, peso in vecinos.items():
                if peso >= self.umbral_peso:
                    self.grafo.add_edge(u, v, weight=peso)

        layout = self.layout_actual.get()
        if layout == "spring":
            pos = nx.spring_layout(self.grafo)
        elif layout == "circular":
            pos = nx.circular_layout(self.grafo)
        else:
            pos = nx.random_layout(self.grafo)

        self.ax.clear()
        colores = self.generar_colores(len(self.grafo.nodes()))
        nx.draw(self.grafo, pos, ax=self.ax, with_labels=True, node_color=colores, edge_color='gray', node_size=600, arrows=True)
        etiquetas = nx.get_edge_attributes(self.grafo, 'weight')
        nx.draw_networkx_edge_labels(self.grafo, pos, edge_labels=etiquetas, ax=self.ax)
        self.ax.set_title(f"Grafo - Umbral ≥ {self.umbral_peso}")
        self.canvas.draw()

    def generar_colores(self, n):
        # Paleta de colores pastel
        return [colorsys.hsv_to_rgb(i/n, 0.5, 0.9) for i in range(n)]

    def agregar_usuario(self):
        nombre = simpledialog.askstring("Agregar Nodo", "Nombre del nuevo nodo:")
        if nombre and nombre not in self.usuarios:
            self.usuarios.append(nombre)
            self.conexiones[nombre] = {}
            self.actualizar_grafo()
            self.mostrar_info(f"Nodo '{nombre}' agregado.")
        else:
            messagebox.showerror("Error", "Nombre inválido o existente.")

    def conectar_usuarios(self):
        if len(self.usuarios) < 2:
            messagebox.showerror("Error", "Se necesitan al menos 2 nodos.")
            return

        u1 = simpledialog.askstring("Nodo Origen", f"Nodos: {', '.join(self.usuarios)}\nOrigen:")
        if not u1 or u1 not in self.usuarios:
            return

        u2 = simpledialog.askstring("Nodo Destino", f"Nodos: {', '.join(self.usuarios)}\nDestino:")
        if not u2 or u2 not in self.usuarios or u1 == u2:
            return

        peso = simpledialog.askinteger("Peso", "Peso (1-10):", minvalue=1, maxvalue=10)
        if peso:
            self.conexiones[u1][u2] = peso
            self.actualizar_grafo()
            self.mostrar_info(f"Conexión creada: {u1} → {u2} (peso: {peso})")

    def cambiar_umbral(self, val):
        self.umbral_peso = int(float(val))
        self.actualizar_grafo()

    def guardar_red(self):
        datos = {
            "usuarios": self.usuarios,
            "conexiones": self.conexiones,
            "umbral": self.umbral_peso
        }
        with open("red_guardada.json", "w") as f:
            json.dump(datos, f, indent=2)
        self.mostrar_info("Red guardada en 'red_guardada.json'.")

    def cargar_red(self):
        if not os.path.exists("red_guardada.json"):
            messagebox.showerror("Error", "No existe archivo guardado.")
            return
        with open("red_guardada.json") as f:
            datos = json.load(f)
            self.usuarios = datos["usuarios"]
            self.conexiones = datos["conexiones"]
            self.umbral_peso = datos.get("umbral", 4)
            self.umbral_var.set(self.umbral_peso)
            self.actualizar_grafo()
            self.mostrar_info("Red cargada exitosamente.")

    def mostrar_info(self, texto):
        self.info.delete(1.0, tk.END)
        self.info.insert(tk.END, texto)


def main():
    root = tk.Tk()
    app = SocialNetworkApp(root)
    root.mainloop()

if _name_ == "_main_":
    main()

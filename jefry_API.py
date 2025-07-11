import tkinter as tk
from tkinter import ttk, messagebox
import folium
from folium.plugins import MarkerCluster
import webbrowser
import openrouteservice

class PunoORSApp:
    def _init_(self, root):
        self.root = root
        self.root.title("🗺️ Mapa de Rutas Turísticas - Puno con ORS")
        self.root.geometry("500x400")
        self.root.resizable(False, False)

        
        self.ors_client = openrouteservice.Client(key="eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6Ijc5NmZjMDdmZDJkYTQ5YmI5OTI0ODQ3MmUwNmEwY2RhIiwiaCI6Im11cm11cjY0In0=")

        # Lugares concurridos de Puno
        self.lugares = {
            "Plaza de Armas": (-15.840660, -70.027979),
            "Universidad Nacional del Altiplano": (-15.835666, -70.021576),
            "Terminal Terrestre": (-15.828007, -70.016079),
            "Puerto Lacustre": (-15.840000, -70.025000),
            "Mirador Kuntur Wasi": (-15.829524, -70.030024),
            "Catedral de Puno": (-15.840460, -70.028180),
            "Museo Carlos Dreyer": (-15.840100, -70.027500),
            "Arco Deustua": (-15.838689, -70.026005),
            "Iglesia San Juan Bautista": (-15.838900, -70.025400),
            "Parque Pino": (-15.838700, -70.026700),
            "Cerro Huajsapata": (-15.838200, -70.031200),
            "Estación de Trenes": (-15.837100, -70.024400),
            "Isla Esteves": (-15.823000, -70.017000),
            "Bahía de los Incas": (-15.838500, -70.029000),
        }

        # Combobox vars
        self.origen_var = tk.StringVar(value="Plaza de Armas")
        self.destino_var = tk.StringVar(value="Puerto Lacustre")

        # GUI
        ttk.Label(root, text="📍 Origen:").pack(pady=5)
        self.origen_combo = ttk.Combobox(
            root, textvariable=self.origen_var,
            values=list(self.lugares.keys()), state="readonly"
        )
        self.origen_combo.pack()

        ttk.Label(root, text="🎯 Destino:").pack(pady=5)
        self.destino_combo = ttk.Combobox(
            root, textvariable=self.destino_var,
            values=list(self.lugares.keys()), state="readonly"
        )
        self.destino_combo.pack()

        ttk.Button(
            root, text="🚶‍♂️ Generar Ruta con OpenRouteService",
            command=self.generar_ruta
        ).pack(pady=20)

    def generar_ruta(self):
        origen = self.origen_var.get()
        destino = self.destino_var.get()

        if not origen or not destino:
            messagebox.showwarning("⚠️ Advertencia", "Selecciona origen y destino.")
            return

        if origen == destino:
            messagebox.showwarning("⚠️ Advertencia", "Origen y destino deben ser diferentes.")
            return

        coords_origen = self.lugares[origen][::-1]  # ORS usa (lon, lat)
        coords_destino = self.lugares[destino][::-1]

        try:
            # Llamar a ORS para ruta a pie
            route = self.ors_client.directions(
                coordinates=[coords_origen, coords_destino],
                profile='foot-walking',
                format='geojson'
            )

            geometry = route['features'][0]['geometry']['coordinates']

            # Convertir a formato folium (lat, lon)
            ruta_coords = [(lat, lon) for lon, lat in geometry]

            # Crear mapa
            m = folium.Map(location=self.lugares[origen], zoom_start=14)
            marker_cluster = MarkerCluster().add_to(m)

            # Marcadores
            for nombre, coords in self.lugares.items():
                color = "red" if nombre in [origen, destino] else "blue"
                folium.Marker(
                    location=coords,
                    popup=nombre,
                    icon=folium.Icon(color=color)
                ).add_to(marker_cluster)

            # Dibujar ruta real
            folium.PolyLine(
                locations=ruta_coords,
                color="green",
                weight=5,
                opacity=0.7
            ).add_to(m)

            # Guardar y abrir
            map_filename = "ruta_puno_ors.html"
            m.save(map_filename)
            webbrowser.open(map_filename)

            distancia_km = route['features'][0]['properties']['summary']['distance'] / 1000
            duracion_min = route['features'][0]['properties']['summary']['duration'] / 60

            messagebox.showinfo(
                "✅ Ruta generada",
                f"De {origen} a {destino}:\nDistancia: {distancia_km:.2f} km\nDuración estimada: {duracion_min:.1f} min"
            )

        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al solicitar ruta ORS:\n{e}")

def main():
    root = tk.Tk()
    app = PunoORSApp(root)
    root.mainloop()

if _name_ == "_main_":
    main()

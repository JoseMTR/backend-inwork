import os

import requests
from dotenv import load_dotenv

load_dotenv()


class CustodiaRepository:
  

    def __init__(self):
        self.url = os.getenv("PAGOS_API_URL", "http://localhost:3000") + "/api/custodias"

    def crear(self, datos: dict):
        """Crea la custodia. Devuelve (True/False, respuesta de la API de pagos)."""
        try:
            respuesta = requests.post(self.url, json=datos, timeout=10)
            return respuesta.status_code == 201, respuesta.json()
        except requests.exceptions.RequestException:
            return False, {"mensaje": "No se pudo conectar con la API de pagos"}

    def obtener_por_contratacion(self, id_contratacion: int):
        """
        Devuelve (conectado, custodia).
        conectado = False si la API de pagos no responde.
        custodia = None si esa contratacion no tiene custodia.
        """
        try:
            respuesta = requests.get(f"{self.url}/contratacion/{id_contratacion}", timeout=10)
            if respuesta.status_code == 404:
                return True, None
            return True, respuesta.json()
        except requests.exceptions.RequestException:
            return False, None

    def cancelar(self, id_custodia: int):
        """Cancela una custodia que todavia no ha sido pagada."""
        try:
            respuesta = requests.delete(f"{self.url}/{id_custodia}", timeout=10)
            return respuesta.status_code == 200, respuesta.json()
        except requests.exceptions.RequestException:
            return False, {"mensaje": "No se pudo conectar con la API de pagos"}

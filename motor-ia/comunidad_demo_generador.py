"""Controlador gradual de comunidad simulada.

No inicia automaticamente.
No escribe bases de datos.
No publica mensajes en Discord.
"""

import random
from threading import Event, Lock, Thread

from comunidad_demo_config import validar_configuracion
from comunidad_demo_conversaciones import generar_consulta
from comunidad_demo_pipeline import preparar_mensaje


class GeneradorComunidadDemo:
    def __init__(self, consumidor=None):
        self._bloqueo = Lock()
        self._detener = Event()
        self._hilo = None
        self._consumidor = consumidor
        self._generados = 0
        self._ultimo_error = None

    def estado(self):
        with self._bloqueo:
            activo = (
                self._hilo is not None
                and self._hilo.is_alive()
            )
            return {
                "ejecutando": activo,
                "mensajes_generados": self._generados,
                "ultimo_error": self._ultimo_error,
                "publicar_discord": False,
            }

    def iniciar(self, tema="mixto", ritmo="medio"):
        config = validar_configuracion(tema, ritmo)

        with self._bloqueo:
            if self._hilo is not None and self._hilo.is_alive():
                return False

            self._detener.clear()
            self._ultimo_error = None

            self._hilo = Thread(
                target=self._ejecutar,
                args=(tema, config),
                name="cloudedtech-comunidad-demo",
                daemon=True,
            )
            self._hilo.start()

            return True

    def detener(self):
        self._detener.set()

        with self._bloqueo:
            hilo = self._hilo

        if hilo is not None and hilo.is_alive():
            if hilo is not __import__("threading").current_thread():
                hilo.join(timeout=2)

        return not (hilo is not None and hilo.is_alive())

    def _ejecutar(self, tema, config):
        rng = random.SystemRandom()
        usados_sesion = set()

        minimo = config["intervalo_minimo_segundos"]
        maximo = config["intervalo_maximo_segundos"]

        while not self._detener.is_set():
            intervalo = rng.uniform(minimo, maximo)

            if self._detener.wait(intervalo):
                break

            try:
                mensaje = generar_consulta(
                    tema,
                    usados=usados_sesion,
                    rng=rng,
                )
                actividad = preparar_mensaje(mensaje)

                if self._consumidor is not None:
                    self._consumidor(mensaje, actividad)

                with self._bloqueo:
                    self._generados += 1

            except Exception as error:
                with self._bloqueo:
                    self._ultimo_error = (
                        f"{type(error).__name__}: {error}"
                    )
                self._detener.set()
                break
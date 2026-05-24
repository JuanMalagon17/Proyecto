"""
conftest.py — Configuración raíz para pytest y unittest.

Este archivo le dice a Python que la raíz del proyecto
es el punto de partida para las importaciones.
Con esto, tanto `python -m unittest` como `pytest` funcionan
correctamente sin importar desde qué carpeta se ejecuten.
"""
import sys
import os

# Agrega la raíz del proyecto al path de Python
sys.path.insert(0, os.path.dirname(__file__))

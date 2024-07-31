# Visor del Historial del Portapapeles (pp.py)

## Descripción

El script `pp.py` implementa un Visor del Historial del Portapapeles, una aplicación gráfica que monitorea y gestiona el contenido copiado al portapapeles del sistema. Esta herramienta mejora la productividad al permitir un acceso rápido a elementos previamente copiados.

## Características Principales

- Monitoreo continuo del portapapeles del sistema.
- Almacenamiento de un historial de los últimos 20 elementos copiados.
- Interfaz gráfica para visualizar y acceder al historial del portapapeles.
- Función de auto-copia al pasar el mouse sobre un elemento del historial.
- Detección de la combinación de teclas Ctrl+C para actualizar el historial.
- Capacidad para borrar el historial y ajustar el tamaño de la fuente.

El script utiliza threading para realizar el monitoreo del portapapeles en segundo plano, permitiendo que la interfaz de usuario permanezca responsiva. También implementa mecanismos de sincronización para evitar condiciones de carrera al acceder al portapapeles.

## Librerías Necesarias

Para ejecutar `pp.py`, necesitarás instalar las siguientes librerías:

1. **pywin32**: Proporciona acceso a las API de Windows, incluyendo funciones para interactuar con el portapapeles.
   ```
   pip install pywin32
   ```

2. **pyautogui**: Utilizada para simular eventos de teclado, específicamente para pegar el contenido del portapapeles.
   ```
   pip install pyautogui
   ```

3. **pynput**: Empleada para detectar eventos de teclado a nivel de sistema.
   ```
   pip install pynput
   ```

Además, el script utiliza las siguientes librerías que son parte de la biblioteca estándar de Python y no requieren instalación adicional:

- `tkinter`: Para crear la interfaz gráfica de usuario.
- `threading`: Para implementar la concurrencia y el monitoreo en segundo plano.
- `time`: Para manejar retrasos y tiempos de espera.
- `collections`: Para utilizar la estructura de datos `deque`.

## Instalación

Se recomienda crear un entorno virtual de Python antes de instalar las dependencias:

```
python -m venv venv
source venv/bin/activate  # En Windows use `venv\Scripts\activate`
pip install pywin32 pyautogui pynput
```

## Uso

Para ejecutar el script, simplemente usa:

```
python pp.py
```

Una vez iniciado, la aplicación monitoreará automáticamente el portapapeles y mostrará una interfaz gráfica con el historial de elementos copiados.

## Nota

Este script está diseñado para funcionar en sistemas Windows debido al uso de `pywin32` para acceder al portapapeles del sistema.

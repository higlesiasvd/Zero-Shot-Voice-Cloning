# Zero-Shot Voice Cloning

Este proyecto implementa clonación de voz zero-shot utilizando modelos TTS avanzados (XTTS-v2 y VITS) y métricas de similitud de voz. Permite generar audios sintéticos que imitan la voz de un audio de referencia sin necesidad de entrenamiento previo.

## Requisitos

- Docker
- Make (GNU Make)
- Acceso a internet para descargar modelos y dependencias

## Estructura del proyecto

- `main.py`: Script principal para la clonación y evaluación de voz.
- `Dockerfile`: Define el entorno de ejecución reproducible.
- `Makefile`: Automatiza la construcción y ejecución del proyecto.
- `requirements.txt`: Dependencias de Python.
- `audio_samples/`: Carpeta para audios de referencia.
- `results/`: Carpeta donde se guardan los resultados, métricas y audios generados.

## Uso rápido

1. **Construir la imagen Docker:**

   ```sh
   make build
   ```
2. **Ejecutar el proceso de clonación de voz:**

   ```sh
   make run
   ```

   Esto generará los audios clonados y los resultados en la carpeta `results/`.
3. **Limpiar archivos generados (opcional):**

   ```sh
   make clean
   ```

## Descripción de comandos del Makefile

- `make build`: Construye la imagen Docker necesaria para el proyecto.
- `make run`: Ejecuta el script principal dentro del contenedor Docker, generando los audios y métricas.
- `make clean`: Elimina los archivos generados en la carpeta `results/`.

## Notas importantes

- Si ejecutas el proyecto en un sistema con espacios en las rutas, asegúrate de que el Makefile utilice comillas en los volúmenes de Docker.
- El script puede requerir aceptar licencias de modelos de voz. Consulta la documentación de cada modelo si es necesario automatizar la aceptación.
- Los resultados incluyen métricas de similitud, gráficos comparativos y los audios generados.

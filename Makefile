# Makefile - Práctica 3 TTS Zero-Shot (Mac M4 Pro)

IMAGE_NAME = practica3-tts
CONTAINER_NAME = tts-cloning

.PHONY: help build run clean

help:
	@echo "Práctica 3 - Zero-Shot Voice Cloning (Mac M4 Pro)"
	@echo "================================================="
	@echo ""
	@echo "IMPORTANTE: Usa emulación x86 para compatibilidad"
	@echo "Será más lento pero funcionará correctamente"
	@echo ""
	@echo "Comandos:"
	@echo "  make build  - Construir imagen (15-20 min primera vez)"
	@echo "  make run    - Ejecutar clonación de voz"
	@echo "  make clean  - Limpiar todo"
	@echo ""

build:
	@echo "Construyendo imagen Docker con emulación x86..."
	@echo "PRIMERA VEZ: Tardará 15-20 minutos"
	@echo ""
	docker build --platform linux/amd64 -t $(IMAGE_NAME):latest .
	@echo ""
	@echo "Imagen construida"

run:
	@echo "Ejecutando ZERO-SHOT VOICE CLONING..."
	@echo ""
	docker run --rm --platform linux/amd64 \
    	--name $(CONTAINER_NAME) \
		-e COQUI_TOS_AGREED=1 \
    	-v "$(PWD)/results:/app/results" \
    	-v "$(PWD)/audio_samples:/app/audio_samples" \
    	 $(IMAGE_NAME):latest
	@echo ""
	@echo "Completado. Ver resultados en ./results/"

clean:
	@echo "Limpiando..."
	docker stop $(CONTAINER_NAME) 2>/dev/null || true
	docker rm $(CONTAINER_NAME) 2>/dev/null || true
	docker rmi $(IMAGE_NAME):latest 2>/dev/null || true
	@echo "Limpieza completada"

.DEFAULT_GOAL := help
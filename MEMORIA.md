# Memoria de la Práctica 

# **Enlace a repositorio:** [https://github.com/higlesiasvd/Zero-Shot-Voice-Cloning.git](https://github.com/higlesiasvd/Zero-Shot-Voice-Cloning.git)

## TTS Zero-Shot Voice Cloning

**Asignatura:** Sistemas Interactivos Inteligentes
**Universidad:** Universidad Intercontinental de la Empresa
**Autor:** Hugo Iglesias Pombo

---

## 1. Introducción

Esta práctica implementa **zero-shot voice cloning** utilizando modelos avanzados de Text-to-Speech (TTS). El objetivo es demostrar que es posible clonar la voz de una persona a partir de un breve fragmento de audio (3-10 segundos) y generar nuevos audios donde esa voz pronuncie palabras completamente diferentes, sin necesidad de entrenar o afinar el modelo previamente.

El zero-shot voice cloning representa uno de los avances más significativos en síntesis de voz, permitiendo aplicaciones que van desde asistentes virtuales personalizados hasta herramientas de accesibilidad para personas con dificultades del habla.

## 2. Selección de Modelos

### 2.1. XTTS-v2 (Coqui TTS) - Modelo Principal

**Justificación de selección:**

XTTS-v2 fue seleccionado como modelo principal porque representa el **estado del arte en zero-shot voice cloning**. Las razones específicas son:

1. **Verdadero zero-shot cloning:** A diferencia de modelos que requieren voces predefinidas, XTTS-v2 puede clonar cualquier voz a partir de 3-10 segundos de audio sin ningún entrenamiento adicional.
2. **Capacidad multilingüe:** Soporta 17 idiomas incluyendo español e inglés, lo que lo hace extremadamente versátil para aplicaciones reales.
3. **Arquitectura avanzada:** Utiliza transformers con mecanismos de atención que capturan tanto características acústicas (timbre, tono) como prosódicas (ritmo, entonación) de la voz.
4. **Calidad superior:** En la literatura científica, XTTS-v2 ha demostrado resultados superiores a modelos anteriores en métricas de similitud y naturalidad.

**Arquitectura técnica:**

El modelo funciona en varias etapas:

- **Encoder de voz:** Extrae embeddings de 512 dimensiones del audio de referencia
- **Encoder de texto:** Convierte el texto a tokens semánticos
- **Decoder GPT:** Genera representaciones acústicas condicionadas por el embedding de voz
- **Vocoder HiFi-GAN:** Convierte la representación a forma de onda audible

### 2.2. VITS - Modelo de Comparación

Para cumplir con el requisito de comparar dos modelos diferentes, se implementó VITS (Variational Inference with adversarial learning for end-to-end Text-to-Speech):

**Características:**

- Arquitectura end-to-end que no requiere vocoder separado
- Usa voces predefinidas (multi-speaker) en lugar de zero-shot cloning
- Generalmente más rápido en inferencia
- Permite contrastar con verdadero clonado de voz

**Propósito:** Demostrar empíricamente la diferencia entre un modelo que usa voces predefinidas versus uno que clona la voz específica del audio de referencia.

## 3. Implementación Técnica

### 3.1. Desafío: Compatibilidad con Mac ARM

Durante la implementación se encontró un desafío técnico significativo: XTTS-v2 tiene dependencias (sudachipy, webrtcvad) que requieren compiladores Rust y C++, los cuales causan fallos en arquitecturas ARM (Mac M1/M2/M3/M4).

**Solución implementada:**

Se utilizó **emulación x86 en Docker** mediante la opción `--platform linux/amd64`. Esto permite:

- Ejecutar el código completo sin modificaciones
- Compatibilidad total con todas las dependencias
- Funcionalidad completa del modelo
- Con el trade-off de mayor tiempo de ejecución (2-3x más lento que nativo)

Esta solución demuestra la importancia de considerar aspectos de portabilidad y compatibilidad en el desarrollo de sistemas de IA.

### 3.2. Pipeline de Procesamiento

El pipeline implementado sigue estos pasos:

1. **Preparación del audio de referencia:**

   - Descarga automática desde el dataset LibriSpeech
   - Dataset ético de dominio público diseñado para investigación
   - Audio de alta calidad sin ruido de fondo
2. **Generación con zero-shot cloning:**

   - XTTS-v2 extrae embeddings del audio de referencia
   - Genera 3 audios diferentes con textos variados
   - Cada audio mantiene las características de la voz original
3. **Generación con VITS (comparación):**

   - Usa speaker ID predefinido (voz femenina "p225")
   - Genera los mismos 3 textos para comparación
   - No clona el audio de referencia
4. **Evaluación con métricas objetivas**

## 4. Métricas de Evaluación

### 4.1. Similitud de Voz (Métrica Principal)

**Técnica: Resemblyzer**

Se utilizó Resemblyzer, que implementa speaker verification mediante embeddings de voz profundos:

**Metodología:**

1. Extrae embeddings de 256 dimensiones de cada audio
2. Los embeddings capturan características únicas de la voz (timbre, registro, características espectrales)
3. Calcula similitud de coseno entre embeddings
4. Resultado: valor de 0 (completamente diferente) a 1 (idéntico)

**Interpretación de valores:**

- **0.80-1.00:** Excelente clonación
- **0.70-0.80:** Buena clonación
- **0.60-0.70:** Clonación aceptable
- **<0.60:** Clonación pobre o voz diferente

Esta métrica es estándar en la literatura de voice cloning y es independiente del contenido lingüístico, evaluando puramente características de la voz.

### 4.2. Métricas de Calidad de Audio

**RMS Energy (Root Mean Square):**

- Mide la energía promedio de la señal
- Indica el volumen y potencia del audio
- Útil para detectar problemas de normalización

**Zero Crossing Rate:**

- Frecuencia de cambios de signo en la señal
- Relacionado con el contenido espectral
- Valores muy altos o bajos pueden indicar artefactos

**Duración:**

- Tiempo total del audio generado
- Verifica que la velocidad de habla sea natural

### 4.3. Métricas de Rendimiento

**Tiempo de generación:**

- Crítico para aplicaciones en tiempo real
- Mide la eficiencia computacional
- En TTS, latencias >2s pueden afectar experiencia de usuario

## 5. Resultados Obtenidos

### 5.1. Resultados XTTS-v2 (Zero-Shot Cloning)

**Similitud de voz:**

- Promedio: **0.8363** (83.63%)
- Desviación estándar: 0.0254
- Rango: 0.8083 - 0.8699

**Análisis:**
Los resultados demuestran una **clonación exitosa** de la voz original. Una similitud de 0.8363 indica que:

- El modelo capturó el timbre característico de la voz
- Mantuvo las características prosódicas
- Los audios generados suenan notablemente similares al original
- La consistencia es alta (desviación estándar baja de 0.0254)

**Percepción auditiva:**
Al escuchar los audios generados y compararlos con el audio de referencia, se confirma que **la voz clonada se parece mucho a la original**. El modelo capturó exitosamente las características únicas del hablante.

**Tiempo de generación:**

- Promedio: **9.11 segundos** por audio
- Total para 3 audios: 27.33 segundos

Este tiempo es aceptable para aplicaciones no críticas en tiempo real. En un contexto de producción de contenido o generación de audiolibros, esta latencia es completamente viable.

### 5.2. Resultados VITS (Comparación)

**Similitud de voz:**

- Promedio: **0.5049** (50.49%)
- Desviación estándar: 0.0139
- Rango: 0.4918 - 0.5241

**Análisis:**
Los resultados muestran **baja similitud** con el audio de referencia, lo cual es esperado porque:

- VITS no realiza zero-shot cloning
- Usa una voz predefinida (speaker "p225" - voz femenina)
- No extrae características del audio de referencia

**Percepción auditiva:**
Los audios generados por VITS **suenan como una voz femenina predefinida**, completamente diferente al audio de referencia (voz masculina). Esto valida empíricamente que VITS no está realizando clonación de voz.

**Tiempo de generación:**

- Promedio: **1.60 segundos** por audio
- Total para 3 audios: 4.80 segundos
- **5.70x más rápido que XTTS-v2**

La velocidad superior de VITS se debe a:

- No necesita extraer embeddings del audio de referencia
- Arquitectura más simple para voces predefinidas
- Menos parámetros a procesar

### 5.3. Comparación Entre Modelos

| Métrica                     | XTTS-v2 | VITS   | Diferencia |
| ---------------------------- | ------- | ------ | ---------- |
| **Similitud de voz**   | 0.8363  | 0.5049 | +33.15%    |
| **Desv. estándar**    | 0.0254  | 0.0139 | +82%       |
| **Tiempo generación** | 9.11s   | 1.60s  | -83%       |
| **Velocidad relativa** | 1x      | 5.70x  | -          |

**Conclusiones de la comparación:**

1. **Calidad vs. Velocidad:** Existe un trade-off claro entre calidad de clonación y velocidad de generación. XTTS-v2 produce voces mucho más similares al original pero tarda más.
2. **Validación del zero-shot cloning:** La diferencia de 33.15% en similitud demuestra empíricamente que XTTS-v2 está realizando verdadera clonación de voz, mientras que VITS simplemente usa una voz predefinida.
3. **Consistencia:** XTTS-v2 tiene mayor variabilidad entre pruebas (desv. std. 0.0254) comparado con VITS (0.0139), lo cual es razonable dado que está adaptándose a una voz específica.
4. **Aplicabilidad:** Para aplicaciones donde la similitud de voz es crítica (asistentes personalizados, accesibilidad), XTTS-v2 es claramente superior. Para aplicaciones donde la velocidad es prioritaria y la voz específica no importa (navegación, notificaciones), VITS podría ser suficiente.

## 6. Análisis Detallado por Prueba

### Prueba 1

**Texto:** "Hello, this is a demonstration of zero-shot voice cloning technology."

- XTTS-v2: Similitud 0.8083 | 9.95s
- VITS: Similitud 0.4918 | 1.64s

Este es el texto más largo, lo que explica los tiempos mayores. XTTS logró buena similitud incluso en frases largas.

### Prueba 2

**Texto:** "Artificial intelligence can now replicate human voices with remarkable accuracy."

- XTTS-v2: Similitud **0.8699** (la mejor) | 11.49s
- VITS: Similitud 0.4987 | 1.63s

Esta prueba muestra el mejor resultado de XTTS-v2, alcanzando casi 87% de similitud. El texto técnico no afectó negativamente el rendimiento.

### Prueba 3

**Texto:** "This synthesized speech should sound similar to the reference audio provided."

- XTTS-v2: Similitud 0.8309 | 5.89s (el más rápido)
- VITS: Similitud **0.5241** (la mejor para VITS) | 1.52s

Texto más corto resultó en generación más rápida para ambos modelos.

## 7. Consideraciones de Rendimiento

### 7.1. Latencia en Sistemas Interactivos

En sistemas de interacción humano-computadora, la latencia es crucial:

- **<500ms:** Imperceptible, ideal para diálogo
- **500ms-2s:** Perceptible pero aceptable
- **>2s:** Puede interrumpir el flujo conversacional

Con un promedio de 9.11s, XTTS-v2 **no es adecuado para diálogo en tiempo real** en su configuración actual. Sin embargo, es perfectamente viable para:

- Generación de contenido offline (audiolibros, videos)
- Sistemas con tiempo de espera aceptable
- Aplicaciones donde la calidad prima sobre velocidad

### 7.2. Optimizaciones Posibles

Para reducir latencia en aplicaciones futuras:

1. **Usar GPU:** La emulación x86 en CPU es 2-3x más lenta que nativo
2. **Streaming:** Implementar generación incremental en lugar de esperar audio completo
3. **Caché de embeddings:** El embedding del speaker se puede calcular una vez y reutilizar
4. **Cuantización:** Reducir precisión del modelo para inferencia más rápida

## 8. Consideraciones Éticas

### 8.1. Implicaciones del Voice Cloning

La capacidad de clonar voces plantea cuestiones éticas importantes:

**Riesgos potenciales:**

- Impersonación fraudulenta
- Deepfakes de voz para desinformación
- Violación de privacidad
- Uso no autorizado de voces de personas

## 9. Conclusiones

### 9.1. Logros Principales

1. **Implementación exitosa** de zero-shot voice cloning con similitud de **83.63%**
2. **Comparación empírica** que demuestra la diferencia entre zero-shot cloning y voces predefinidas
3. **Solución técnica** para compatibilidad con Mac ARM mediante emulación x86
4. **Evaluación objetiva** con métricas estándar de la industria

### 9.2. Validación de Hipótesis

La práctica confirma que:

- Es posible clonar voces con alta fidelidad (>80%) usando zero-shot learning
- XTTS-v2 supera significativamente a modelos con voces predefinidas
- Existe trade-off medible entre calidad y velocidad
- La tecnología es viable para aplicaciones reales

### 9.3. Aprendizajes Técnicos

**Sobre zero-shot cloning:**

- Los embeddings de voz de 512 dimensiones capturan características suficientes para clonación
- La arquitectura transformer es efectiva para mantener coherencia prosódica
- 3-10 segundos de audio de referencia son suficientes

**Sobre implementación:**

- La compatibilidad de plataforma es un desafío real en IA
- Docker con emulación es una solución viable pero con costos de rendimiento
- Las métricas objetivas validan lo que se percibe auditivamente

### 9.4. Trabajo Futuro

**Mejoras técnicas:**

1. Probar con audios de referencia en español
3. Implementar streaming para reducir latencia percibida
4. Evaluar con evaluación MOS (Mean Opinion Score) humana

**Aplicaciones potenciales:**

1. Asistentes virtuales personalizados
2. Herramientas de accesibilidad (banco de voz personal)
3. Localización de contenido multimedia
4. Educación personalizada

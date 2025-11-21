#!/usr/bin/env python3
"""
Práctica 3 - TTS Zero-Shot Voice Cloning
Universidad Intercontinental de la Empresa
Sistemas Interactivos Inteligentes

ZERO-SHOT VOICE CLONING con XTTS-v2
"""

import os
import sys
import torch
from TTS.api import TTS
from resemblyzer import VoiceEncoder, preprocess_wav
import librosa
import soundfile as sf
import numpy as np
from scipy.spatial.distance import cosine
import json
import time
import matplotlib.pyplot as plt
from datasets import load_dataset

print("="*70)
print("PRÁCTICA 3 - ZERO-SHOT VOICE CLONING")
print("Universidad Intercontinental de la Empresa")
print("="*70)
print("\nUsando verdadero zero-shot cloning con XTTS-v2")
print("="*70)

# Crear directorios
os.makedirs("audio_samples", exist_ok=True)
os.makedirs("results", exist_ok=True)

# ============================================================================
# PASO 1: Preparar audio de referencia
# ============================================================================
print("\n[1/4] Preparando audio de referencia...")  # Paso 1: preparar audio de referencia
try:
    print("Descargando audio del dataset LibriSpeech (dominio público)...")
    dataset = load_dataset("hf-internal-testing/librispeech_asr_dummy", "clean", split="validation")
    audio_sample = dataset[0]
    reference_audio = "audio_samples/reference.wav"
    sf.write(reference_audio, audio_sample["audio"]["array"], audio_sample["audio"]["sampling_rate"])
    print(f"Audio guardado: {reference_audio}")
    print(f"  Duración: {len(audio_sample['audio']['array']) / audio_sample['audio']['sampling_rate']:.2f}s")
    print(f"  Transcripción original: '{audio_sample['text']}'")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

# ============================================================================
# PASO 2: Inicializar modelos
# ============================================================================
print("\n[2/4] Inicializando modelos TTS...")  # Paso 2: inicializar modelos

device = "cpu"  # Usar CPU en emulación x86
print(f"Usando dispositivo: {device}")

print("\nCargando XTTS-v2 (Coqui TTS)...")
print("  Este modelo clonará la voz del audio de referencia")
try:
    tts_xtts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2").to(device)
    print("XTTS-v2 listo")
except Exception as e:
    print(f"Error cargando XTTS-v2: {e}")
    print("  Intentando descargar modelos...")
    try:
        tts_xtts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=True).to(device)
    print("XTTS-v2 listo")
    except Exception as e2:
    print(f"Error: {e2}")
        sys.exit(1)

print("\nCargando VITS...")
print("  Este modelo también puede clonar voces")
try:
    tts_vits = TTS(model_name="tts_models/en/vctk/vits").to(device)
    print("VITS listo")
except Exception as e:
    print(f"No se pudo cargar VITS: {e}")
    print("  Continuaremos solo con XTTS-v2")
    tts_vits = None

# Sistema de comparación de voces
print("\nCargando encoder de voces para métricas...")
try:
    voice_encoder = VoiceEncoder(device=device)
    print("Encoder listo (Resemblyzer)")
except Exception as e:
    print(f"Error cargando encoder: {e}")
    sys.exit(1)

# ============================================================================
# PASO 3: Generar audios con ZERO-SHOT CLONING
# ============================================================================
print("\n[3/4] Generando audios con clonación de voz...")  # Paso 3: generación de audios
print("Los audios generados clonarán la voz del audio de referencia")

# Textos en inglés (XTTS soporta multilingüe pero el audio ref es inglés)
texts = [
    "Hello, this is a demonstration of zero-shot voice cloning technology.",
    "Artificial intelligence can now replicate human voices with remarkable accuracy.",
    "This synthesized speech should sound similar to the reference audio provided.",
]

def calculate_similarity(ref_path, gen_path):
    """Calcula similitud entre dos audios usando embeddings de voz"""
    try:
        # Cargar y preprocesar audios
        ref_wav = preprocess_wav(ref_path)
        gen_wav = preprocess_wav(gen_path)
        
        # Obtener embeddings
        ref_emb = voice_encoder.embed_utterance(ref_wav)
        gen_emb = voice_encoder.embed_utterance(gen_wav)
        
        # Similitud de coseno (1 = idéntico, 0 = completamente diferente)
        similarity = 1 - cosine(ref_emb, gen_emb)
        return float(similarity)
    except Exception as e:
        print(f"  ⚠ Error calculando similitud: {e}")
        return 0.0

def evaluate_quality(audio_path):
    """Evalúa calidad del audio"""
    try:
        audio, sr = librosa.load(audio_path, sr=None)
        return {
            "duration": float(len(audio) / sr),
            "rms_energy": float(np.sqrt(np.mean(audio**2))),
            "zero_crossing_rate": float(np.mean(librosa.feature.zero_crossing_rate(audio))),
        }
    except Exception as e:
        print(f"Error evaluando calidad: {e}")
        return {"duration": 0, "rms_energy": 0, "zero_crossing_rate": 0}

results = {"reference_audio": reference_audio, "models": []}

# ------------------------------------------------------------------
# MODELO 1: XTTS-v2 (ZERO-SHOT CLONING)
# ------------------------------------------------------------------
print("\n" + "="*70)
print("MODELO 1: XTTS-v2 (ZERO-SHOT VOICE CLONING)")
print("="*70)
print("Clonando la voz del audio de referencia...")

xtts_results = {"model": "XTTS-v2", "description": "Zero-shot voice cloning", "tests": []}

for i, text in enumerate(texts):
    print(f"\n[{i+1}/3] Clonando voz para: '{text[:50]}...'")
    start = time.time()
    
    try:
        output_path = f"results/xtts_output_{i+1}.wav"
        
        # AQUÍ OCURRE LA MAGIA: XTTS clona la voz del reference_audio
        tts_xtts.tts_to_file(
            text=text,
            file_path=output_path,
            speaker_wav=reference_audio,  # ← Audio a clonar
            language="en"
        )
        
        gen_time = time.time() - start
        similarity = calculate_similarity(reference_audio, output_path)
        quality = evaluate_quality(output_path)
        
        xtts_results["tests"].append({
            "test_id": i+1,
            "text": text,
            "output_file": output_path,
            "generation_time": gen_time,
            "voice_similarity": similarity,
            "quality_metrics": quality
        })
        
    print(f"  Similitud con voz original: {similarity:.4f} | Tiempo: {gen_time:.2f}s")
        
    except Exception as e:
        print(f"  Error: {e}")

results["models"].append(xtts_results)

# ------------------------------------------------------------------
# MODELO 2: VITS (si está disponible)
# ------------------------------------------------------------------
if tts_vits is not None:
    print("\n" + "="*70)
    print("MODELO 2: VITS")
    print("="*70)
    
    vits_results = {"model": "VITS", "description": "Multi-speaker TTS", "tests": []}
    
    # VITS usa speaker IDs predefinidos, no clona exactamente
    # Lo incluimos para comparación
    speaker_id = "p225"  # Voz femenina
    
    for i, text in enumerate(texts):
    print(f"\n[{i+1}/3] Generando con VITS: '{text[:50]}...'")
        start = time.time()
        
        try:
            output_path = f"results/vits_output_{i+1}.wav"
            
            tts_vits.tts_to_file(
                text=text,
                file_path=output_path,
                speaker=speaker_id
            )
            
            gen_time = time.time() - start
            similarity = calculate_similarity(reference_audio, output_path)
            quality = evaluate_quality(output_path)
            
            vits_results["tests"].append({
                "test_id": i+1,
                "text": text,
                "output_file": output_path,
                "generation_time": gen_time,
                "voice_similarity": similarity,
                "quality_metrics": quality
            })
            
            print(f"  Similitud: {similarity:.4f} | Tiempo: {gen_time:.2f}s")
            
        except Exception as e:
            print(f"  Error: {e}")
    
    results["models"].append(vits_results)

# ============================================================================
# PASO 4: Generar comparación y resultados
# ============================================================================
print("\n[4/4] Generando análisis y comparación...")  # Paso 4: análisis y comparación

# Calcular estadísticas
for model_data in results["models"]:
    if len(model_data["tests"]) > 0:
        sims = [t["voice_similarity"] for t in model_data["tests"]]
        times = [t["generation_time"] for t in model_data["tests"]]
        model_data["statistics"] = {
            "avg_similarity": float(np.mean(sims)),
            "std_similarity": float(np.std(sims)),
            "min_similarity": float(np.min(sims)),
            "max_similarity": float(np.max(sims)),
            "avg_generation_time": float(np.mean(times)),
            "total_time": float(np.sum(times))
        }

# Guardar resultados completos
with open("results/comparison_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print("✓ Resultados guardados: results/comparison_results.json")

# Crear gráficos
if len(results["models"]) > 0:
    try:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        models = [m["model"] for m in results["models"]]
        similarities = [m["statistics"]["avg_similarity"] for m in results["models"]]
        times = [m["statistics"]["avg_generation_time"] for m in results["models"]]

        # Gráfico de similitud
        bars1 = ax1.bar(models, similarities, color=['#2ecc71', '#e74c3c'])
        ax1.set_ylabel('Similitud de Voz (Resemblyzer)', fontsize=11)
        ax1.set_title('Similitud con Voz Original', fontsize=12, fontweight='bold')
        ax1.set_ylim([0, 1])
        ax1.grid(axis='y', alpha=0.3)
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.3f}', ha='center', va='bottom', fontsize=10)

        # Gráfico de tiempo
        bars2 = ax2.bar(models, times, color=['#2ecc71', '#e74c3c'])
        ax2.set_ylabel('Tiempo (segundos)', fontsize=11)
        ax2.set_title('Tiempo de Generación', fontsize=12, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}s', ha='center', va='bottom', fontsize=10)

        plt.tight_layout()
        plt.savefig("results/comparison.png", dpi=300, bbox_inches='tight')
    print("Gráfico guardado: results/comparison.png")
    except Exception as e:
        print(f"No se pudo generar gráfico: {e}")

# Generar informe
report = []
report.append("="*70)
report.append("INFORME - ZERO-SHOT VOICE CLONING")
report.append("="*70)
report.append("")
report.append("AUDIO DE REFERENCIA:")
report.append(f"  Archivo: {reference_audio}")
report.append(f"  Dataset: LibriSpeech (dominio público)")
report.append("")
report.append("MODELOS EVALUADOS:")
for m in results["models"]:
    report.append(f"  {m['model']}: {m['description']}")
report.append("")
report.append("MÉTRICAS DE SIMILITUD (Resemblyzer):")
report.append("  Mide qué tan similar es la voz generada a la voz original")
report.append("  Rango: 0.0 (completamente diferente) - 1.0 (idéntico)")
report.append("")
report.append("RESULTADOS:")
report.append("-"*70)
report.append(f"{'Modelo':<20} {'Similitud':<15} {'Desv.Std':<15} {'Tiempo (s)':<15}")
report.append("-"*70)
for m in results["models"]:
    report.append(
        f"{m['model']:<20} "
        f"{m['statistics']['avg_similarity']:<15.4f} "
        f"{m['statistics']['std_similarity']:<15.4f} "
        f"{m['statistics']['avg_generation_time']:<15.2f}"
    )
report.append("-"*70)
report.append("")

# Análisis
if len(results["models"]) >= 1:
    report.append("ANÁLISIS:")
    report.append("")
    xtts = results["models"][0]
    report.append(f"XTTS-v2 (Zero-Shot Cloning):")
    report.append(f"  Similitud promedio: {xtts['statistics']['avg_similarity']:.4f}")
    if xtts['statistics']['avg_similarity'] > 0.7:
        report.append(f"  Alta similitud - La voz se clonó exitosamente")
    elif xtts['statistics']['avg_similarity'] > 0.5:
        report.append(f"  Similitud media - Capturó características generales")
    else:
        report.append(f"  Baja similitud - No logró clonar bien la voz")
    report.append(f"  Tiempo promedio: {xtts['statistics']['avg_generation_time']:.2f}s")
    if len(results["models"]) >= 2:
        report.append("")
        vits = results["models"][1]
        diff = (xtts['statistics']['avg_similarity'] - vits['statistics']['avg_similarity']) * 100
        report.append(f"Comparación XTTS vs VITS:")
        report.append(f"  XTTS tiene {abs(diff):.2f}% {'más' if diff > 0 else 'menos'} similitud")
        time_ratio = vits['statistics']['avg_generation_time'] / xtts['statistics']['avg_generation_time']
        if time_ratio > 1:
            report.append(f"  XTTS es {time_ratio:.2f}x más rápido")
        else:
            report.append(f"  VITS es {1/time_ratio:.2f}x más rápido")

report.append("")
report.append("CONCLUSIÓN:")
report.append("  XTTS-v2 realiza zero-shot voice cloning de la voz del audio de referencia sin entrenamiento previo.")
report.append("")
report.append("="*70)

report_text = "\n".join(report)
print("\n" + report_text)

with open("results/comparison_report.txt", "w", encoding="utf-8") as f:
    f.write(report_text)
print("\nInforme guardado: results/comparison_report.txt")

# Resumen final
print("\n" + "="*70)
print("PROCESO COMPLETADO EXITOSAMENTE")
print("="*70)
print("\nZERO-SHOT VOICE CLONING realizado con éxito")
print("\nResultados en 'results/':")
print("  Audios clonados:")
print("    - xtts_output_*.wav (voz clonada)")
if tts_vits:
    print("    - vits_output_*.wav")
print("  Métricas:")
print("    - comparison_results.json")
print("  Visualizaciones:")
print("    - comparison.png")
print("  Informe:")
print("    - comparison_report.txt")
print("\nLos audios generados tienen la voz del audio de referencia")
print()
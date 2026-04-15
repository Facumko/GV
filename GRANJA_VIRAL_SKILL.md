# SKILL: Granja Viral — Sistema Automatizado de Contenido Viral

## ROL DE CLAUDE
Sos el arquitecto técnico y guía del proyecto "Granja Viral". Conocés el sistema completo. Tu trabajo es retomar el proyecto desde donde quedó, proponer el siguiente paso concreto y ejecutarlo junto al usuario. No explicás lo que ya está documentado — actuás.

---

## CONTEXTO DEL PROYECTO

Sistema de generación masiva de contenido viral para TikTok y YouTube Shorts.
- **Costo operativo:** $0 en fase inicial (stack 100% local/gratuito)
- **Idiomas:** DOS pipelines separados — Español Latino + Inglés
- **Estrategia:** Nichos dinámicos (el sistema detecta nichos en auge, no nicho fijo)
- **Usuario:** Programador avanzado, aprende tecnologías rápido, 16GB RAM, empieza desde cero en plataformas

## CICLO FUNDAMENTAL
```
DETECTAR nicho en auge → OBSERVAR tendencias → GENERAR contenido → PUBLICAR → APRENDER → repetir
```

---

## ARQUITECTURA — 4 CAPAS

| Capa | Función | Stack | Estado inicial |
|------|---------|-------|----------------|
| 1 | Inteligencia Viral (detecta nichos + patrones) | Python + YouTube Data API + SQLite | Por construir |
| 2 | Generación de Contenido (guiones + audio) | Python + Ollama/Llama3 + Edge-TTS + Whisper | Por construir |
| 3 | Producción de Video (render 9:16) | Node.js + Remotion + FFmpeg | Por construir |
| 4 | Publicación + Aprendizaje (feedback loop) | Python + SQLite + publicación manual | Por construir |

---

## MEJORAS RESPECTO AL PLAN ORIGINAL

### 1. Detección dinámica de nichos (NUEVO)
La Capa 1 no trabaja sobre un nicho fijo. Agrega un módulo `niche_detector.py` que:
- Monitorea Google Trends API (pytrends, gratuito)
- Cruza con YouTube trending por categoría
- Rankea nichos por velocidad de crecimiento (views últimas 48h vs 7 días)
- Propone automáticamente el nicho más prometedor cada semana
- Permite al usuario aprobar o rechazar el nicho sugerido

### 2. Dos pipelines separados (NUEVO)
```
granja-viral/
├── pipeline_es/   # Español Latino
│   ├── capa1/ capa2/ capa3/ capa4/
│   └── data/viral_es.db
└── pipeline_en/   # Inglés
    ├── capa1/ capa2/ capa3/ capa4/
    └── data/viral_en.db
```
Comparten: assets/, config/, el módulo niche_detector.py

### 3. Modelos de IA recomendados (NUEVO)
- **Guiones en Español:** Ollama + `llama3:8b` (local, gratis, aceptable para ES)
- **Guiones en Inglés:** Ollama + `llama3:8b` o Claude API (mejor calidad EN, con créditos gratuitos iniciales)
- **TTS Español:** Edge-TTS voz `es-AR-TomasNeural` o `es-MX-JorgeNeural`
- **TTS Inglés:** Edge-TTS voz `en-US-GuyNeural` o `en-US-JennyNeural`

### 4. Score de viralidad cruzado (NUEVO)
La tabla `performance` en SQLite incluye campo `pipeline` (es/en) para comparar qué nichos y estructuras funcionan mejor en cada idioma y cruzar aprendizajes.

---

## STACK COMPLETO

```
Python 3.10+         → Backend principal (capas 1, 2, 4)
Node.js 18+          → Render de video (capa 3)
Ollama + Llama 3 8B  → Generación de guiones (local, gratis)
Edge-TTS             → Text-to-Speech (Microsoft, gratis, ilimitado)
Whisper small        → Timestamps y transcripción (local)
Remotion 4+          → Framework de video React
FFmpeg               → Composición y render final
SQLite               → Base de datos local
YouTube Data API v3  → Análisis de tendencias (10k req/día gratis)
pytrends             → Google Trends (detección de nichos, gratis)
pandas               → Procesamiento de datos
python-dotenv        → Variables de entorno
```

---

## PLAN DE EJECUCIÓN

### SEMANA 1 — Infraestructura + Capa 1
- [ ] Instalar Python, Node.js, Ollama, FFmpeg, Git
- [ ] Obtener YouTube Data API key (Google Cloud Console, gratis)
- [ ] Crear estructura de carpetas dual (pipeline_es / pipeline_en)
- [ ] Construir `niche_detector.py` (pytrends + YouTube trending)
- [ ] Construir Capa 1: scraper + analyzer + SQLite
- **Meta:** sistema detecta y sugiere nicho en auge automáticamente

### SEMANA 2 — Capa 2 + Capa 3
- [ ] Instalar Ollama, bajar modelo llama3:8b
- [ ] Construir generador de guiones (estructura: Hook 3s / Conflicto / Resolución)
- [ ] Integrar Edge-TTS + Whisper para audio y timestamps
- [ ] Instalar Remotion, construir componentes JSX
- [ ] Probar render de 3 videos completos en cada pipeline
- **Meta:** primer video 9:16 con subtítulos dinámicos renderizado

### SEMANA 3 — Publicación + Datos reales
- [ ] Crear canales TikTok y YouTube (uno por idioma o compartido)
- [ ] Publicar 10 videos manualmente
- [ ] Registrar performance en SQLite
- [ ] Anotar views 24h / 48h
- **Meta:** primeros datos reales del sistema

### SEMANA 4 — Cierre del loop
- [ ] Ejecutar analytics.py para identificar patrones ganadores
- [ ] Ajustar prompts de Ollama según resultados
- [ ] Refinar niche_detector con pesos basados en data propia
- [ ] Publicar 15-20 videos con patrones ajustados
- **Meta:** sistema aprendiendo de sí mismo, ciclo cerrado

---

## ERRORES A EVITAR
- NO automatizar publicación (TikTok detecta bots → ban)
- NO usar Pexels como fondos (genérico, saturado — usar gameplay propio)
- NO optimizar antes de tener datos reales
- NO agregar features antes de tener el ciclo funcionando
- NO depender de scraping directo de TikTok (usa YouTube Data API oficial)
- NO esperar el video perfecto — volumen + iteración gana

---

## CÓMO RETOMAR EL PROYECTO

Cuando el usuario te pase este skill + el PDF, seguí estos pasos:

1. **Preguntá en qué semana/paso está** (o inferilo del contexto)
2. **Identificá el próximo bloqueo concreto** (instalación, código, error, decisión)
3. **Proponé UNA sola acción** para avanzar en esa sesión
4. **Ejecutala junto al usuario** paso a paso
5. Al final de la sesión, **resumí el estado actual** en 3 líneas para que el usuario lo guarde

---

## ESTADO DEL PROYECTO (actualizar cada sesión)
```
Última sesión: [FECHA]
Completado: [qué capas/módulos están funcionando]
Próximo paso: [acción concreta pendiente]
Bloqueos conocidos: [si hay alguno]
```

import asyncio
import edge_tts
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

async def generar_audio(texto, nombre='audio_001', voz='en-US-GuyNeural'):  # FIX: era es-AR-TomasNeural
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, f'{nombre}.mp3')
    communicate = edge_tts.Communicate(texto, voz)
    await communicate.save(output_path)
    print(f"✅ Audio guardado: {output_path}")

if __name__ == '__main__':
    texto = """You've been doing your morning wrong your whole life.
    Most people start with coffee — and that's exactly the problem.
    Try this instead for 7 days. The results will shock you."""

    asyncio.run(generar_audio(texto))
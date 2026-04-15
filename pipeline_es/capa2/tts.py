import asyncio
import edge_tts
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

async def generar_audio(texto, nombre='audio_001', voz='es-AR-TomasNeural'):
    output_path = os.path.join(OUTPUT_DIR, f'{nombre}.mp3')
    communicate = edge_tts.Communicate(texto, voz)
    await communicate.save(output_path)
    print(f"✅ Audio guardado: {output_path}")

if __name__ == '__main__':
    texto = """La mañana es el reto de todos. 
    Pero como le pasa a esta persona, cuando el ritmo se rompe todo se complica. 
    Entonces decidió tomar un enfoque más extraño. ¡Y funcionó!"""
    
    asyncio.run(generar_audio(texto))
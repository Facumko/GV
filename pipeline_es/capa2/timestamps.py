import whisper
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

def generar_timestamps(audio_file='audio_001.mp3'):
    audio_path = os.path.join(DATA_DIR, audio_file)
    print("⏳ Transcribiendo...")
    
    model = whisper.load_model('small')
    result = model.transcribe(audio_path, word_timestamps=True, language='es')
    
    palabras = []
    for seg in result['segments']:
        for word in seg.get('words', []):
            palabras.append({
                'word': word['word'].strip(),
                'start': round(word['start'], 2),
                'end': round(word['end'], 2)
            })
    
    output_path = os.path.join(DATA_DIR, 'timestamps_001.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(palabras, f, ensure_ascii=False, indent=2)
    
    print(f"✅ {len(palabras)} palabras guardadas en timestamps_001.json")
    print("\nPrimeras 5 palabras:")
    for p in palabras[:5]:
        print(f"  {p['word']} → {p['start']}s - {p['end']}s")

if __name__ == '__main__':
    generar_timestamps()
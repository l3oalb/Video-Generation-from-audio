import whisper

# On charge le modèle une seule fois au début pour gagner du temps
model = whisper.load_model("base")

def get_transcription_segments(audio_path, target_duration=5.375):
    """
    Transforme un audio en une liste de segments de texte sans créer de fichiers .txt
    """
    print(f"⏳ Analyse de l'audio...")
    result = model.transcribe(audio_path, verbose=False)
    
    segments_list = []
    current_part_text = ""
    current_part_start = 0

    for segment in result["segments"]:
        current_part_text += segment["text"] + " "
        
        # Vérification du timing
        if segment["end"] - current_part_start >= target_duration:
            segments_list.append(current_part_text.strip())
            
            # Réinitialisation
            current_part_text = ""
            current_part_start = segment["end"]

    # On ajoute le reliquat s'il existe
    if current_part_text.strip():
        segments_list.append(current_part_text.strip())

    return segments_list
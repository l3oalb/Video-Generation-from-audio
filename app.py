import streamlit as st
import os
import whisper
import tempfile
import time
import requests
import fal_client
from openai import OpenAI
from moviepy import VideoFileClip, concatenate_videoclips, AudioFileClip
from dotenv import load_dotenv

# --- CONFIGURATION INITIALE ---
load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_KEY"))

# On fixe la durée cible pour coller aux 129 frames à 24 fps de Fal.ai
TARGET_DURATION = 5.375 
STORY_SEED = 42

st.set_page_config(page_title="AI Movie Meme Generator", page_icon="🎬")
st.title("🎬 AI Video Meme Generator")
st.info("Transformez vos audios en histoires animées cohérentes.")

# --- CHARGEMENT DU MODÈLE WHISPER (Cache pour éviter de recharger) ---
@st.cache_resource
def load_whisper():
    return whisper.load_model("base")

model_whisper = load_whisper()

# --- FONCTIONS DE TRANSCRIPTION ---
def get_segments(audio_path):
    result = model_whisper.transcribe(audio_path)
    segments_list = []
    current_text = ""
    current_start = 0

    for segment in result["segments"]:
        current_text += segment["text"] + " "
        if segment["end"] - current_start >= TARGET_DURATION:
            segments_list.append(current_text.strip())
            current_text = ""
            current_start = segment["end"]
    if current_text.strip():
        segments_list.append(current_text.strip())
    return segments_list

# --- FONCTIONS GPT (PROMPTS) ---
def generate_bible_and_prompts(segments):
    full_text = " ".join(segments)
    
    # 1. Bible Visuelle
    bible_resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a Concept Artist. Define a consistent visual style and characters for this story in 3 sentences (English)."},
            {"role": "user", "content": full_text}
        ]
    )
    bible = bible_resp.choices[0].message.content.strip()

    # 2. Prompts des scènes
    prompts = []
    for seg in segments:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"VISUAL BIBLE: {bible}\nCreate a single fluid video prompt in English for this scene. Include '720p', 'high detail', 'smooth motion'."},
                {"role": "user", "content": seg}
            ]
        )
        prompts.append(resp.choices[0].message.content.strip())
    
    return bible, prompts

# --- FONCTIONS VIDÉO (FAL.AI) ---
def generate_all_clips(prompts, temp_dir):
    video_paths = []
    for i, p in enumerate(prompts):
        st.write(f"⏳ Génération du segment {i+1}/{len(prompts)}...")
        handler = fal_client.submit(
            "fal-ai/hunyuan-video",
            arguments={
                "prompt": p,
                "video_size": "720p_portrait",
                "num_frames": 129,
                "fps": 24,
                "seed": STORY_SEED,
                "guidance_scale": 7.0
            }
        )
        result = fal_client.result("fal-ai/hunyuan-video", handler.request_id)
        
        # Téléchargement
        path = os.path.join(temp_dir, f"part_{i}.mp4")
        with open(path, "wb") as f:
            f.write(requests.get(result['video']['url']).content)
        video_paths.append(path)
    return video_paths

# --- INTERFACE UTILISATEUR (STREAMLIT) ---
uploaded_audio = st.file_uploader("Étape 1 : Importez votre audio (mp3, wav)", type=["mp3", "wav"])

if uploaded_audio:
    # Sauvegarde temporaire de l'audio pour Whisper et MoviePy
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
        tmp_audio.write(uploaded_audio.read())
        st.session_state.audio_path = tmp_audio.name

    # BOUTON 1 : TRANSCRIPTION
    if st.button("Étape 2 : Analyser l'histoire"):
        with st.spinner("Transcription et découpage..."):
            st.session_state.segments = get_segments(st.session_state.audio_path)
            st.success(f"Histoire découpée en {len(st.session_state.segments)} scènes.")
            for s in st.session_state.segments:
                st.write(f"- {s}")

    # BOUTON 2 : PROMPTS
    if "segments" in st.session_state and st.button("Étape 3 : Créer le scénario visuel"):
        with st.spinner("GPT-4o-mini travaille sur la cohérence..."):
            bible, prompts = generate_bible_and_prompts(st.session_state.segments)
            st.session_state.bible = bible
            st.session_state.prompts = prompts
            st.write(f"🎨 **Style défini :** {bible}")
            st.success("Prompts générés avec succès.")

    # BOUTON 3 : VIDÉO FINALE
    if "prompts" in st.session_state and st.button("🚀 Étape 4 : Générer le film (Fal.ai)"):
        with tempfile.TemporaryDirectory() as tmp_video_dir:
            with st.status("Production de la vidéo en cours...", expanded=True) as status:
                # Génération
                clips = generate_all_clips(st.session_state.prompts, tmp_video_dir)
                
                # Assemblage
                status.update(label="Montage final et synchronisation audio...")
                video_clips = [VideoFileClip(c) for c in clips]
                final_v = concatenate_videoclips(video_clips, method="compose")
                
                # Ajout de l'audio
                audio_bg = AudioFileClip(st.session_state.audio_path)
                final_v = final_v.set_audio(audio_bg.subclip(0, final_v.duration))
                
                output_path = "final_meme_video.mp4"
                final_v.write_videofile(output_path, codec="libx264", audio_codec="aac")
                
                status.update(label="Film terminé !", state="complete")
            
            # Affichage final
            st.video(output_path)
            with open(output_path, "rb") as f:
                st.download_button("💾 Télécharger ma vidéo", f, "mon_film_ia.mp4")
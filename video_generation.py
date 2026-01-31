import os
import requests
import fal_client
import tempfile
from moviepy import VideoFileClip, concatenate_videoclips, AudioFileClip

# Configuration de cohérence
STORY_SEED = 42 

def download_video(url, save_path):
    """Télécharge le fichier depuis l'URL fournie par Fal.ai."""
    response = requests.get(url)
    with open(save_path, "wb") as f:
        f.write(response.content)

def generate_video_segments(prompts_list, temp_dir):
    """
    Prend la liste de prompts et génère chaque clip MP4 
    dans un dossier temporaire.
    """
    video_paths = []
    
    for i, prompt_text in enumerate(prompts_list):
        print(f"Demande Fal.ai pour le segment {i+1}...")
        
        handler = fal_client.submit(
            "fal-ai/hunyuan-video",
            arguments={
                "prompt": prompt_text,
                "video_size": "720p_portrait",
                "num_frames": 129,
                "fps": 24,
                "seed": STORY_SEED,
                "guidance_scale": 7.0,
                "negative_prompt": "blurry, distorted, low quality, 3D render, realistic, text, watermark"
            }
        )
        
        result = fal_client.result("fal-ai/hunyuan-video", handler.request_id)
        url = result['video']['url']
        
        # Sauvegarde locale dans le dossier temporaire
        clip_path = os.path.join(temp_dir, f"segment_{i:02d}.mp4")
        download_video(url, clip_path)
        video_paths.append(clip_path)
        
    return video_paths

def assemble_final_video(video_paths, audio_source_path, output_filename):
    """
    Assemble les clips et synchronise l'audio original.
    """
    print("Assemblage et synchronisation audio...")
    
    # 1. Charger les clips
    clips = [VideoFileClip(p) for p in video_paths]
    final_video = concatenate_videoclips(clips, method="compose")
    
    # 2. Ajouter l'audio original
    original_audio = AudioFileClip(audio_source_path)
    
    # On s'assure que l'audio ne dépasse pas la vidéo
    final_audio = original_audio.subclip(0, final_video.duration)
    final_video = final_video.set_audio(final_audio)
    
    # 3. Export
    final_video.write_videofile(output_filename, codec="libx264", audio_codec="aac")
    
    # Nettoyage des clips pour libérer de la mémoire
    for c in clips: c.close()
    original_audio.close()
    
    return output_filename
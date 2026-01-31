from openai import OpenAI
import os

# Configuration client (sera récupérée via les Secrets sur Hugging Face)
client = OpenAI(api_key=os.environ.get("OPENAI_KEY"))

def generate_visual_bible(segments_list):
    """Génère la Bible Visuelle à partir de la liste des segments de texte."""
    full_story_text = " ".join(segments_list)
    
    print("🎨 Création de la Bible Visuelle pour cette histoire...")
    system_instruction = (
        "You are a Concept Artist. Read this story and define a consistent visual style "
        "and character descriptions. Describe the main characters' physical traits, "
        "clothing, and the overall animation style. Keep it to 3-4 sentences in English."
    )
    
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": f"Story summary: {full_story_text[:4000]}"}
            ]
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Erreur Bible : {e}")
        return "High-quality 2D digital animation, vibrant colors."

def create_video_prompt(segment_text, visual_bible):
    """Génère un prompt unique pour un segment donné."""
    system_prompt = (
        f"You are a Video Prompt Engineer. \n"
        f"VISUAL BIBLE TO FOLLOW: {visual_bible}\n\n"
        "Your task: Transform the user text into a SINGLE FLUID PARAGRAPH in English. "
        "Maintain characters and style. Include: '720p', 'high resolution', 'smooth motion'."
    )

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": segment_text}
            ],
            max_completion_tokens=1000,
            temperature=0.7
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Erreur Prompt Segment : {e}")
        return None

def process_all_prompts(segments_list):
    """
    La fonction 'chef d'orchestre' : prend une liste de textes, 
    crée la bible, et renvoie une liste de prompts.
    """
    # 1. Générer la bible une seule fois pour tous les segments
    visual_bible = generate_visual_bible(segments_list)
    
    # 2. Générer la liste des prompts
    prompts_list = []
    for i, text in enumerate(segments_list):
        print(f"⏳ Génération du prompt {i+1}/{len(segments_list)}...")
        prompt = create_video_prompt(text, visual_bible)
        if prompt:
            prompts_list.append(prompt)
            
    return prompts_list, visual_bible
---
title: Video Generation From Audio UTT
emoji: 🏃
colorFrom: indigo
colorTo: red
sdk: streamlit
app_file: app.py
pinned: false
license: mit
short_description: L’objectif est de concevoir une application capable de trans
---

# Gen-AI-project-UTT
L’objectif est de concevoir une application capable de transformer un audio en une vidéo, en automatisant les étapes suivantes :
Transcription de l’audio .mp3 → texte
Analyse du texte → génération d’images
Composition d’une vidéo finale (texte animé, images, sous-titres)
Exposition du service via une API déployée dans un environnement MLOps
Le projet démontre :
la maîtrise des modèles génératifs multimodaux (audio → texte, texte → vidéo/image),
la mise en place d’un pipeline ML reproductible, monitoré et versionné,
l’intégration des bonnes pratiques MLOps (MLflow, DVC, CI/CD, conteneurisation…).

# Ingenierie des Prompts

La principale problématique à laquelle font face les modèles de génération vidéo est la dérive contextuelle (ou l'oubli du contexte) à mesure que la durée de la vidéo augmente. Pour pallier cette limite technique, nous avons structuré notre pipeline autour de séquences très courtes, de 5 à 6 secondes chacune (soit 129 frames à 24 fps).

### Stratégie de cohérence
* **Segmentation temporelle :** Le script de l'audio est découpé en parties égales. Pour chaque segment, un prompt descriptif spécifique est généré par le modèle GPT-4o-mini.
* **Ancre de style :** La première phrase de chaque prompt est identique pour toutes les séquences d'un même projet. Elle définit le contexte global (style visuel, personnages, ambiance) afin d'éviter que le modèle n'oscille entre différents rendus, comme le passage d'un style réaliste à une animation 2D.
* **Fixation de la Seed :** Nous utilisons une seed (graine aléatoire) commune pour l'ensemble des segments d'une même histoire. Cela permet de stabiliser les caractéristiques physiques des personnages et les éléments du décor d'un plan à l'autre.

---

# Generation des Videos

La génération a été réalisée via l'API fal.ai en utilisant le modèle HunyuanVideo. Ce choix s'appuie sur les performances de pointe de ce modèle dans le domaine de la génération vidéo open-source, celui-ci étant classé premier sur la plateforme Hugging Face lors de la réalisation du projet.

## Defis et limites rencontres

* **Temps de calcul :** Pour un segment de 5 à 6 secondes, le temps de génération varie entre 5 et 6 minutes. Cette latence est due au haut niveau de détails et à la résolution de sortie (720p). 
    * *Optimisation possible :* Une parallélisation des requêtes permettrait de générer tous les segments simultanément plutôt qu'en série, réduisant drastiquement le temps total de production.
* **Instabilite visuelle :** Malgré l'optimisation des prompts et l'usage d'une seed fixe, des micro-variations subsistent. Par exemple, le personnage du fermier conserve ses attributs principaux (chapeau, moustache), mais la densité ou la forme de sa moustache peut varier sensiblement d'une partie à l'autre.

## Pistes d'amelioration

L'évolution logique du projet serait d'intégrer une dimension Image-to-Video (I2V). Au lieu de s'appuyer uniquement sur du texte (Text-to-Video), le modèle utiliserait une image de référence contenant tous les éléments clés de l'histoire comme base structurelle fixe. 

Passer d'une approche purement textuelle à une approche multimodale (Image + Texte) permettrait de verrouiller l'apparence des personnages de manière définitive. Le modèle utilisé pour ce prototype ne supportant pas nativement cette fonctionnalité, elle constitue un axe de développement prioritaire pour les versions futures.

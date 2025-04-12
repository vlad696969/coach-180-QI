import os
import streamlit as st
from langchain_openai import ChatOpenAI
import openai
import json
from supabase import create_client, Client
from dotenv import load_dotenv
import hashlib
from datetime import date

# 🌌 Style cinématographique global
st.markdown("""
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            color: #000000;
            font-family: 'Montserrat', sans-serif;
        }
        h1, h2, h3, h4, h5, h6 {
            font-weight: 800;
        }
        .stTextInput > div > div > input,
        .stSelectbox > div > div > div > div,
        .stTextArea > div > textarea {
            background-color: #f5f5f5;
            color: #000000;
        }
        .stSlider > div {
            color: #CD0D0D;
        }
        .stButton > button {
            background-color: #CD0D0D;
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: bold;
        }
        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-thumb {
            background: #CD0D0D;
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🧠 Coach Pédagogique AI")
st.markdown("<h4 style='color:#CD0D0D;'>Un mentor. Un objectif. 60 jours pour tout maîtriser.</h4>", unsafe_allow_html=True)

# 🎮 Vidéo explicative de l’application dans un menu dépliant
with st.expander("🎩 Comment utiliser cette application ?"):
    st.video("https://youtu.be/w5cDkYeAilw")
    st.markdown("<br><a href='https://platform.openai.com/signup' target='_blank'>🔑 Créer un compte et une clé API OpenAI ici</a>", unsafe_allow_html=True)

with st.expander(" Comprendre les modèles et la température"):
    st.markdown("""
    ### Modèles GPT
    - **GPT-3.5 Turbo** : rapide et économique.
    - **GPT-4** : plus lent mais plus performant.

    ### 💰 Tarification indicative
    <div style='margin-left: 1rem;'>
        <ul>
            <li><strong>GPT-3.5 Turbo</strong> : <code>~0.50 $</code> / <em>1M tokens (input)</em>, <code>~1.50 $</code> / <em>1M tokens (output)</em></li>
            <li><strong>GPT-4</strong> : <code>~10 $</code> / <em>1M tokens (input)</em>, <code>~30 $</code> / <em>1M tokens (output)</em></li>
        </ul>
    </div>

    ### Température ("Creativity")
    - <strong>0.0 à 0.3</strong> → Réponses très fiables, peu créatives (logique, math, code)
    - <strong>0.4 à 0.7</strong> → Bon équilibre logique / créativité
    - <strong>0.8 à 1.0</strong> → Réponses plus libres, narratives, parfois moins précises
    """, unsafe_allow_html=True)

# Chargement des variables d'environnement
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_user_hash(api_key):
    return hashlib.sha256(api_key.encode()).hexdigest()

PROMPT_MAITRE = '''
## 🧠 **PROMPT OPTIMISÉ : Programme de 60 jours pour maîtriser n’importe quel domaine**

**Ton rôle :**  
Tu es un mentor personnel et un coach d’apprentissage avec un QI de 180, expert absolu dans la pédagogie efficace.  
Tu m'accompagnes pendant **60 jours** afin que je devienne compétent(e) dans le domaine précis suivant : **[sujet précis à compléter]**.

Tu dois systématiquement viser l’efficacité maximale :

- Va à l’essentiel et ignore tout ce qui est superficiel.
- Priorise uniquement les méthodes et ressources ayant le meilleur ratio temps/résultat.
- Décompose les concepts complexes en étapes claires et accessibles.
- Identifie et corrige rapidement mes blocages et mes angles morts.
- Stimule ma réflexion autonome plutôt que de simplement fournir des réponses toutes faites.
- N'accepte aucune excuse ou procrastination.

---

### Programme initial à établir ensemble (1 fois au début des 60 jours) :

**Étape 1 : Diagnostic et objectif**

- Évalue mes connaissances actuelles par des questions précises et rapides.
- Définit avec moi un objectif final précis, ambitieux mais réaliste, atteignable en 60 jours.
- Définit avec moi combien de temps je suis prêt à consacrer à cet apprentissage tout les jours

**Étape 2 : Création du programme**

- Découpe clairement l’objectif en sous-compétences clés à maîtriser.
- Établis une feuille de route précise et concrète (compétences à acquérir par semaine).
- Recommande-moi UNE ressource principale seulement (livre OU formation vidéo OU autre) qui couvre efficacement l'ensemble du sujet.
- Encourage moi à discuter ce programme pour l’adapter à mes besoins spécifiques.
---

### Accompagnement régulier (toutes les semaines) :

Chaque semaine, tu devras :

- M'indiquer clairement les compétences clés à maîtriser durant cette semaine.
- Me fournir des exercices pratiques à difficulté progressive (avec feedback immédiat).
- Me soumettre à des petits défis pratiques ou études de cas réalistes qui stimulent l'intégration de mes connaissances dans la vie réelle.

---

### Interaction quotidienne (chaque séance d'étude) :

À chaque interaction :

- M'encourager à poser des questions et à interagir avec toi
- Pose-moi des questions ciblées pour mesurer précisément ma compréhension.
- Ajuste immédiatement le programme ou les exercices en fonction de mes réponses.
- Aide-moi à résoudre concrètement mes difficultés spécifiques avec des analogies simples et puissantes.
'''

st.markdown("Entrez votre clé OpenAI pour commencer :")
api_key = st.text_input("Clé API OpenAI", type="password")

model_choice = st.selectbox("Choisissez le modèle :", ["gpt-3.5-turbo", "gpt-4"])

temp = st.slider("🎯 Niveau de créativité (température)", 0.0, 1.0, 0.5, 0.1)

@st.cache_data(show_spinner=False)
def test_api_key(key, model):
    try:
        client = openai.OpenAI(api_key=key)
        client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Dis juste OK"}]
        )
        return True, "Clé fonctionnelle."
    except Exception as e:
        return False, str(e)

if api_key:
    valid, info = test_api_key(api_key, model_choice)
    if valid:
        st.success(f"✅ Clé API valide")
        chat = ChatOpenAI(api_key=api_key, temperature=temp, model=model_choice)
        user_hash = get_user_hash(api_key)

        if "chat_history" not in st.session_state:
            response = supabase.table("user_history").select("messages").eq("id", user_hash).execute()
            st.session_state.chat_history = response.data[0]["messages"] if response.data else [{"role": "system", "content": PROMPT_MAITRE}]

        messages = st.session_state.chat_history

        total_days = 60

        # 📊 Nouvelle logique de progression : jours uniques
        today = date.today().isoformat()
        progress = supabase.table("progress_logs")\
            .select("date")\
            .eq("user_hash", user_hash)\
            .execute()
        unique_days = set(entry["date"] for entry in progress.data)
        already_logged_today = today in unique_days

        if not already_logged_today:
            unique_days.add(today)

        completed_days = len(unique_days)

        st.progress(completed_days / total_days, text=f"🗓 {completed_days} jours complétés sur {total_days}")

        # 📓 Journal des 3 derniers jours
        with st.expander("📓 Journal des 3 derniers jours"):
            progress = supabase.table("progress_logs")\
                .select("*")\
                .eq("user_hash", user_hash)\
                .order("day_number", desc=True)\
                .limit(3)\
                .execute()

            logs = progress.data

            if not logs:
                st.info("Aucune interaction enregistrée pour le moment.")
            else:
                for entry in reversed(logs):
                    st.markdown(f"""
                    <div style='background-color:#f8f8f8; padding:1rem; margin-bottom:1rem; border-left: 5px solid #CD0D0D; border-radius:8px;'>
                        <h5 style='color:#CD0D0D;'>🗓 Jour {entry['day_number']} — {entry['date']}</h5>
                        <p><strong>👤 Toi :</strong><br>{entry['question']}</p>
                        <p><strong>🧐 Coach :</strong><br>{entry['response']}</p>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("## 💬 Discute avec ton coach")
        user_input = st.chat_input("Pose ta question... (Maj+Entrée pour une nouvelle ligne)")

        if user_input:
            messages.append({"role": "user", "content": user_input})
            with st.spinner("🤔 Le coach réfléchit..."):
                response = chat.invoke(messages)
                assistant_reply = response.content
            messages.append({"role": "assistant", "content": assistant_reply})
            supabase.table("user_history").upsert({"id": user_hash, "messages": messages}).execute()
            st.session_state.chat_history = messages

            if not already_logged_today:
                supabase.table("progress_logs").insert({
                "user_hash": user_hash,
                "day_number": completed_days,
                "date": today,
                "question": user_input,
                "response": assistant_reply
            }).execute()

            st.markdown(f"""
            <div style='background-color:#f5f5f5; padding:1rem; border-left: 5px solid #CD0D0D; border-radius:8px;'>
                <strong style='color:#000000;'>👤 Toi :</strong><br>{user_input}
            </div>
            <div style='background-color:#eaeaea; padding:1rem; border-left: 5px solid #CD0D0D; margin-top:0.5rem; border-radius:8px;'>
                <strong style='color:#CD0D0D;'>🧐 Coach :</strong><br>{assistant_reply}
            </div>
            """, unsafe_allow_html=True)

    else:
        st.error(f"❌ Clé API invalide : {info}")

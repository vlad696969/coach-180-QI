import os
import streamlit as st
from langchain_openai import ChatOpenAI
import openai
import json
from supabase import create_client, Client
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Prompt maître
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

# UI
st.title("🎓 Coach Pédagogique AI")
st.markdown("Entrez votre clé OpenAI pour commencer :")
api_key = st.text_input("Clé API OpenAI", type="password")

model_choice = st.selectbox("Choisissez le modèle :", ["gpt-3.5-turbo", "gpt-4"])

with st.expander("ℹ️ Informations sur les modèles et la température"):
    st.markdown("""
    ### 🔥 Température du modèle

    La température contrôle le **niveau de créativité** de l'IA :

    - **0.0 → 0.3** : Réponses très factuelles, rigoureuses, fiables.
    - **0.4 → 0.6** : Bon équilibre entre précision et créativité (par défaut).
    - **0.7 → 1.0** : Réponses plus variées, créatives, parfois moins exactes.

    🔽️ Pour des explications claires et structurées, reste proche de 0.3-0.5.  
    🔽️ Pour stimuler des idées originales ou des exercices variés, monte vers 0.7+.

    ---

    ### 🤔 GPT-3.5 vs GPT-4 : quelles différences ?

    | Modèle        | Qualité des réponses | Vitesse  | Prix approximatif |
    |---------------|---------------------|----------|--------------------|
    | GPT-3.5 Turbo | Rapide, bon niveau  | Rapide   | ≈ 0,50€ / 1M tokens |
    | GPT-4         | Plus pertinent, plus nuancé | Plus lent | ≈ 30€ / 1M tokens |

    **💬 Un token correspond à ≈ 1 mot.**  
    > Par exemple : une question + réponse de 500 mots ≈ 1 000 tokens.

    **🌐 Pour suivre ta consommation exacte :**  
    [Consulte ton usage sur la plateforme OpenAI](https://platform.openai.com/account/usage)
    """)

temp = st.slider("Niveau de créativité (température)", 0.0, 1.0, 0.5, 0.1)

# Validation de la clé API
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
        st.success(f"✅ Clé API valide : {info}")

        chat = ChatOpenAI(api_key=api_key, temperature=temp, model=model_choice)

        # Chargement depuis Supabase
        user_hash = str(hash(api_key))
        response = supabase.table("user_history").select("messages").eq("id", user_hash).execute()
        messages = response.data[0]["messages"] if response.data else [{"role": "system", "content": PROMPT_MAITRE}]

        st.markdown("## 💬 Discussion avec ton coach pédagogique")
        user_input = st.chat_input("Pose ta question... (Maj+Entrée pour une nouvelle ligne)")

        if user_input:
            messages.append({"role": "user", "content": user_input})
            with st.spinner("L'IA réfléchit..."):
                response = chat.invoke(messages)
                messages.append({"role": "assistant", "content": response.content})
                supabase.table("user_history").upsert({"id": user_hash, "messages": messages}).execute()

        for msg in messages[1:]:
            if msg["role"] == "user":
                st.markdown(f"**👤 Toi :** {msg['content']}")
            else:
                st.markdown(f"**🫠 Coach :** {msg['content']}")

    else:
        st.error(f"❌ Clé API invalide : {info}")
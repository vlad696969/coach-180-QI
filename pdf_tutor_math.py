import os
import streamlit as st
from apikey import API
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain_openai import OpenAI

os.environ["OPENAI_API_KEY"] = API

## Prompt maitre 




st.title("🚀 Mon assistant IA (rapide) avec LaTeX")

question = st.text_input("Pose ta question :")

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)

if question:
    docs_similaires = db.similarity_search(question)
    llm = OpenAI(temperature=0.2)

    # Nouveau prompt explicite
    prompt_template = (
        "Réponds à la question suivante de façon détaillée et pédagogique en utilisant "
        "impérativement le format Markdown. Encadre systématiquement toutes les équations mathématiques "
        "avec du LaTeX : utilise `$...$` pour les équations inline ou `$$...$$` pour les blocs.\n\n"
        f"Question : {question}\n"
        "Réponse :"
    )

    chain = load_qa_chain(llm, chain_type="stuff")
    reponse = chain.run(input_documents=docs_similaires, question=prompt_template)

    st.markdown("🧠 **Réponse IA :**")
    st.markdown(reponse)

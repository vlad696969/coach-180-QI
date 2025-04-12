import os
from apikey import API
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

os.environ["OPENAI_API_KEY"] = API

# Charger TOUS les PDFs d'un coup
loader = DirectoryLoader("docs/", glob="**/*.pdf", loader_cls=PyPDFLoader)
documents = loader.load()

# Découpage
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
docs = text_splitter.split_documents(documents)

# Embedding et sauvegarde (une fois pour toutes)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
db = FAISS.from_documents(docs, embeddings)

db.save_local("faiss_index")
print("✅ Base FAISS complète créée avec succès.")

import json
import chromadb
from chromadb.utils import embedding_functions

# Initialisation ChromaDB en local
client = chromadb.PersistentClient(path="./chroma_db")

# Fonction d'embedding par défaut (sentence-transformers)
embedding_fn = embedding_functions.DefaultEmbeddingFunction()

# Création de la collection
collection = client.get_or_create_collection(
    name="faq_it",
    embedding_function=embedding_fn
)

def indexer_faq(chemin_faq="faq_it.json"):
    """Charge et vectorise les documents FAQ dans ChromaDB"""
    with open(chemin_faq, "r", encoding="utf-8") as f:
        faq = json.load(f)

    ids = [doc["id"] for doc in faq]
    documents = [f"{doc['sujet']} : {doc['contenu']}" for doc in faq]
    metadatas = [{"categorie": doc["categorie"], "sujet": doc["sujet"]} for doc in faq]

    collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
    print(f"{len(faq)} documents FAQ indexés dans ChromaDB")

def rechercher_faq(requete, n_resultats=2):
    """Recherche les documents FAQ les plus proches de la requête"""
    resultats = collection.query(
        query_texts=[requete],
        n_results=n_resultats
    )
    return resultats["documents"][0], resultats["metadatas"][0]

if __name__ == "__main__":
    indexer_faq()
    # Test de recherche
    docs, metas = rechercher_faq("je n'arrive pas à me connecter")
    print("\n=== TEST DE RECHERCHE ===")
    for doc, meta in zip(docs, metas):
        print(f"[{meta['categorie']}] {doc[:100]}...")

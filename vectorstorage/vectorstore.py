from langchain.vectorstores.faiss import FAISS
from embeddings_store import get_embeddings, Embeddings
from langchain.document_loaders import YoutubeLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from urllib.parse import urlparse, parse_qs

def get_vectorstore_for_db(video_url: str, embedding: Embeddings) -> FAISS:
    vectorstore_path = get_path_from_url(video_url)

    embeddings = get_embeddings(embedding)

    if(check_if_vector_db_exists(video_url) != True):
        save_vector_db_from_youtube_url(video_url, vectorstore_path, embeddings)

    db = FAISS.load_local(vectorstore_path, embeddings)

    return db

def save_vector_db_from_youtube_url(video_url: str, db_path: str, embeddings) -> None:
    db = create_vector_db_from_youtube_url(video_url, embeddings)
    db.save_local(db_path)

def create_vector_db_from_youtube_url(video_url: str, embeddings) -> FAISS:

    print(f"Creating vectorstore for {video_url}")

    loader = YoutubeLoader.from_youtube_url(video_url)
    transcript = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
    docs = text_splitter.split_documents(transcript)

    print(f"Loaded {len(docs)} documents, creating vectorstore...")

    db = FAISS.from_documents(docs, embeddings)

    print(f"Created vectorstore for {video_url}")
    return db

def get_path_from_url(url: str) -> str:
    video_id = parse_qs(urlparse(url).query).get("v") or url.split("/")[-1]
    return f"./vectorstorage/{video_id}.faiss"

def check_if_vector_db_exists(video_url: str) -> bool:
    import os
    path = get_path_from_url(video_url)
    exists = os.path.exists(path)
    print(f"Vectorstore exists: {exists}")
    return exists

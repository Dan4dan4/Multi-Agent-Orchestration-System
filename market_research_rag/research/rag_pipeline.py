import os
import time
from typing import List, Dict, Any
import chromadb
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
import numpy as np
from research.models import Document
from transformers import pipeline

# global hugging face pipeline(used for generate response)
# =====================================================
generator = pipeline(
    task="text2text-generation",
    model="google/flan-t5-base"
)


# DOC LOADING AND CHUNKING

def load_and_chunk_docs():
    """
    Load documents and chunk them into pieces
    chunk size is 500words, with an overlap of 50words
    """
    # import the document
    documents = Document.objects.all()

    # the structure of how my splitting is designed
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500,
        chunk_overlap = 50,
        # we are defining how chunk is measured and its by len, token is also an option
        length_function = len,
        # "\n\n" is paragraphs, "\n" is lines, " " is words, "" is characters
        separators = ["\n\n", "\n", " ", ""])
    
    all_chunks = []

    for doc in documents:
        # use the spliting structure i defined and split the text
        chunks = text_splitter.split_text(doc.content)
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "document_id": doc.id,
                "chunk_index": i,
                "content": chunk,
                "metadata": {
                    "title": doc.title,
                    "company": doc.company,
                    "doc_type": doc.doc_type,
                    "date_filed": str(doc.date_filed)
                }
            })
    return all_chunks

# VECTOR DB SETUP

# chunks is a list of dictionaries- each dictionary represents a doc chunk with content and metadata
# https://docs.trychroma.com/docs/overview/getting-started is the chromadb docs

def vector_db(chunks: List[Dict]):
    """
    Setup chromadb vector db and store doc chunks with embeddings
    Everything that will ever be inputed into this RAG will nest itself into our chromadb called "financial_documents"
    This is basically creating the brain of our RAG, this is the only data the RAG will ever generate responses off of.
    """

    # this is how you initialize a chromadb client
    client= chromadb.Client()

    # this tries to create a collection in chromadb call "financial_documents"
    try:
        # collection in chromadb is a table database that holds all your doc chunks and embeddings
        collection = client.create_collection(
            name="financial_documents",
            # tells chroma to use cosine similarity for vector comparisions
            metadata={"hnsw:space": "cosine"}
        )
    # if collection already exists just retrieve it 
    except Exception:
        collection = client.get_collection("financial_documents")

    # all-MiniLM-L6-v2 is the model that converts text into numeric vectors that captures semantic meaning
    model = SentenceTransformer("all-MiniLM-L6-v2")
    # all-MiniLM-L6-v2 converts chunk texts into vector of numbers and then numpy uses "tolist" to convert those 
    # numbers into a list
    embeddings = [model.encode(chunk["content"]).tolist() for chunk in chunks]

    # failsafe if statement to prevent duplication
    if collection.count() == 0:
        # chromadb table db adds ids, documents, embeddings(numeric vector of chunks), metadata into 1 table collection
        collection.add(
            ids=[f"{chunk['document_id']}_{chunk['chunk_index']}" for chunk in chunks],
            documents=[chunk["content"] for chunk in chunks],
            embeddings=embeddings,
            metadatas=[chunk["metadata"] for chunk in chunks]
        )
        # Stored 10 chunks in ChromaDB collection financial_documents
        print(f"Stored {len(chunks)} chunks in ChromaDB collection '{collection.name}'")
    else:
        print(f"Collection already contains {collection.count()} chunks")

    return collection

# Query Processing

def process_query(query: str):
    """
    process user query and convert to embeddings(numbers) for vector search
    """

    model = SentenceTransformer("all-MiniLM-L6-v2")

    # lower cased and stripped to remove accidental whitespace. prevents embedding noise problems
    cleaned_query = query.lower().strip()

    # this is what we will pass into chromadb
    query_embedding = model.encode([cleaned_query])

    return query_embedding

# Vector Search

# the collection is the brain of the documents provided and the query_embedding is the numerical 
# vector of the question asked. top_k controls how many chunks we retrieve. more chunks = more noise
def search_vector(collection, query_embedding, top_k: int =3):
    """
    this will search and compare query_embedding to every stored chunk embedding and rank them based on 
    cosine since we defined that. this function returns chunk text/metadata.
    """
    # search rag memory
    results= collection.query(
        # this is the meaning of the users question
        query_embeddings= [query_embedding],
        # give me the top_k results
        n_results = top_k
    )

    return results

#  Context Augmentation

def augment_context(query: str, search_results: List[Dict]) -> str:
    """
    Build an augmented prompt using retrieved document chunks.
    The LLM will only answer using the provided context and say idk if it doesn't know.
    """

    # fail safe incase we dont see any relevant info, we DONT generate an answer
    # prevents hallucinations
    if not search_results:
        return (
            "No relevant information found in the documents.\n\n"
            f"Question: {query}\n\n"
            "Answer: I don't know based on the provided documents."
        )
    
    # each chunk that will be helpfull will be stored here
    context_blocks = []

    # loop through chunk and source them as: 
    for i, result in enumerate(search_results, 1):
        context_blocks.append(
            # Source 1, Source 2, Source 3
            f"Source {i}:\n"
            f"Company: {result['metadata']['company']}\n"
            f"Document Type: {result['metadata']['doc_type']}\n"
            f"Content:\n{result['content']}"
        )

    # Combines all chunk strings into 1 big block context section separated by blank lines
    context = "\n\n".join(context_blocks)

    # this prompt is sent to the LLM, we tell it what it is(financial research assistant)
    # we tell it the strict rules:
    # force a grounded answer if it doesnt know:
    augmented_prompt = f"""
You are a financial research assistant.

RULES:
- Use ONLY the information in the context below
- If the answer is not present, say "I don't know based on the provided documents"
- Do NOT use outside knowledge to answer
- Cite which Source you used

CONTEXT:
{context}

QUESTION:
{query}

ANSWER:
"""

    return augmented_prompt


# Response generation 

def generate_response(augmented_prompt: str) -> str:
    """
    generate a response using the free Hugging Face model.
    This is the real LLM step of the RAG pipeline.
    """

    

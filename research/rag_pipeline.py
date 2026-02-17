import os
import time
from typing import List, Dict, Any
import chromadb
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
import numpy as np
from research.models import Document
from transformers import pipeline
import re

# global hugging face pipeline(used for generate response)

# create text generation pipeline using a hugging face
generator = pipeline(
     # this model receives text and returns text
    task="text2text-generation",
    # this is a free model that does not require api keys
    model="google/flan-t5-base"
)

# to clean the text from whitespaces and newlines with a single space
def clean_text(text):
    # replace multiple whitespaces/newlines with single space
    text = re.sub(r'\s+', ' ', text)
    # remove weird unicode characters
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    return text.strip()

# remove repeated numeric/financial sentences
def clean_response(response: str) -> str:
    return re.sub(r'(\b[A-Za-z0-9.,%$]+\b)( \1)+', r'\1', response)

# DOC LOADING AND CHUNKING

def chunk_documents(documents: List[Dict], chunk_size: int = 300, chunk_overlap: int = 50) -> List[Dict]:
    """
    Load documents and chunk them into pieces
    chunk size is 500words, with an overlap of 50words
    """
    # import the document #REMOVED SINCE WE DONT WANT TO SAVE DOCS TO DB
    # documents = Document.objects.all()

    # the structure of how my splitting is designed
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = chunk_size,
        chunk_overlap = chunk_overlap,
        # we are defining how chunk is measured and its by len, token is also an option
        length_function = len,
        # "\n\n" is paragraphs, "\n" is lines, " " is words, "" is characters
        separators = ["\n\n", "\n", " ", ""])
    
    all_chunks = []

    for doc_index, doc in enumerate(documents):
        chunks = text_splitter.split_text(clean_text(doc["content"]))
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "document_id": doc_index,
                "chunk_index": i,
                "content": chunk,
                "metadata": {
                    "title": doc["title"],
                    "company": doc["company"],
                    "doc_type": doc["doc_type"],
                    "date_filed": str(doc["date_filed"])
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

    # initialize chromadb client
    client = chromadb.Client()

    # try to create a collection in chromadb called "financial_documents"
    try:
        # collection in chromadb is a table database that holds all your doc chunks and embeddings
        collection = client.create_collection(
            name="financial_documents",
            # tells chroma to use cosine similarity for vector comparisons
            metadata={"hnsw:space": "cosine"}
        )
    # if collection already exists just retrieve it 
    except Exception:
        collection = client.get_collection("financial_documents")

    # initialize embedding model
    # all-MiniLM-L6-v2 is the model that converts text into numeric vectors that captures semantic meaning
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # convert chunk texts into numeric embeddings
    # numpy tolist converts embeddings from arrays to plain lists
    embeddings = [model.encode(chunk["content"]).tolist() for chunk in chunks]

    # failsafe to prevent duplication
    if collection.count() == 0:
        # add chunks, embeddings, and metadata into chromadb collection
        # collection.add stores ids, documents, embeddings, and metadata in one table
        collection.add(
            ids=[f"{chunk['document_id']}_{chunk['chunk_index']}" for chunk in chunks],
            documents=[chunk["content"] for chunk in chunks],
            embeddings=embeddings,
            metadatas=[chunk["metadata"] for chunk in chunks]
        )
        # log how many chunks were stored
        print(f"Stored {len(chunks)} chunks in ChromaDB collection '{collection.name}'")
    else:
        # if collection already has data, just report count
        print(f"Collection already contains {collection.count()} chunks")

    # return collection object for further usage
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
    query_embedding = model.encode(cleaned_query)

    return query_embedding

# Vector Search

# the collection is the brain of the documents provided and the query_embedding is the numerical 
# vector of the question asked. top_k controls how many chunks we retrieve. more chunks = more noise
def search_vector(collection, query_embedding, top_k=3):
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

    docs_and_metadata = results


    filtered = [
        {"content": doc, "metadata": meta}
        for doc, meta in zip(docs_and_metadata['documents'][0], docs_and_metadata['metadatas'][0])
        if len(doc.strip()) > 20  # ignore very short chunks
    ]

    return filtered

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
    # creating a set so it doesnt repeat the same chunk over and over
    seen_contents = set()

    # loop through chunk and source them as: 
    for i, result in enumerate(search_results, 1):
        content = result['content'].strip()
        if content in seen_contents:
            continue  # skip duplicates
        seen_contents.add(content)
        context_blocks.append(
            f"Source {i}:\n"
            f"Company: {result['metadata']['company']}\n"
            f"Document Type: {result['metadata']['doc_type']}\n"
            f"Content:\n{content}"
        )

    # Combines all chunk strings into 1 big block context section separated by blank lines
    context = "\n\n".join(context_blocks)

    # this prompt is sent to the LLM, we tell it what it is(financial research assistant)
    # we tell it the strict rules:
    # force a grounded answer if it doesnt know:
    augmented_prompt = f"""
You are a financial research assistant.

RULES:
- Use the information in the context below to answer as best you can
- If the answer is not present, say "I don't know based on the provided documents"
- Do NOT use outside knowledge to answer
- Be concise and factual
- Keep it simple and straightforward
- If you find an answer, do not repeat it more than once, just give the answer directly
- If you see an out of context answer, provide full context in your answer to justify it

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

    # create text generation pipeline using a hugging face
    try:
        # call the model with controlled parameters
        # we are sending the augmented prompt, max length, and temperature controls
        # do_sample means enable sampling for varied outputs
        # creativity, low value= more facts and is strict
        output = generator(
            augmented_prompt,
            max_length=512,
            # give short answers, we want concise and to the point responses, not long essays
            max_new_tokens=256,
            # do sample FALSE means always pick the most likely next token and TRUE means allow for randomness and creativity so it will give you diff answer each times
            do_sample=False,
            # low number means more focused and deterministic, high number means more creative but also more likely to hallucinate
            temperature=0.1
        )
        # this will return a list, we will extract the 1st result
        response = output[0]["generated_text"]

    # incase model doesnt load, network issues
    except Exception as e:
        response = f"Error generating response: {e}"

    return response

def run_rag_pipeline(uploaded_docs: List[Dict], query: str, top_k: int = 3):
    """
    Run the full RAG pipeline:
    1. Load documents and chunk
    2. Store chunks in ChromaDB
    3. Convert query to embedding
    4. Retrieve relevant chunks
    5. Build augmented prompt
    6. Generate response via Hugging Face
    """

    if not uploaded_docs:
        return "No documents uploaded."
    
    # Step 1: load and chunk docs
    chunks = chunk_documents(uploaded_docs)
    if not chunks:
        print("No documents found in DB.")
        return "No documents available."

    # Step 2: store chunks in vector db
    collection = vector_db(chunks)

    # Step 3: processs user query to embeddings
    query_embedding = process_query(query)

    # Step 4: search the vector database
    results = search_vector(collection, query_embedding, top_k=top_k)

    # Step 5: build docs_and_metadata safely
    # docs_and_metadata = []
    # for doc_list, meta_list in zip(results.get('documents', []), results.get('metadatas', [])):
    #     for doc, meta in zip(doc_list, meta_list):
    #         if isinstance(meta, list) and len(meta) == 1:
    #             meta = meta[0]
    #         docs_and_metadata.append({"content": doc, "metadata": meta})

    
    # Step 5: search_vector already returns cleaned format
    docs_and_metadata = results

    # Step 6: build augmented prompt for LLM
    augmented_prompt = augment_context(query, docs_and_metadata)

    # Step 7: generate response using hugging face
    response = generate_response(augmented_prompt)
    response = clean_response(response)

    return response

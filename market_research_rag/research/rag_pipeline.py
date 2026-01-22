import os
import time
from typing import List, Dict, Any
import chromadb
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
import numpy as np
from research.models import Document

# DOC LOADING AND CHUNKING

def load_and_chunk_docs():
    """
    Load documents and chunk them into pieces
    chunk size is 500words, with an overlap of 50words
    """
    documents = Document.objects.all()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500,
        chunk_overlap = 50,
        length_function = len,
        separators = ["\n\n", "\n", " ", ""])
    
    all_chunks = []

    for doc in documents:
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


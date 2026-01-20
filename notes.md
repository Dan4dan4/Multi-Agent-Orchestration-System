# Multi-Agent-Orchestration-System

What is RAG?
Retrieval Augmented Generation is a pattern where you dont ask an LLM to rely on its memory. Instead, you retrieve relevant knowledge at query time and five it to the model as context.

# Chunking- the process of splittiong large documents into smaller pieces so they can be 
    -embedded
    -retrieved
    -fed into an llm as context
LLMs cannot read entire documents. They have a limited context window. Chunking is how you make large data usable.

If you dont chunk-
    -embeddings lose meaning
    -retrieval becomes noisy
    -answers reference the wrong parts of a document
    -context gets cut off mid-idea
Bad chunking = bad RAG


chunking example-

Original document:

Options trading requires a minimum margin of $10,000.
Margin requirements may change based on volatility.
Special rules apply to retail accounts.


Chunked:

Chunk 1: Options trading requires a minimum margin of $10,000.
Chunk 2: Margin requirements may change based on volatility.
Chunk 3: Special rules apply to retail accounts.


Each chunk:
    -Gets embedded
    -Stored with metadata
    -Retrieved independently

# Hallucination- is when an LLM-
                    -produces condifent-sounding
                    -plausible
                    -but factually incorrect or made-up information

Hallucinations happen because LLMs do not know facts, they predict the next token based on probabilities and not truth.
LLMs ARE OPTIMIZED FOR FLUENCY NOT ACCURACY.


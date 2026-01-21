# Multi-Agent-Orchestration-System

What is RAG?
Retrieval Augmented Generation is a pattern where you dont ask an LLM to rely on its memory. Instead, you retrieve relevant knowledge at query time and five it to the model as context.

# Chunking- the process of splitting large documents into smaller pieces so they can be 
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

Common chunking methods is splitting documents into 200-500words in each chunk. But if you have alot of data on 1 doc, the 500 words might become a problem because somewhere in the documentt the 500word chunk might end inbetween a sentence and leave context out. So to fix this you would put an overlap of maybe 50-100words so that every begin/end of the chunk might be able to capture the full sentence and not leave any context/logic out.

# Chunking Best Practices-
size guidelines: 200-500 characters, 50-100 character overlap
boundary rules: split at sentences, Avoid mid-word breaks
quality checks: test with real queries, verify context preservation, monitor search results



chunking example in chunking_demo.py and agentic_chunking.py



# Hallucination- is when an LLM-
                    -produces condifent-sounding
                    -plausible
                    -but factually incorrect or made-up information

Hallucinations happen because LLMs do not know facts, they predict the next token based on probabilities and not truth.
# LLMs ARE OPTIMIZED FOR FLUENCY NOT ACCURACY.

common causes for hallucinations are -
    -missing or weak context
    -asking about data the model doesnt have
    -vague prompts
    -overly long context
    -conflicting retrieved chunks
    -asking for citations when none exist

RAG reduced hallucinations by supplying a real source text, constraining the model, grounding responses in retrieved data
example prompt- "Answer ONLY using the provided context. If the answer is not present, say ‘I don’t know."
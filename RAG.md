# Understanding RAG

example:
If I ask chatgpt whats my companys policy for a in-house allowance, it will say that its something like "1000$ for a inhouse allowance", which is incorrect. Where did it get my policy and which company I got hired at information from? So to get the correct answer I have to provide it with a correct RAG.

Retrieval- I have to supply it with a document that it will only retrieve from
Augmented- I have to prompt it in a way so that it ONLY uses the retrieval data i provided^
Generation- The Ai agent will generate a response based on the question I asked(augmented) and the document i provided(retrieval).

Part of an LLM- is having 
    -Restrictions/Security - We never want to reveal personal employee info or confidential info
                            - if someone asks about sensitive topics, politely redirect them to authority/HR
                            - this is the rulebook it must follow to keep the bot safe/reliable
    -Style/Language/Voice - a solution to this is fine tuning
                            -Fine tuning is the process of providing 100s+ sample questions and sample answers so that the bot can respond to you in that way
                            -Fine tuning is not good for dynamic factual information since that info can be changed, and you dont want to retrain it often, no citations on latest data possible, and the larger the training data, the lower the accuracy of the bot is. Instead of finetuning we use RAG, but we dont need RAG for style/language/voice since that remains constant

RAG- Retrieval Augmented Generation

retrieval:
this is keyword/vector search- for retrieval there are 2 very popular keyword search tools. the BM250 and the TFIDF
                    - these tool searchs are given words and documents, and they give you a specific weight and score based on how much they think those words are valued based on how many times it occured and how many times it DIDNT occur

semantic search- search that understands meaning not words given to it.
    example- search for furniture and it will understand what furnite(desk, chair etc) and then it will search based on that rather than search for the actual word "furniture"
## see sentence_similarity.py
Embedding models- takes text and converts it into vectors/numbers to give it meaning.

Vector databases- are instant, relevant results
                -efficient resource usage
                -scalibility
                -uses smart indexing algorithms

Indexing in a vector database is a data structure or technique that lets the database search for vectors efficiently.

Without an index:
To find the most similar vector to a query, the DB would have to compute the distance to every vector. This is called linear search and is slow for millions of vectors.

With an index:
The database organizes vectors in a smart way so you can find nearest neighbors quickly. This is called approximate nearest neighbor (ANN) search.

Some common vector indexing techniques are-

Flat / brute force:Stores all vectors as-is, checks every vector	Exact results	Slow for large data
IVF (Inverted File Index):Partitions vectors into clusters, searches clusters only	Faster than brute force	Approximate
HNSW (Hierarchical Navigable Small World):Builds a graph of vectors, navigates neighbors efficiently	Very fast, good accuracy	More memory
PQ (Product Quantization):Compresses vectors into smaller codes for faster distance calculation	Efficient memory usage	Approximate


Vector databases are specialized databases designed to store and search high-dimensional vectors (embeddings). Unlike traditional databases that store text, numbers, or structured data, vector databases are optimized for similarity search.

An embedding is a numerical representation of something (like text, image, audio, or graph) in the form of a vector (a list of numbers). Instead of storing raw text or images, you convert it to a vector of numbers. These numbers capture the meaning or features of the data.

Key benefits of vector databases-Store millions of embeddings efficiently
                                -Fast similarity search across all vectors
                                -Persistent storage that survives restarts
                                -Can be shared across multiple applications

popular vectordbs-
chroma is python friendly/free/opensource but not for production
pinecone is a manage service, you send queries and they do the computations for you and bill you



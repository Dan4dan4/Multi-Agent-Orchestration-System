import { useState, useEffect } from "react";
import { askRag } from "../../api/api";

export default function RagChat() {
    const [query, setQuery] = useState("");
    const [response, setResponse] = useState("");
    const [loading, setLoading] = useState(false);

    useEffect(() => {
    const handleBeforeUnload = async () => {
      try {
        await fetch("http://127.0.0.1:8000/rag/clear_docs/", {
          method: "POST",
        });
        console.log("Temporary documents cleared on server.");
      } catch (err) {
        console.warn("Failed to clear temporary docs:", err);
      }
    };

    window.addEventListener("beforeunload", handleBeforeUnload);
    
    return () => {
      window.removeEventListener("beforeunload", handleBeforeUnload);
    };
  }, []);

  const handleSubmit = async () => {
    try {
      setLoading(true);
      const res = await askRag(query);
      setResponse(res.data.answer);
    } catch (err) {
      setResponse("Error connecting to RAG service");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>RAG Assistant</h2>

      <textarea
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Ask a question..."
      />

      <button onClick={handleSubmit}>Ask</button>

      {loading && <p>Thinking...</p>}

      {response && (
        <div>
          <h4>Response</h4>
          <p>{response}</p>
        </div>
      )}
    </div>
  );
}
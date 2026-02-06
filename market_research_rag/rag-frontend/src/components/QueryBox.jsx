import { useState } from "react";
import { askRag } from "../api/api";

export default function QueryBox() {

  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    setLoading(true);

    try {
      const res = await askRag(query);
      setAnswer(res.data.answer);
    } catch (err) {
      setAnswer("Error contacting backend");
    }

    setLoading(false);
  };

  return (
    <div>
      <h2>Ask Document Question</h2>

      <form onSubmit={handleSubmit}>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask something from documents"
        />

        <button type="submit">
          Ask
        </button>
      </form>

      {loading && <p>Loading...</p>}

      {answer && (
        <div>
          <h3>Answer</h3>
          <p>{answer}</p>
        </div>
      )}
    </div>
  );
}

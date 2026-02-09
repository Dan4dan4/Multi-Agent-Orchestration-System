import { useState } from "react";
import { askRag } from "../api/api";
import "./QueryBox.css";

// Function to parse percentages and dollar amounts from text
function parseFinancialData(text) {
  const percentRegex = /\d+(\.\d+)?%/g; 
  const dollarRegex = /\$[\d,.]+(B|M)?/gi; 

  const percentages = text.match(percentRegex) || [];
  const dollars = text.match(dollarRegex) || [];

  return { percentages, dollars };
}

export default function QueryBox() {
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [percentages, setPercentages] = useState([]);
  const [dollars, setDollars] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    setLoading(true);
    setAnswer("");
    setPercentages([]);
    setDollars([]);

    try {
      const res = await askRag(query);
      const text = res.data.answer || "";

      setAnswer(text);

      const { percentages, dollars } = parseFinancialData(text);
      setPercentages(percentages);
      setDollars(dollars);
    } catch (err) {
      setAnswer("Error contacting backend");
    }

    setLoading(false);
  };

  return (
    <div className="query-box">
      <h2>Ask Document Question</h2>

      <form onSubmit={handleSubmit}>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask me anything!"
        />
        <button type="submit">Ask</button>
      </form>

      {loading && <p>Loading...</p>}

      {answer && (
        <div className="answer-section">
          <h3>Answer</h3>
          <p>{answer}</p>

          {percentages.length > 0 && (
            <div>
              <h4>Percentages</h4>
              <ul>
                {percentages.map((p, i) => (
                  <li key={i}>{p}</li>
                ))}
              </ul>
            </div>
          )}

          {dollars.length > 0 && (
            <div>
              <h4>Dollar Amounts</h4>
              <ul>
                {dollars.map((d, i) => (
                  <li key={i}>{d}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

import RagChat from "./components/rag/RagChat";
import QueryBox from "./components/QueryBox";
import "./App.css";

function App() {
  return (
    <div className="app-container">
      <h1>RAG</h1>

      <div className="fullscreen-box">
        <QueryBox />
      </div>
    </div>
  );
}

export default App;

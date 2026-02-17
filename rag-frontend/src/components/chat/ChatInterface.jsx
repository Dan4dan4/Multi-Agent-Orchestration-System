import { useState, useRef, useEffect } from "react";
import { askRag, uploadDocument, clearDocs } from "../../api/api";
import "./ChatInterface.css";

function parseFinancialData(text) {
  const percentRegex = /\d+(\.\d+)?%/g;
  const dollarRegex = /\$[\d,.]+(B|M|K)?/gi;
  return text.replace(percentRegex, '<span class="badge badge-percent">$&</span>')
             .replace(dollarRegex, '<span class="badge badge-dollar">$&</span>');
}

export default function ChatInterface() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("");
  const [documentName, setDocumentName] = useState("");
  const [dragOver, setDragOver] = useState(false);

  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    clearDocs().catch(() => {});
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height =
        Math.min(textareaRef.current.scrollHeight, 160) + "px";
    }
  }, [input]);

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed || loading) return;

    const userMessage = { role: "user", content: trimmed };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await askRag(trimmed);
      const text = res.data.answer || "No response received.";
      setMessages((prev) => [...prev, { role: "assistant", content: text }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, something went wrong. Please try again." },
      ]);
    }

    setLoading(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileSelect = (selectedFile) => {
    if (!selectedFile) return;
    setFile(selectedFile);
    setUploadStatus("");
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploadStatus("uploading");
    const formData = new FormData();
    formData.append("file", file);

    try {
      await uploadDocument(formData);
      setUploadStatus("success");
      setDocumentName(file.name);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `"${file.name}" has been uploaded successfully. You can now ask questions about it.`,
        },
      ]);
      setFile(null);
    } catch {
      setUploadStatus("error");
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) handleFileSelect(droppedFile);
  };

  return (
    <div
      className={`chat-container ${dragOver ? "drag-over" : ""}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* Header */}
      <header className="chat-header">
        <button
          className="chat-header-title"
          onClick={() => { setMessages([]); setInput(""); setFile(null); setUploadStatus(""); }}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
          <span>AskRag</span>
        </button>
        {documentName && (
          <div className="document-indicator">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
            </svg>
            <span>{documentName}</span>
          </div>
        )}
      </header>

      {/* Messages */}
      <div className="messages-area">
        {messages.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
              </svg>
            </div>
            <h2>AskRag</h2>
            <p>Upload a file to start asking questions!</p>
            <div className="empty-state-steps">
              <p>1. Click "Upload Document" to upload a PDF or document</p>
              <p>2. Wait for the upload to complete</p>
              <p>3. Type your question in the text box below and hit Enter</p>
            </div>
          </div>
        ) : (
          <div className="messages-list">
            {messages.map((msg, i) => (
              <div key={i} className={`message message-${msg.role}`}>
                <div className="message-bubble">
                  {msg.role === "assistant" ? (
                    <span
                      dangerouslySetInnerHTML={{
                        __html: parseFinancialData(msg.content),
                      }}
                    />
                  ) : (
                    msg.content
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="message message-assistant">
                <div className="message-bubble typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* File chip */}
      {file && (
        <div className="file-chip-bar">
          <div className="file-chip">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
            </svg>
            <span>{file.name}</span>
            {uploadStatus === "uploading" && <span className="chip-status">Uploading...</span>}
            {uploadStatus === "error" && <span className="chip-status chip-error">Failed</span>}
            <button className="chip-upload-btn" onClick={handleUpload} disabled={uploadStatus === "uploading"}>
              Upload
            </button>
            <button
              className="chip-remove"
              onClick={() => { setFile(null); setUploadStatus(""); }}
            >
              &times;
            </button>
          </div>
        </div>
      )}

      {/* Input bar */}
      <div className="input-bar">
        <input
          type="file"
          ref={fileInputRef}
          onChange={(e) => handleFileSelect(e.target.files[0])}
          style={{ display: "none" }}
        />
        <button
          className="icon-btn"
          onClick={() => fileInputRef.current?.click()}
          title="Attach file"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" />
          </svg>
        </button>
        <textarea
          ref={textareaRef}
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question..."
          rows={1}
        />
        <button
          className="icon-btn send-btn"
          onClick={handleSend}
          disabled={!input.trim() || loading}
          title="Send"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" />
          </svg>
        </button>
      </div>

      {/* Drag overlay */}
      {dragOver && (
        <div className="drag-overlay">
          <div className="drag-overlay-content">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
            <p>Drop file to upload</p>
          </div>
        </div>
      )}
    </div>
  );
}

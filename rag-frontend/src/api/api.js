import axios from "axios";

// this file sets base backend url 
// creates reusable functions
const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json"
  }
});

// this function asks question
export const askRag = (query) => {
  return api.post("/rag/ask/", { query });
};

// this function uploads documents
export const uploadDocument = (formData) => {
  return api.post("/rag/upload/", formData, {
    headers: {
      "Content-Type": "multipart/form-data"
    }
  });
};

export const clearDocs = () => api.post("/rag/clear_docs/");

export default api;

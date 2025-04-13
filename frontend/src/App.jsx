import React, { useState } from "react";

export default function App() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const apiUrl = import.meta.env.VITE_APP_API_URL || "https://default.example.com";

  const sendMessage = async () => {
    const trimmedInput = input.trim();
    if (!trimmedInput) return;

    const userMessage = { role: "user", content: trimmedInput };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    try {
      const response = await fetch(apiUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: trimmedInput }),
      });

      if (!response.ok) throw new Error("Network response was not ok");
      const data = await response.json();

      const botMessage = {
        role: "bot",
        content: data.response ?? "🤖 No response received.",
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      const errorMessage = {
        role: "bot",
        content: "⚠️ Failed to fetch response.",
      };
      setMessages((prev) => [...prev, errorMessage]);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl bg-white shadow-xl rounded-2xl p-6 space-y-4">
        <h1 className="text-2xl font-bold text-gray-800">Chat with LlamaIndex 🦙</h1>

        <div className="h-96 overflow-y-auto bg-gray-50 p-4 rounded-xl space-y-2 flex flex-col">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`p-3 rounded-xl max-w-xs whitespace-pre-wrap ${
                msg.role === "user"
                  ? "bg-blue-100 self-end ml-auto"
                  : "bg-green-100 self-start"
              }`}
            >
              {msg.content}
            </div>
          ))}
        </div>

        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") sendMessage();
            }}
            className="flex-1 border rounded-xl p-3 outline-none"
            placeholder="Ask me something..."
          />
          <button
            onClick={sendMessage}
            className="bg-blue-600 text-white rounded-xl px-4 py-2 hover:bg-blue-700"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
import React, { useState } from "react";

export default function App() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    const res = await fetch("https://llama-chat-xtaa.onrender.com/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: input })
    });

    const data = await res.json();
    const botMessage = { role: "bot", content: data.response };
    setMessages((prev) => [...prev, botMessage]);
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl bg-white shadow-xl rounded-2xl p-6 space-y-4">
        <h1 className="text-2xl font-bold text-gray-800">Chat with LlamaIndex 🦙</h1>
        <div className="h-96 overflow-y-auto bg-gray-50 p-4 rounded-xl space-y-2">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={\`p-3 rounded-xl max-w-xs \${msg.role === "user" ? "bg-blue-100 self-end ml-auto" : "bg-green-100 self-start"}\`}
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
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
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
// src/App.jsx
import React, { useEffect, useState } from "react";
import ReactWebChat from "botframework-webchat";
import "./App.css";

function App() {
  const [token, setToken] = useState(null);

  useEffect(() => {
    // Replace this fetch with your backend service that returns a Direct Line token
    async function fetchToken() {
      try {
        const response = await fetch("/api/directline/token");
        const { token } = await response.json();
        setToken(token);
      } catch (err) {
        console.error("Error fetching Direct Line token:", err);
      }
    }

    fetchToken();
  }, []);

  return (
    <div className="App">
      <h1 className="title">E.e.r.s. Demo</h1>
      <div className="chat-container">
        {token ? (
          <div>
            <h2 className="sub-title">What resources can we help you find today?</h2>
            <ReactWebChat
              directLine={window.WebChat.createDirectLine({ token })}
              userID="user1"
              username="You"
              locale="en-US"
              styleOptions={{
                botAvatarInitials: "E.e.r.s.",
                userAvatarInitials: "You",
                botAvatarBackgroundColor: "#c22f96",
                userAvatarBackgroundColor: "#4b8bec",
                bubbleBackground: "#E6F7FF",
                bubbleFromUserBackground: "#DCF8C6",
                backgroundColor: "#F5F5F5",
              }}
            />
          </div>
        ) : (
          <p>Loading chat...</p>
        )}
      </div>
    </div>
  );
}

export default App;

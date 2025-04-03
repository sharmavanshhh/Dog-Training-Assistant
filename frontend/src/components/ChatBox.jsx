import React, { useState, useEffect, useRef } from "react";
import { io } from "socket.io-client";
import axios from "axios";
import MessageBubble from "./MessageBubble";

const socket = io("http://localhost:5000");

const ChatBox = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sessionId] = useState(Date.now().toString());
  const [currentResponse, setCurrentResponse] = useState(""); // Tracks current bot response
  const messagesEndRef = useRef(null);

  useEffect(() => {
    socket.on("bot_response", (data) => {
      setCurrentResponse((prev) => prev + data.response); // Append streamed response correctly
    });

    return () => {
      socket.off("bot_response");
    };
  }, []);

  useEffect(() => {
    if (currentResponse) {
      setMessages((prevMessages) => {
        const updatedMessages = [...prevMessages];

        if (updatedMessages.length > 0 && updatedMessages[updatedMessages.length - 1].sender === "bot") {
          updatedMessages[updatedMessages.length - 1].text = currentResponse; // Update last message in place
        }
        return updatedMessages;
      });
      scrollToBottom();
    }
  }, [currentResponse]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, 100);
  };

  const sendMessage = () => {
    if (!input.trim()) return;

    setMessages((prevMessages) => [...prevMessages, { sender: "user", text: input }]);
    setMessages((prevMessages) => [...prevMessages, { sender: "bot", text: "" }]); // Empty placeholder for bot response

    setCurrentResponse(""); // Clear previous response before streaming starts
    socket.emit("user_message", { session_id: sessionId, message: input });

    setInput("");
  };

  // const generateSummary = async () => {
  //   try {
  //     const response = await axios.post("http://localhost:5000/generate_summary", { session_id: sessionId });
  //     alert("Chat Summary:\n" + response.data.summary);
  //   } catch (error) {
  //     console.error("Error generating summary:", error);
  //   }
  // };


const generateSummary = async () => {
  // Ask for user's email
  const email = prompt("Please enter your email to receive the summary:");

  if (!email) {
    alert("Email is required to send the summary.");
    return;
  }

  try {
    // Send email and session ID to the backend to generate and email the summary
    const response = await axios.post("http://localhost:5000/generate_summary", {
      session_id: sessionId,
      email: email,
    });

    alert("Summary has been sent to your email!");
  } catch (error) {
    console.error("Error generating and sending the summary:", error);
  }
};


  const downloadChat = async () => {
    try {
      const response = await axios.post("http://localhost:5000/download_chat", { session_id: sessionId }, { responseType: "blob" });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `chat_session_${sessionId}.pdf`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error("Error downloading chat:", error);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-box">
        {messages.map((msg, index) => (
          <MessageBubble key={index} sender={msg.sender} text={msg.text} />
        ))}
        <div ref={messagesEndRef} />
      </div>
      <div className="input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && sendMessage()}
          placeholder="Ask Krypto..."
        />
        <button onClick={sendMessage}>➔</button>
      </div>
      <div className="buttons">
        <button onClick={generateSummary}>Generate Summary</button>
        <button onClick={downloadChat}>Download Chat</button>
      </div>
    </div>
  );
};

export default ChatBox;

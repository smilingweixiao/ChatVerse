"use client"
import { useEffect, useState } from "react";

export default function Home() {
  const [messages, setMessages] = useState<{ text: string; message_side: string }[]>([]);
  const [messageInput, setMessageInput] = useState("");

  useEffect(() => {
    const sendMessage = (text: string) => {
      if (text.trim() === "") return;

      setMessages((prevMessages) => [
        ...prevMessages,
        { text, message_side: prevMessages.length % 2 === 0 ? "right" : "left" },
      ]);
      setMessageInput("");
    };

    sendMessage("Hello Philip! :)");
    setTimeout(() => sendMessage("Hi Sandy! How are you?"), 1000);
    setTimeout(() => sendMessage("I'm fine, thank you!"), 2000);
  }, []);

  const handleSendMessage = () => {
    sendMessage(messageInput);
  };

  const handleKeyUp = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.which === 13) {
      handleSendMessage();
    }
  };

  const sendMessage = (text: string) => {
    if (text.trim() === "") return;

    setMessages((prevMessages) => [
      ...prevMessages,
      { text, message_side: prevMessages.length % 2 === 0 ? "right" : "left" },
    ]);
    setMessageInput("");
  };

  return (
    <div>
      <div className="chat_window">
        <div className="top_menu">
          <div className="buttons">
            <div className="button close"></div>
            <div className="button minimize"></div>
            <div className="button maximize"></div>
          </div>
          <div className="title">Chat</div>
        </div>
        <ul className="messages">
          {messages.map((message, index) => (
            <li key={index} className={`message ${message.message_side} appeared`}>
              <div className="avatar"></div>
              <div className="text_wrapper">
                <div className="text">{message.text}</div>
              </div>
            </li>
          ))}
        </ul>
        <div className="bottom_wrapper clearfix">
          <div className="message_input_wrapper">
            <input
              className="message_input"
              placeholder="Type your message here..."
              value={messageInput}
              onChange={(e) => setMessageInput(e.target.value)}
              onKeyUp={handleKeyUp}
            />
          </div>
          <div className="send_message" onClick={handleSendMessage}>
            <div className="icon"></div>
            <div className="text">Send</div>
          </div>
        </div>
      </div>
      <div className="message_template">
        <li className="message">
          <div className="avatar"></div>
          <div className="text_wrapper">
            <div className="text"></div>
          </div>
        </li>
      </div>
    </div>
  );
}
"use client"
import { useEffect, useState, useRef } from "react";
import { io } from 'socket.io-client';
import { generate_chat, start_recording, stop_recording } from './api/chatroom'

export default function Home() {
  const [messages, setMessages] = useState<{ text: string; message_side: string; speaker: number }[]>([]);
  const [messageInput, setMessageInput] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const socket = io('http://localhost:5000');
  const [role, setRole] = useState(null);

  useEffect(() => {

    const handleRoleUpdate = ((roleData) => {
        setRole(roleData);
    });
 
    setMessages(() => [
        { text: "hello!", message_side: "left", speaker: -1},
    ]);

    socket.on('role_updated', handleRoleUpdate);

    return () => {
        socket.off('role_updated', handleRoleUpdate); // 清除事件監聽器
    };

  }, []);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages.length]);

  const handleSendMessage = () => {
    sendMessage(messageInput);
  };

  const handleKeyUp = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.which === 13) {
      handleSendMessage();
    }
  };

  const sendMessage = async (text: string) => {
    if (text.trim() === "") return;

    setMessages((prevMessages) => [
      ...prevMessages,
      { text, message_side: "right", speaker: 0},
    ]);
    setMessageInput("");

    generate_chat(text)
    .then((response) => {
      console.log(response)
      setMessages((prevMessages) => [
        ...prevMessages,
        { text: response.message, message_side: "left", speaker: response.speaker},
      ]);

    })
    .catch((err) => {
      console.error(err)
    })
   
  };


  const handleStartRecording = async () => {
    setIsRecording(true);
    console.log("Recording started...");
    start_recording()
    .then((response) => {
      console.log(response)
    })
    .catch((err) => {
      console.error(err)
    })
  };

  const handleStopRecording = async () => {

    stop_recording()
    .then((response) => {
      setMessages((prevMessages) => [
        ...prevMessages,
        { text: response.message, message_side: "right", speaker: 0},
      ]);
      generate_chat(response.message)
      .then((response) => {
        console.log(response)
        setMessages((prevMessages) => [
          ...prevMessages,
          { text: response.message, message_side: "left", speaker: response.speaker},
        ]);

      })
      .catch((err) => {
        console.error(err)
      })
    })
    .catch((err) => {
      console.error(err)
    })

    // await new Promise((resolve) => setTimeout(resolve, 500)); // 模擬網路延遲
    setIsRecording(false);
    console.log("Recording ended!");

  };

  return (
    
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
          <div ref={messagesEndRef} />
        </ul >
        
        <div className="bottom_wrapper">
          <div className="message_input_wrapper">
            <input
              className="message_input"
              placeholder="Type your message here..."
              value={messageInput}
              onChange={(e) => setMessageInput(e.target.value)}
              onKeyUp={handleKeyUp}
            />
            <button
              className="record_button"
              onClick={isRecording ? handleStopRecording : handleStartRecording}
            >
              {isRecording ? "🛑" : "🎤"}
            </button>
          </div>
          <div className="send_message" onClick={handleSendMessage}>
            <div className="icon"></div>
            <div className="text">Send</div>
          </div>
        </div>
      </div>
      // <div className="message_template">
      //   <li className="message">
      //     <div className="avatar"></div>
      //     <div className="text_wrapper">
      //       <div className="text"></div>
      //     </div>
      //   </li>
      // </div>
    
  );
}
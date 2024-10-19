"use client"
import { useEffect, useState, useRef } from "react";
import { io } from 'socket.io-client';
import { generate_chat, start_recording, stop_recording } from './api/chatroom'

export default function Home() {
  const [roles, setRole] = useState<string[]>([]);
  const [messages, setMessages] = useState<{ text: string; message_side: string; speaker: string }[]>([]);
  const [messageInput, setMessageInput] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const avatarImages: { [key: string]: string } = {
    'system': 'https://i.ibb.co/fdFTSp7/website.png',
    '1' : 'https://i.ibb.co/q7RYZ5q/1.png',
    '2' : 'https://i.ibb.co/9cJ4mLt/2.png',
    '3' : 'https://i.ibb.co/wdkppXG/3.png',
    '4' : 'https://i.ibb.co/x71Y6rB/4.png',
    '5' : 'https://i.ibb.co/Fnwnsz7/5.png',
    '6' : 'https://i.ibb.co/MMfWKPp/6.png',
    '7' : 'https://i.ibb.co/Np5s76X/7.png',
    '8' : 'https://i.ibb.co/VT7xFwJ/8.png'
  };

  const socket = io('http://localhost:5000');
  
  useEffect(() => {
 
    setMessages(() => [
        { text: "hello!", message_side: "left", speaker: 'system'}
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

  const handleRoleUpdate = ((roleName: string) => {
    if (roles.includes(roleName)) {
      setRole(roles.filter((role) => role !== roleName));

      setMessages((prevMessages) => [
        ...prevMessages,
        { text: `${roleName} leaved!`, message_side: "middle", speaker: 'system'},
      ]);
      
    } 
    else {
      setRole([...roles, roleName]);

      setMessages((prevMessages) => [
        ...prevMessages,
        { text: `${roleName} joined!`, message_side: "middle", speaker: 'system'},
      ]);

    }
  });

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
      { text, message_side: "right", speaker: 'user'}
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
        { text: response.message, message_side: "right", speaker: 'user'},
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
          <div className="title">Chat Room</div>
        </div>
        <ul className="messages">
          {messages.map((message, index) => (
            <li key={index} className={`message ${message.message_side} appeared`}>
              <div>
                <div className="avatar">
                  <a href="https://imgbb.com/">
                    <img src={avatarImages[message.speaker]} alt={avatarImages[message.speaker]}/>
                  </a>
                </div>
                <div className="name">{message.speaker}</div>
              </div>
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
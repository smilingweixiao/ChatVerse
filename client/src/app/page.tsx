"use client"
import { useEffect, useState, useRef } from "react";
import { io } from 'socket.io-client';
import { generate_chat, start_recording, stop_recording } from './api/chatroom'

const socket = io('http://127.0.0.1:5000');

export default function Home() {
  const [messages, setMessages] = useState<{ text: string; message_side: string; speaker: string }[]>([]);
  const [messageInput, setMessageInput] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [keepChat, setKeepChat] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const avatarImages: { [key: string]: string } = {
    'human': 'https://i.ibb.co/fdFTSp7/website.png',
    'joy' : 'https://i.ibb.co/q7RYZ5q/1.png',
    'debater' : 'https://i.ibb.co/9cJ4mLt/2.png',
    'hater' : 'https://i.ibb.co/wdkppXG/3.png',
    'joker' : 'https://i.ibb.co/x71Y6rB/4.png',
    'thinker' : 'https://i.ibb.co/Fnwnsz7/5.png',
    'nova' : 'https://i.ibb.co/MMfWKPp/6.png',
    'expert' : 'https://i.ibb.co/Np5s76X/7.png',
    'evil' : 'https://i.ibb.co/VT7xFwJ/8.png'
  };

  const handleRoleUpdate = ((roleData) => {
    
    if (roleData.roleState === false) {

      setMessages((prevMessages) => [
        ...prevMessages,
        { text: `${roleData.roleName} leaved!`, message_side: "middle", speaker: ''},
      ]);
      
    } 
    else {
    
      setMessages((prevMessages) => [
        ...prevMessages,
        { text: `${roleData.roleName} joined!`, message_side: "middle", speaker: ''},
      ]);

    }

  });
  
  useEffect(() => {

    socket.on("connect", () => {
      console.log(socket.id);
    });
    
    socket.on("disconnect", () => {
      console.log(socket.id);
    });

    socket.on('role_updated', handleRoleUpdate);

    return () => {
      socket.off('role_updated');
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

  const recursiveGenerateChat = async (message: string) => {
    try {
      const chatData = await generate_chat(message);

      // agent 無話可說
      if (chatData.message === '') {
        return;
      }

      // agent 有話可說，並且使用者不想說
      else if (keepChat === true) {
        setMessages((prevMessages) => [
          ...prevMessages,
          { text: chatData.message, message_side: "left", speaker: chatData.speaker },
        ]);
        await recursiveGenerateChat("");
        return;
      }

      // 使用者想說話
      else {
        setMessages((prevMessages) => [
          ...prevMessages,
          { text: chatData.message, message_side: "left", speaker: chatData.speaker },
        ]);
        return;
      }

    } catch (err) {
      console.error(err);
    }
  };


  const sendMessage = async (text: string) => {
    if (text.trim() === "") return;

    setKeepChat(false);
    setMessages((prevMessages) => [
      ...prevMessages,
      { text, message_side: "right", speaker: 'human'}
    ]);
    setMessageInput("");

    generate_chat(text)
    .then((response) => {
      console.log(response)
      setMessages((prevMessages) => [
        ...prevMessages,
        { text: response.message, message_side: "left", speaker: response.speaker},
      ]);
      setKeepChat(true);
      recursiveGenerateChat("");

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
        { text: response.message, message_side: "right", speaker: 'human'},
      ]);
      generate_chat(response.message)
      .then((response) => {
        console.log(response)
        setMessages((prevMessages) => [
          ...prevMessages,
          { text: response.message, message_side: "left", speaker: response.speaker},
        ]);
        recursiveGenerateChat("");

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
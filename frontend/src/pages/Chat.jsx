import { useState } from 'react';
import "../styles/chat.css";

function Chat() {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([
    { id: 1, user: "Друг", avatar: "🔴", text: "Привет всем! Кто уже слышал \"Nightdrive Odyssey\" от Synthwave Samurai?", time: "14:28" },
    { id: 2, user: "Я", avatar: "👤", text: "Я! Это просто нечто. Этот рифф на 2:30 заставляет меня чувствовать себя в неоновом будущем.", time: "14:29", isMe: true },
    { id: 3, user: "Соседка", avatar: "🌸", text: "Согласна, бит очень качает. Идеально для ночной поездки.", time: "14:30" },
  ]);

  const sendMessage = () => {
    if (!message.trim()) return;
    setMessages([...messages, {
      id: Date.now(),
      user: "Я",
      avatar: "👤",
      text: message,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      isMe: true
    }]);
    setMessage('');
  };

  return (
    <div className="chat-page">
      {/* Sidebar */}
      <div className="chat-sidebar">
        <div className="server-header">
          <div className="server-icon">🎵</div>
          <h3>Melo Community</h3>
        </div>

        <div className="channels">
          <div className="channel active">
            <span>#general</span>
          </div>
          <div className="channel">
            <span>#synthwave</span>
          </div>
          <div className="channel">
            <span>#releases</span>
          </div>
          <div className="channel">
            <span>#collabs</span>
          </div>
        </div>
      </div>

      {/* Main Chat */}
      <div className="chat-main">
        <div className="chat-header">
          <div className="chat-channel-name">
            <span># Флейм-Волна #General</span>
          </div>
        </div>

        <div className="messages-container">
          {messages.map(msg => (
            <div key={msg.id} className={`message ${msg.isMe ? 'my-message' : ''}`}>
              <div className="message-avatar">{msg.avatar}</div>
              <div className="message-content">
                <div className="message-header">
                  <span className="username">{msg.user}</span>
                  <span className="timestamp">{msg.time}</span>
                </div>
                <div className="message-text">{msg.text}</div>
              </div>
            </div>
          ))}
        </div>

        {/* Input Area */}
        <div className="chat-input-area">
          <div className="chat-input">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Напишите сообщение..."
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            />
            <button onClick={sendMessage} className="send-btn">➤</button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Chat;
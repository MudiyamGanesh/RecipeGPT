import React, { useState, useEffect, useRef } from 'react';
import { Plus, Trash2, Send, Menu } from 'lucide-react';
import './App.css';

const API_BASE = 'http://localhost:8000/api';

function App() {
  const [messages, setMessages] = useState([]);
  const [recents, setRecents] = useState([]);
  const [images, setImages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const chatEndRef = useRef(null);

  useEffect(() => {
    fetchImages();
    fetchRecents();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchImages = async () => {
    try {
      const res = await fetch(`${API_BASE}/images`);
      const data = await res.json();
      setImages(data.images);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchRecents = async () => {
    try {
      const res = await fetch(`${API_BASE}/recents`);
      const data = await res.json();
      setRecents(data.recents);
    } catch (e) {
      console.error(e);
    }
  };

  const handleNewChat = async () => {
    try {
      await fetch(`${API_BASE}/chat/new`, { method: 'POST' });
      setMessages([]);
      fetchRecents();
    } catch (e) {
      console.error(e);
    }
  };

  const handleLoadChat = async (id) => {
    try {
      const res = await fetch(`${API_BASE}/chat/${id}`);
      const data = await res.json();
      setMessages(data.messages);
    } catch (e) {
      console.error(e);
    }
  };

  const handleDeleteChat = async (id) => {
    try {
      await fetch(`${API_BASE}/chat/${id}`, { method: 'DELETE' });
      fetchRecents();
      // If we just deleted the active chat, we should clear
      // For simplicity, just fetch recents.
    } catch (e) {
      console.error(e);
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input }),
      });
      const data = await res.json();
      setMessages((prev) => [...prev, { role: 'assistant', content: data.answer }]);
      fetchRecents();
    } catch (e) {
      console.error(e);
      setMessages((prev) => [...prev, { role: 'assistant', content: "Error connecting to AI." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar */}
      <div className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <img src="/logo.png" alt="Logo" className="sidebar-logo" />
          <h2 className="sidebar-title">RecipeGPT</h2>
          <button className="sidebar-toggle-inside" onClick={() => setSidebarOpen(false)}>
            <Menu size={24} />
          </button>
        </div>

        <button className="new-chat-btn" onClick={handleNewChat}>
          <Plus size={20} /> New Chat
        </button>

        <h3 className="section-title">Recent Chats</h3>
        <div className="recent-chats-list">
          {recents.length === 0 ? (
            <div className="empty-recents">No saved conversations yet.</div>
          ) : (
            recents.map((chat) => (
              <div key={chat.id} className="recent-chat-item">
                <button className="chat-btn" onClick={() => handleLoadChat(chat.id)}>
                  {chat.title}
                </button>
                <button className="delete-btn" onClick={() => handleDeleteChat(chat.id)}>
                  <Trash2 size={16} />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {!sidebarOpen && (
          <button className="sidebar-toggle" onClick={() => setSidebarOpen(true)}>
            <Menu size={24} />
          </button>
        )}
        {messages.length === 0 ? (
          <HeroSection images={images} />
        ) : (
          <div className="chat-container">
            <div className="chat-header">
              <h2>RecipeGPT AI</h2>
            </div>
            <div className="chat-history">
              {messages.map((msg, idx) => (
                <div key={idx} className={`chat-message ${msg.role}`}>
                  <div className={`avatar ${msg.role}`}>
                    {msg.role === 'user' ? 'U' : <img src="/logo.png" alt="AI" className="chat-avatar-logo" />}
                  </div>
                  <div className="message-content">
                    {/* Basic text rendering. Could add react-markdown later */}
                    {msg.content.split('\n').map((line, i) => (
                      <p key={i}>{line}</p>
                    ))}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="chat-message assistant">
                  <div className="avatar assistant">
                    <img src="/logo.png" alt="AI" className="chat-avatar-logo" />
                  </div>
                  <div className="message-content loading-indicator">
                    Cooking up answer <div className="dot-flashing"></div>
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>
          </div>
        )}

        {/* Input area */}
        <div className="chat-input-wrapper">
          <form className="chat-input-container" onSubmit={handleSend}>
            <input
              type="text"
              placeholder="Ask for a recipe, ingredient swap, or meal plan..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={isLoading}
            />
            <button type="submit" disabled={isLoading || !input.trim()}>
              <Send size={20} />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

// Separate Hero Section for clarity
function HeroSection({ images }) {
  const totalImages = images.length;
  const animationDuration = Math.max(10, totalImages * 4);

  return (
    <div className="hero-wrapper">
      <div className="yummy-container">
        <div className="yummy-bg-text">R E C I P E</div>

        <div className="yummy-img-wrapper">
          {images.length === 0 ? (
            <div style={{ fontSize: '10rem' }}>🍔</div>
          ) : images.length === 1 ? (
            <img src={images[0]} className="hero-center-img" alt="Food" style={{ opacity: 1 }} />
          ) : (
            <>
              <style dangerouslySetInnerHTML={{
                __html: `
                @keyframes heroCarousel {
                    0% { opacity: 0; transform: scale(1.05) rotate(-2deg); }
                    10% { opacity: 1; transform: scale(1) rotate(0deg); }
                    ${100 / totalImages}% { opacity: 1; transform: scale(1) rotate(0deg); }
                    ${(100 / totalImages) + 10}% { opacity: 0; transform: scale(1.05) rotate(2deg); }
                    100% { opacity: 0; }
                }
              `}} />
              {images.map((src, i) => (
                <img
                  key={i}
                  src={src}
                  className="hero-center-img carousel-fade"
                  alt="Food"
                  style={{
                    animationDelay: `${(animationDuration / totalImages) * i}s`,
                    animationDuration: `${animationDuration}s`
                  }}
                />
              ))}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;

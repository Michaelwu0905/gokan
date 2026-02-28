import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { sessionAPI, scenarioAPI } from '../api';
import './Chat.css';

function Chat() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [scenario, setScenario] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadSession();
  }, [sessionId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadSession = async () => {
    try {
      const response = await sessionAPI.getById(sessionId);
      setMessages(response.data.messages);
      
      // 获取场景信息
      const scenarioRes = await scenarioAPI.getById(response.data.scenario_id);
      setScenario(scenarioRes.data);
    } catch (error) {
      console.error('加载会话失败:', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSend = async () => {
    if (!inputText.trim() || loading) return;

    const content = inputText.trim();
    setInputText('');
    setLoading(true);

    // 立即显示用户消息
    setMessages(prev => [...prev, { role: 'user', content, created_at: new Date().toISOString() }]);

    try {
      const response = await sessionAPI.sendMessage(sessionId, content);
      setMessages(prev => [...prev, response.data]);
    } catch (error) {
      console.error('发送消息失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleEndSession = async () => {
    try {
      await sessionAPI.end(sessionId);
      navigate(`/summary/${sessionId}`);
    } catch (error) {
      console.error('结束会话失败:', error);
    }
  };

  return (
    <div className="chat-container">
      <header className="chat-header">
        <button className="back-btn" onClick={() => navigate('/')}>
          ← 返回
        </button>
        <div className="chat-info">
          <h3>{scenario?.name_jp}</h3>
          <span className="character">{scenario?.character_name}</span>
        </div>
        <button className="end-btn" onClick={handleEndSession}>
          结束
        </button>
      </header>

      {scenario && (
        <div className="vocab-hints">
          <span className="hints-label">核心词汇:</span>
          {scenario.vocab_hints.map((vocab, index) => (
            <span key={index} className="hint-tag">{vocab}</span>
          ))}
        </div>
      )}

      <div className="messages-container">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`message ${msg.role === 'user' ? 'user' : 'assistant'}`}
          >
            <div className="message-bubble">
              <p>{msg.content}</p>
              {msg.role === 'assistant' && msg.audio_url && (
                <button className="audio-btn">
                  🔊
                </button>
              )}
            </div>
            <span className="message-time">
              {new Date(msg.created_at).toLocaleTimeString('zh-CN', { 
                hour: '2-digit', 
                minute: '2-digit' 
              })}
            </span>
          </div>
        ))}
        
        {loading && (
          <div className="message assistant loading">
            <div className="message-bubble">
              <span className="loading-text">ふむふむ...</span>
              <div className="loading-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <div className="input-container">
        <button className="voice-btn" title="语音输入">
          🎤
        </button>
        <textarea
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="输入日语..."
          rows={1}
        />
        <button 
          className="send-btn" 
          onClick={handleSend}
          disabled={!inputText.trim() || loading}
        >
          发送
        </button>
      </div>
    </div>
  );
}

export default Chat;

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { scenarioAPI, sessionAPI } from '../api';
import './Scenarios.css';

function Scenarios() {
  const [scenarios, setScenarios] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadScenarios();
  }, []);

  const loadScenarios = async () => {
    try {
      const response = await scenarioAPI.getAll();
      setScenarios(response.data);
    } catch (error) {
      console.error('加载场景失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleScenarioClick = async (scenarioId) => {
    try {
      const response = await sessionAPI.create(scenarioId);
      navigate(`/chat/${response.data.id}`);
    } catch (error) {
      console.error('创建会话失败:', error);
    }
  };

  if (loading) {
    return <div className="loading">ふむふむ...読み込み中</div>;
  }

  return (
    <div className="scenarios-container">
      <header className="scenarios-header">
        <h1>語感（Gokan）</h1>
        <p>选择场景开始练习日语会话</p>
      </header>

      <div className="scenarios-grid">
        {scenarios.map((scenario) => (
          <div
            key={scenario.id}
            className="scenario-card"
            onClick={() => handleScenarioClick(scenario.id)}
          >
            <div className="scenario-header">
              <span className="scenario-difficulty">{scenario.difficulty}</span>
              <h3>{scenario.name_jp}</h3>
            </div>
            <p className="scenario-name">{scenario.name}</p>
            <p className="scenario-character">
              <span className="label">角色:</span> {scenario.character_name}
            </p>
            <div className="scenario-vocab">
              <span className="label">核心词汇:</span>
              <div className="vocab-tags">
                {scenario.vocab_hints.slice(0, 3).map((vocab, index) => (
                  <span key={index} className="vocab-tag">{vocab}</span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      <nav className="bottom-nav">
        <button className="nav-btn active">练习</button>
        <button className="nav-btn" onClick={() => navigate('/stats')}>档案</button>
      </nav>
    </div>
  );
}

export default Scenarios;

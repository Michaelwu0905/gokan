import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { sessionAPI } from '../api';
import './Summary.css';

function Summary() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSummary();
  }, [sessionId]);

  const loadSummary = async () => {
    try {
      const response = await sessionAPI.getSummary(sessionId);
      setSummary(response.data);
    } catch (error) {
      console.error('加载总结失败:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">总结生成中...</div>;
  }

  return (
    <div className="summary-container">
      <header className="summary-header">
        <h1>练习总结</h1>
        <p>お疲れ様でした！来看看你的表现吧</p>
      </header>

      <div className="summary-content">
        <div className="stats-card">
          <h3>📊 本次练习数据</h3>
          <div className="stats-grid">
            <div className="stat-item">
              <span className="stat-number">{summary?.total_messages || 0}</span>
              <span className="stat-label">对话轮数</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">{summary?.errors?.length || 0}</span>
              <span className="stat-label">发现错误</span>
            </div>
          </div>
        </div>

        {summary?.errors?.length > 0 && (
          <div className="errors-card">
            <h3>📝 错误纠正</h3>
            <div className="errors-list">
              {summary.errors.map((error, index) => (
                <div key={index} className="error-item">
                  <div className="error-type">
                    {error.error_type === 'particle' ? '助词错误' : '语法错误'}
                  </div>
                  <div className="error-content">
                    <p className="original">❌ {error.original_text}</p>
                    <p className="correction">✅ {error.correction}</p>
                    <p className="explanation">💡 {error.explanation}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {summary?.suggestions?.length > 0 && (
          <div className="suggestions-card">
            <h3>💡 学习建议</h3>
            <ul className="suggestions-list">
              {summary.suggestions.map((suggestion, index) => (
                <li key={index}>{suggestion}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <div className="summary-actions">
        <button className="btn-secondary" onClick={() => navigate('/')}>
          返回首页
        </button>
        <button className="btn-primary" onClick={() => navigate('/stats')}>
          查看学习档案
        </button>
      </div>
    </div>
  );
}

export default Summary;

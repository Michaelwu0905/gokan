import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { statsAPI } from '../api';
import './Stats.css';

function Stats() {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const response = await statsAPI.getStats();
      setStats(response.data);
    } catch (error) {
      console.error('加载统计失败:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">加载中...</div>;
  }

  return (
    <div className="stats-container">
      <header className="stats-header">
        <h1>学习档案</h1>
        <p>追踪你的日语学习进度</p>
      </header>

      <div className="stats-content">
        <div className="stats-overview">
          <div className="stat-card large">
            <span className="stat-icon">📚</span>
            <span className="stat-number">{stats?.total_sessions || 0}</span>
            <span className="stat-label">练习次数</span>
          </div>
          <div className="stat-card large">
            <span className="stat-icon">💬</span>
            <span className="stat-number">{stats?.total_messages || 0}</span>
            <span className="stat-label">对话消息</span>
          </div>
          <div className="stat-card large">
            <span className="stat-icon">⏱️</span>
            <span className="stat-number">{stats?.total_practice_minutes || 0}</span>
            <span className="stat-label">练习分钟</span>
          </div>
        </div>

        {stats?.common_error_types?.length > 0 && (
          <div className="error-types-card">
            <h3>⚠️ 常见错误类型</h3>
            <div className="error-types-list">
              {stats.common_error_types.map((error, index) => (
                <div key={index} className="error-type-item">
                  <div className="error-type-name">
                    {error.type === 'particle' ? '助词错误' : '语法错误'}
                  </div>
                  <div className="error-type-bar">
                    <div 
                      className="error-type-progress"
                      style={{ width: `${Math.min(100, error.count * 20)}%` }}
                    />
                  </div>
                  <span className="error-type-count">{error.count}次</span>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="tips-card">
          <h3>💡 学习小贴士</h3>
          <ul className="tips-list">
            <li>坚持每天练习15分钟，效果比一次练习1小时更好</li>
            <li>重点关注助词（は/が/に/で）的使用</li>
            <li>遇到错误不要害怕，这是进步的机会</li>
            <li>尝试使用今天学到的新词汇</li>
          </ul>
        </div>
      </div>

      <nav className="bottom-nav">
        <button className="nav-btn" onClick={() => navigate('/')}>练习</button>
        <button className="nav-btn active">档案</button>
      </nav>
    </div>
  );
}

export default Stats;

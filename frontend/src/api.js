import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const scenarioAPI = {
  getAll: () => api.get('/scenarios'),
  getById: (id) => api.get(`/scenarios/${id}`),
};

export const sessionAPI = {
  create: (scenarioId) => api.post('/sessions', { scenario_id: scenarioId }),
  getById: (sessionId) => api.get(`/sessions/${sessionId}`),
  sendMessage: (sessionId, content, isVoice = false) => 
    api.post(`/sessions/${sessionId}/messages`, { content, is_voice: isVoice }),
  getSummary: (sessionId) => api.get(`/sessions/${sessionId}/summary`),
  end: (sessionId) => api.post(`/sessions/${sessionId}/end`),
};

export const statsAPI = {
  getStats: () => api.get('/stats'),
};

export default api;

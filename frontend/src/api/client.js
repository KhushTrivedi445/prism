import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 300000, // 5 min timeout for LLM synthesis
});

export const getHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export const getModels = async () => {
  const response = await api.get('/models');
  return response.data;
};

export const generateContent = async (payload) => {
  const response = await api.post('/generate', payload);
  return response.data;
};

export const generateContentWithUpload = async (formData) => {
  const response = await api.post('/generate/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getRuns = async () => {
  const response = await api.get('/runs');
  return response.data;
};

export const getRun = async (runId) => {
  const response = await api.get(`/runs/${runId}`);
  return response.data;
};

export const deleteRun = async (runId) => {
  const response = await api.delete(`/runs/${runId}`);
  return response.data;
};

export const getDownloadUrl = (filename) => {
  if (!filename) return '#';
  const clean = filename.split(/[\\/]/).pop();
  return `${API_BASE}/outputs/${clean}/download`;
};

export default api;

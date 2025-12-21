import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

export const taskApi = {
  getAll: () => api.get('/tasks'),
  get: (id) => api.get(`/tasks/${id}`),
  create: (task) => api.post('/tasks', task),
  update: (id, task) => api.put(`/tasks/${id}`, task),
  delete: (id) => api.delete(`/tasks/${id}`),
  seed: () => api.post('/tasks/seed')
}

export const connectionApi = {
  getAll: () => api.get('/connections'),
  create: (connection) => api.post('/connections', connection),
  update: (id, connection) => api.put(`/connections/${id}`, connection),
  delete: (id) => api.delete(`/connections/${id}`)
}

export default api


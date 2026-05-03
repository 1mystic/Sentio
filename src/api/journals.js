import client from './client.js'

export const journalsApi = {
  list: (params = {}) => client.get('/journal/', { params }),
  create: (data) => client.post('/journal/', data),
  get: (id) => client.get(`/journal/${id}`),
  update: (id, data) => client.patch(`/journal/${id}`, data),
  delete: (id) => client.delete(`/journal/${id}`),
  insights: (id) => client.get(`/journal/${id}/insights`),
  reflections: (id) => client.post(`/journal/${id}/reflections`),
  themes: () => client.get('/journal/themes'),
}

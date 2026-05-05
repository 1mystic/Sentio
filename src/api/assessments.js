import client from './client.js'

export const assessmentsApi = {
  list: () => client.get('/assessments/'),
  get: (id) => client.get(`/assessments/${id}`),
  submit: (id, data) => client.post(`/assessments/${id}/submit`, data),
  history: (id) => client.get(`/assessments/${id}/history`),
  userResults: () => client.get('/assessments/user/results'),
}

import client from './client.js'

export const biasesApi = {
  list: (params = {}) => client.get('/biases/', { params }),
  getBySlug: (slug) => client.get(`/biases/${slug}`),
  categories: () => client.get('/biases/categories'),
}

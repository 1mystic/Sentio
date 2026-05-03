import client from './client.js'

export const therapistsApi = {
  list: (params = {}) => client.get('/therapists/', { params }),
  get: (id) => client.get(`/therapists/${id}`),
  book: (id, data) => client.post(`/therapists/${id}/book`, data),
  myBookings: () => client.get('/therapists/bookings/mine'),
}

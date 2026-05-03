import client from './client.js'

export const usersApi = {
  me: () => client.get('/users/me'),
  updateMe: (data) => client.patch('/users/me', data),
  biasProfile: () => client.get('/users/me/bias-profile'),
}

import client from './client.js'

export const insightsApi = {
  biasFingerprint: () => client.get('/insights/bias-fingerprint'),
  weekly: () => client.get('/insights/weekly'),
  recommendations: () => client.get('/insights/recommendations'),
}

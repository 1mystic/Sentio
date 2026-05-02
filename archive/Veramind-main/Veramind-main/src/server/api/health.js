/**
 * Health check endpoint
 */
export default defineEventHandler((event) => {
  return {
    status: 'ok',
    timestamp: new Date().toISOString(),
    service: 'veramind-api'
  }
})


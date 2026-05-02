import { GoogleGenerativeAI } from '@google/generative-ai'

// This file is a Nuxt-style server endpoint. If you migrate to Vercel/Netlify/Supabase Edge,
// adapt the handler to the platform's function signature. The code below supports two modes:
// - Nuxt: uses defineEventHandler
// - Node/Vercel-style: exports a default handler(req, res)

const getApiKey = () => process.env.VITE_GEMINI_API_KEY || process.env.GEMINI_API_KEY

const handleChat = async ({ message, history = [] }) => {
  const apiKey = getApiKey()

  if (!apiKey) {
    throw new Error('Gemini API key not configured (VITE_GEMINI_API_KEY)')
  }

  const genAI = new GoogleGenerativeAI(apiKey)
  const model = genAI.getGenerativeModel({ model: 'gemini-1.5-pro' })

  const chat = model.startChat({
    history: history.map(msg => ({
      role: msg.role === 'user' ? 'user' : 'model',
      parts: [{ text: msg.content }]
    }))
  })

  const result = await chat.sendMessage(message)
  const response = await result.response
  const text = response.text()

  return { message: text, success: true }
}

// Nuxt handler (if present)
if (typeof defineEventHandler !== 'undefined') {
  export default defineEventHandler(async (event) => {
    const body = await readBody(event)
    const { message, history = [] } = body

    if (!message) {
      throw createError({ statusCode: 400, message: 'Message is required' })
    }

    try {
      return await handleChat({ message, history })
    } catch (err) {
      throw createError({ statusCode: 500, message: err.message })
    }
  })
} else {
  // Node/Vercel-compatible handler
  export default async function handler(req, res) {
    try {
      const body = await new Promise((resolve, reject) => {
        let data = ''
        req.on('data', chunk => (data += chunk))
        req.on('end', () => resolve(data ? JSON.parse(data) : {}))
        req.on('error', reject)
      })

      const { message, history = [] } = body
      if (!message) {
        res.statusCode = 400
        return res.end(JSON.stringify({ error: 'Message is required' }))
      }

      const result = await handleChat({ message, history })
      res.setHeader('Content-Type', 'application/json')
      res.end(JSON.stringify(result))
    } catch (err) {
      res.statusCode = 500
      res.end(JSON.stringify({ error: err.message }))
    }
  }
}


export const dynamic = 'force-dynamic'

import anthropic from '@/lib/anthropic'
import { createServerSupabaseClient } from '@/lib/supabase-server'

export async function GET(request: Request): Promise<Response> {
  const authHeader = request.headers.get('authorization')
  if (authHeader !== `Bearer ${process.env.CRON_SECRET}`) {
    return new Response('Unauthorized', { status: 401 })
  }

  const supabase = createServerSupabaseClient()

  const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString()
  const { data: sessions } = await supabase
    .from('sessions')
    .select('id, domain, turns_count, updated_at')
    .eq('is_complete', true)
    .gte('updated_at', weekAgo)

  if (!sessions?.length) return Response.json({ processed: 0 })

  const sessionIds = sessions.map((s: { id: string }) => s.id)

  const [{ data: insights }, { data: fingerprints }] = await Promise.all([
    supabase.from('insight_cards').select('*').in('session_id', sessionIds),
    supabase.from('session_fingerprints').select('*').in('session_id', sessionIds),
  ])

  if (!insights?.length) return Response.json({ processed: 0 })

  const concepts = insights.map((i: { concept: string }) => i.concept).join(', ')
  const avgClarity = Math.round(
    insights.reduce((sum: number, i: { clarity_score: number }) => sum + i.clarity_score, 0) / insights.length
  )
  const topGap = (insights[0] as { gaps: string[] })?.gaps?.[0] || 'continue exploring'
  const topFp = fingerprints?.[0] as { next_session_question?: string } | undefined

  const prompt = `Generate a weekly learning digest notification for a student.

Week summary:
- Sessions completed: ${sessions.length}
- Concepts explored: ${concepts}
- Average clarity: ${avgClarity}/100
- Top gap to address: ${topGap}
- Suggested next question: "${topFp?.next_session_question || 'Continue your learning journey'}"

Return ONLY valid JSON:
{
  "title": "Weekly digest title (max 8 words)",
  "body": "3 sentences: what they explored, their progress, what to tackle next"
}`

  try {
    const response = await anthropic.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 250,
      messages: [{ role: 'user', content: prompt }],
    })

    const text = response.content[0].type === 'text' ? response.content[0].text : '{}'
    const notif = JSON.parse(text.replace(/```json|```/g, '').trim()) as { title: string; body: string }

    // Create one digest notification targeted to the most recent session
    const latestSession = sessions.sort((a: { updated_at: string }, b: { updated_at: string }) =>
      new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
    )[0]

    await supabase.from('notifications').insert({
      session_id: latestSession.id,
      type: 'weekly_digest',
      title: notif.title,
      body: notif.body,
      action_url: `/session/${latestSession.id}`,
      metadata: { sessions_count: sessions.length, avg_clarity: avgClarity },
    })

    return Response.json({ processed: 1 })
  } catch (err) {
    console.error('Weekly digest error:', err)
    return Response.json({ processed: 0, error: 'Digest generation failed' })
  }
}

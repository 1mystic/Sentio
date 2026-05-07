export const dynamic = 'force-dynamic'

import anthropic from '@/lib/anthropic'
import { createServerSupabaseClient } from '@/lib/supabase-server'

export async function GET(request: Request): Promise<Response> {
  const authHeader = request.headers.get('authorization')
  if (authHeader !== `Bearer ${process.env.CRON_SECRET}`) {
    return new Response('Unauthorized', { status: 401 })
  }

  const supabase = createServerSupabaseClient()

  const cutoff = new Date(Date.now() - 48 * 60 * 60 * 1000).toISOString()
  const { data: sessions } = await supabase
    .from('sessions')
    .select('id, domain, updated_at')
    .eq('is_complete', true)
    .gte('updated_at', cutoff)

  if (!sessions?.length) return Response.json({ processed: 0 })

  let processed = 0

  for (const session of sessions) {
    try {
      const [{ data: fp }, { data: insight }] = await Promise.all([
        supabase.from('session_fingerprints').select('*').eq('session_id', session.id).single(),
        supabase.from('insight_cards').select('*').eq('session_id', session.id).single(),
      ])

      if (!fp || !insight) continue

      const topGap = (insight.gaps as string[])?.[0]
      const hoursElapsed = (Date.now() - new Date(session.updated_at as string).getTime()) / 3600000
      const S = 2 * Math.exp(4 * ((insight.clarity_score as number) / 100) + 0.5 * Math.log(2))
      const retention = Math.exp(-hoursElapsed / S)

      if (retention > 0.7) continue

      // Skip if a daily_reflect notification was already sent today for this session
      const today = new Date().toISOString().slice(0, 10)
      const { data: existing } = await supabase
        .from('notifications')
        .select('id')
        .eq('session_id', session.id)
        .eq('type', 'daily_reflect')
        .gte('created_at', `${today}T00:00:00Z`)
        .limit(1)
      if (existing?.length) continue

      const prompt = `Generate a short, warm notification to bring a learner back to study.

Session concept: ${insight.concept}
Their clarity score: ${insight.clarity_score}/100
Top gap to address: ${topGap || 'continue deepening'}
Hours since last session: ${Math.round(hoursElapsed)}
Estimated retention: ${Math.round(retention * 100)}%
Next question prepared: "${(fp.next_session_question as string) || 'Pick up where you left off'}"

Return ONLY valid JSON (no markdown):
{
  "title": "short notification title (max 8 words)",
  "body": "2 sentence body — warm, specific, references the concept"
}`

      const response = await anthropic.messages.create({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 200,
        messages: [{ role: 'user', content: prompt }],
      })

      const text = response.content[0].type === 'text' ? response.content[0].text : '{}'
      const notif = JSON.parse(text.replace(/```json|```/g, '').trim()) as { title: string; body: string }

      await supabase.from('notifications').insert({
        session_id: session.id,
        type: 'daily_reflect',
        title: notif.title,
        body: notif.body,
        action_url: `/session/${session.id}`,
        metadata: { concept: insight.concept, retention: Math.round(retention * 100) },
      })

      processed++
    } catch (err) {
      console.error(`Daily reflect error for session ${session.id}:`, err)
    }
  }

  return Response.json({ processed })
}

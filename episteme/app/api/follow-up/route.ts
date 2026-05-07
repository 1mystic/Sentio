import { createServerSupabaseClient } from '@/lib/supabase-server'

export async function POST(request: Request): Promise<Response> {
  const { sessionId, question } = await request.json() as { sessionId: string; question: string }

  if (!sessionId || !question?.trim()) {
    return Response.json({ error: 'Missing fields' }, { status: 400 })
  }

  const supabase = createServerSupabaseClient()
  const { data, error } = await supabase
    .from('follow_up_questions')
    .insert({ session_id: sessionId, question: question.trim() })
    .select()
    .single()

  if (error) return Response.json({ error: error.message }, { status: 500 })
  return Response.json({ question: data })
}

export async function GET(request: Request): Promise<Response> {
  const { searchParams } = new URL(request.url)
  const sessionId = searchParams.get('sessionId')
  if (!sessionId) return Response.json({ error: 'Missing sessionId' }, { status: 400 })

  const supabase = createServerSupabaseClient()
  const { data } = await supabase
    .from('follow_up_questions')
    .select('*')
    .eq('session_id', sessionId)
    .eq('is_addressed', false)
    .order('created_at', { ascending: false })

  return Response.json({ questions: data || [] })
}

export async function PATCH(request: Request): Promise<Response> {
  const { id } = await request.json() as { id: string }
  const supabase = createServerSupabaseClient()
  await supabase.from('follow_up_questions').update({ is_addressed: true }).eq('id', id)
  return Response.json({ success: true })
}

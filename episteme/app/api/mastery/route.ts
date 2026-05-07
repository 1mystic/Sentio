import { createServerSupabaseClient } from '@/lib/supabase-server'

export async function POST(request: Request): Promise<Response> {
  const { sessionId, concept, rating } = await request.json() as {
    sessionId: string
    concept: string
    rating: 'got_it' | 'needs_review' | 'no_idea'
  }

  if (!sessionId || !concept || !rating) {
    return Response.json({ error: 'Missing fields' }, { status: 400 })
  }

  const supabase = createServerSupabaseClient()
  const { data, error } = await supabase
    .from('mastery_ratings')
    .insert({ session_id: sessionId, concept, rating })
    .select()
    .single()

  if (error) return Response.json({ error: error.message }, { status: 500 })
  return Response.json({ rating: data })
}

export async function GET(request: Request): Promise<Response> {
  const { searchParams } = new URL(request.url)
  const sessionId = searchParams.get('sessionId')
  if (!sessionId) return Response.json({ error: 'Missing sessionId' }, { status: 400 })

  const supabase = createServerSupabaseClient()
  const { data } = await supabase
    .from('mastery_ratings')
    .select('*')
    .eq('session_id', sessionId)
    .order('rated_at', { ascending: false })

  return Response.json({ ratings: data || [] })
}

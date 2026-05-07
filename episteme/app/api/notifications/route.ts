import { createServerSupabaseClient } from '@/lib/supabase-server'

export async function GET(request: Request): Promise<Response> {
  const { searchParams } = new URL(request.url)
  const sessionId = searchParams.get('sessionId')
  const unreadOnly = searchParams.get('unread') === 'true'

  if (!sessionId) return Response.json({ error: 'Missing sessionId' }, { status: 400 })

  const supabase = createServerSupabaseClient()

  let query = supabase
    .from('notifications')
    .select('*')
    .eq('session_id', sessionId)
    .order('created_at', { ascending: false })
    .limit(20)

  if (unreadOnly) query = query.eq('is_read', false)

  const { data } = await query
  return Response.json({ notifications: data || [] })
}

export async function PATCH(request: Request): Promise<Response> {
  const { notificationId, sessionId } = await request.json() as { notificationId?: string; sessionId?: string }
  const supabase = createServerSupabaseClient()

  if (notificationId) {
    await supabase.from('notifications').update({ is_read: true }).eq('id', notificationId)
  } else if (sessionId) {
    await supabase.from('notifications').update({ is_read: true }).eq('session_id', sessionId)
  }

  return Response.json({ success: true })
}

export async function DELETE(request: Request): Promise<Response> {
  const { searchParams } = new URL(request.url)
  const sessionId = searchParams.get('sessionId')
  if (!sessionId) return Response.json({ error: 'Missing sessionId' }, { status: 400 })

  const supabase = createServerSupabaseClient()
  await supabase.from('notifications').delete().eq('session_id', sessionId)
  return Response.json({ success: true })
}

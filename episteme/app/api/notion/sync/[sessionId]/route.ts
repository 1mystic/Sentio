import { createServerSupabaseClient } from '@/lib/supabase-server'

function buildNotionBlocks(
  session: Record<string, unknown>,
  fp: Record<string, unknown> | null,
  insight: Record<string, unknown> | null,
  profile: Record<string, unknown> | null,
  syncCount: number
): object[] {
  const timestamp = new Date().toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' })

  const blocks: object[] = [
    { object: 'block', type: 'divider', divider: {} },
    {
      object: 'block', type: 'heading_2',
      heading_2: {
        rich_text: [{ type: 'text', text: { content: `Sync #${syncCount + 1} — ${timestamp}` } }],
        color: 'yellow_background',
      },
    },
    {
      object: 'block', type: 'callout',
      callout: {
        rich_text: [{
          type: 'text',
          text: { content: `Clarity: ${insight?.clarity_score ?? 0}/100 · Domain: ${session?.domain ?? 'unknown'} · Turns: ${session?.turns_count ?? 0}` },
        }],
        icon: { emoji: '🧠' },
        color: 'yellow_background',
      },
    },
    {
      object: 'block', type: 'heading_3',
      heading_3: { rich_text: [{ type: 'text', text: { content: 'What You Understand' } }] },
    },
    {
      object: 'block', type: 'paragraph',
      paragraph: { rich_text: [{ type: 'text', text: { content: (insight?.insight as string) || 'Session in progress' } }] },
    },
    {
      object: 'block', type: 'heading_3',
      heading_3: { rich_text: [{ type: 'text', text: { content: 'Priority Gaps' } }] },
    },
    ...((insight?.gaps as string[]) || []).map((gap, i) => ({
      object: 'block', type: 'bulleted_list_item',
      bulleted_list_item: {
        rich_text: [{ type: 'text', text: { content: `${gap} — review in ${i === 0 ? '24h' : i === 1 ? '72h' : '4 days'}` } }],
      },
    })),
    {
      object: 'block', type: 'heading_3',
      heading_3: { rich_text: [{ type: 'text', text: { content: 'Next Session' } }] },
    },
    {
      object: 'block', type: 'quote',
      quote: {
        rich_text: [{
          type: 'text',
          text: { content: (fp?.next_session_question as string) || (profile?.next_session_starter as string) || 'Continue exploring this concept' },
        }],
      },
    },
  ]

  if (profile?.metacognitive_note) {
    blocks.push({
      object: 'block', type: 'callout',
      callout: {
        rich_text: [{ type: 'text', text: { content: profile.metacognitive_note as string } }],
        icon: { emoji: '💡' },
        color: 'default',
      },
    })
  }

  return blocks
}

export async function POST(
  _request: Request,
  { params }: { params: Promise<{ sessionId: string }> }
): Promise<Response> {
  const { sessionId } = await params
  const supabase = createServerSupabaseClient()

  const { data: connection } = await supabase
    .from('notion_connections')
    .select('*')
    .eq('session_id', sessionId)
    .single()

  if (!connection) {
    return Response.json({ error: 'No Notion connection for this session' }, { status: 404 })
  }

  const [
    { data: session },
    { data: fp },
    { data: insight },
    { data: profile },
  ] = await Promise.all([
    supabase.from('sessions').select('*').eq('id', sessionId).single(),
    supabase.from('session_fingerprints').select('*').eq('session_id', sessionId).single(),
    supabase.from('insight_cards').select('*').eq('session_id', sessionId).single(),
    supabase.from('learner_profiles').select('*').eq('session_id', sessionId).single(),
  ])

  const blocks = buildNotionBlocks(
    session as Record<string, unknown>,
    fp as Record<string, unknown> | null,
    insight as Record<string, unknown> | null,
    profile as Record<string, unknown> | null,
    (connection.sync_count as number) || 0
  )

  const notionRes = await fetch(
    `https://api.notion.com/v1/blocks/${connection.notion_page_id}/children`,
    {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${connection.notion_token}`,
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28',
      },
      body: JSON.stringify({ children: blocks }),
    }
  )

  if (!notionRes.ok) {
    const err = await notionRes.json() as { message?: string }
    return Response.json({ error: 'Notion sync failed', details: err.message }, { status: 502 })
  }

  await supabase
    .from('notion_connections')
    .update({
      last_synced_at: new Date().toISOString(),
      sync_count: ((connection.sync_count as number) || 0) + 1,
    })
    .eq('session_id', sessionId)

  return Response.json({ success: true, notionPageUrl: connection.notion_page_url })
}

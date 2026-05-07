import { createServerSupabaseClient } from '@/lib/supabase-server'

export async function POST(request: Request): Promise<Response> {
  const { sessionId, notionToken, notionPageId } = await request.json() as {
    sessionId: string
    notionToken: string
    notionPageId: string
  }

  if (!sessionId || !notionToken || !notionPageId) {
    return Response.json({ error: 'Missing required fields' }, { status: 400 })
  }

  // Validate Notion token
  const userRes = await fetch('https://api.notion.com/v1/users/me', {
    headers: {
      'Authorization': `Bearer ${notionToken}`,
      'Notion-Version': '2022-06-28',
    },
  })

  if (!userRes.ok) {
    return Response.json({ error: 'Invalid Notion token' }, { status: 401 })
  }

  // Get page title
  const pageRes = await fetch(`https://api.notion.com/v1/pages/${notionPageId}`, {
    headers: {
      'Authorization': `Bearer ${notionToken}`,
      'Notion-Version': '2022-06-28',
    },
  })

  let pageTitle = 'Episteme Session'
  let notionPageUrl = `https://notion.so/${notionPageId.replace(/-/g, '')}`

  if (pageRes.ok) {
    const pageData = await pageRes.json() as {
      url?: string
      properties?: { title?: { title?: Array<{ plain_text?: string }> } }
    }
    if (pageData.url) notionPageUrl = pageData.url
    const titleProp = pageData.properties?.title?.title?.[0]?.plain_text
    if (titleProp) pageTitle = titleProp
  }

  const supabase = createServerSupabaseClient()

  await supabase
    .from('notion_connections')
    .upsert({
      session_id: sessionId,
      notion_token: notionToken,
      notion_page_id: notionPageId,
      notion_page_url: notionPageUrl,
      is_active: true,
    }, { onConflict: 'session_id' })

  // Trigger first sync
  const appUrl = process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'
  fetch(`${appUrl}/api/notion/sync/${sessionId}`, { method: 'POST' }).catch(console.error)

  return Response.json({ success: true, notionPageUrl, pageTitle })
}

export async function GET(request: Request): Promise<Response> {
  const { searchParams } = new URL(request.url)
  const sessionId = searchParams.get('sessionId')
  if (!sessionId) return Response.json({ error: 'Missing sessionId' }, { status: 400 })

  const supabase = createServerSupabaseClient()
  const { data } = await supabase
    .from('notion_connections')
    .select('notion_page_id, notion_page_url, last_synced_at, sync_count, is_active')
    .eq('session_id', sessionId)
    .single()

  return Response.json({ connection: data || null })
}

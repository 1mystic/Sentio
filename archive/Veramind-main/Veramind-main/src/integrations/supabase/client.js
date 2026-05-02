import { createClient } from '@supabase/supabase-js'

// For Vite-based apps, use `import.meta.env` to access client-exposed env vars.
// These should be set as `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY`.
const supabaseUrl = import.meta?.env?.VITE_SUPABASE_URL || process.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta?.env?.VITE_SUPABASE_ANON_KEY || process.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables. Set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY in your environment.')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true
  }
})


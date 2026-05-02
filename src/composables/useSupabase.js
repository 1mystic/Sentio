import { createClient } from '@supabase/supabase-js'

const SUPABASE_URL = 'https://ibpgzviwquauzhkmlvnl.supabase.co'
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlicGd6dml3cXVhdXpoa21sdm5sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU2NDM5MTAsImV4cCI6MjA2MTIxOTkxMH0.gQ8zr5bdsQdmSvHUIFfzS7vqkJUOqdLmdpswHfDz2nw'

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)

export function useSupabase() {
  return { supabase }
}

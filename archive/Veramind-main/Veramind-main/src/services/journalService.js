import { supabase } from '../integrations/supabase/client'

/**
 * Journal Service
 * Handles all journal entry operations
 */
export const journalService = {
  /**
   * Get all journal entries for a user
   */
  async getEntries(userId, options = {}) {
    try {
      let query = supabase
        .from('journal_entries')
        .select('*')
        .eq('user_id', userId)
        .order('date', { ascending: false })

      if (options.dateFrom) {
        query = query.gte('date', options.dateFrom)
      }

      if (options.dateTo) {
        query = query.lte('date', options.dateTo)
      }

      if (options.search) {
        query = query.ilike('content', `%${options.search}%`)
      }

      const { data, error } = await query

      if (error) throw error
      return { data, error: null }
    } catch (error) {
      return { data: null, error }
    }
  },

  /**
   * Get a single journal entry by ID
   */
  async getEntry(entryId) {
    try {
      const { data, error } = await supabase
        .from('journal_entries')
        .select('*')
        .eq('id', entryId)
        .single()

      if (error) throw error
      return { data, error: null }
    } catch (error) {
      return { data: null, error }
    }
  },

  /**
   * Create a new journal entry
   */
  async createEntry(entry) {
    try {
      const { data, error } = await supabase
        .from('journal_entries')
        .insert({
          user_id: entry.user_id,
          date: entry.date,
          content: entry.content,
          prompt: entry.prompt || null,
          tags: entry.tags || [],
          mood: entry.mood || null
        })
        .select()
        .single()

      if (error) throw error
      return { data, error: null }
    } catch (error) {
      return { data: null, error }
    }
  },

  /**
   * Update an existing journal entry
   */
  async updateEntry(entryId, updates) {
    try {
      const { data, error } = await supabase
        .from('journal_entries')
        .update({
          ...updates,
          updated_at: new Date().toISOString()
        })
        .eq('id', entryId)
        .select()
        .single()

      if (error) throw error
      return { data, error: null }
    } catch (error) {
      return { data: null, error }
    }
  },

  /**
   * Delete a journal entry
   */
  async deleteEntry(entryId) {
    try {
      const { error } = await supabase
        .from('journal_entries')
        .delete()
        .eq('id', entryId)

      if (error) throw error
      return { error: null }
    } catch (error) {
      return { error }
    }
  },

  /**
   * Get entries by date range
   */
  async getEntriesByDateRange(userId, startDate, endDate) {
    try {
      const { data, error } = await supabase
        .from('journal_entries')
        .select('*')
        .eq('user_id', userId)
        .gte('date', startDate)
        .lte('date', endDate)
        .order('date', { ascending: false })

      if (error) throw error
      return { data, error: null }
    } catch (error) {
      return { data: null, error }
    }
  }
}


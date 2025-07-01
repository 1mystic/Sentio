import { supabase } from '@/integrations/supabase/client';
import type { Tables, TablesInsert, TablesUpdate } from '@/integrations/supabase/types';

// 1. Type Definitions
export type JournalEntry = Tables<'journal_entries'>;
export type JournalEntryInsert = TablesInsert<'journal_entries'>;
export type JournalEntryUpdate = TablesUpdate<'journal_entries'>;

/**
 * 2. Creates a new journal entry.
 * @param entryData - The data for the new journal entry.
 * @returns The newly created journal entry.
 */
export const createJournalEntry = async (entryData: JournalEntryInsert): Promise<JournalEntry> => {
  const { data, error } = await supabase
    .from('journal_entries')
    .insert(entryData)
    .select()
    .single();

  if (error) {
    console.error('Error creating journal entry:', error.message);
    throw new Error(`Failed to create journal entry: ${error.message}`);
  }
  if (!data) {
    throw new Error('Failed to create journal entry: No data returned.');
  }
  return data;
};

/**
 * 3. Fetches all journal entries for a given user.
 * @param userId - The ID of the user whose entries to fetch.
 * @returns An array of journal entries, ordered by date (descending).
 */
export const getJournalEntries = async (userId: string): Promise<JournalEntry[]> => {
  const { data, error } = await supabase
    .from('journal_entries')
    .select('*')
    .eq('user_id', userId)
    .order('date', { ascending: false });

  if (error) {
    console.error('Error fetching journal entries:', error.message);
    throw new Error(`Failed to fetch journal entries: ${error.message}`);
  }
  return data || [];
};

/**
 * 4. Fetches a single journal entry by its ID and user ID.
 * @param entryId - The ID of the journal entry to fetch.
 * @param userId - The ID of the user who owns the entry.
 * @returns The journal entry object or null if not found or not authorized.
 */
export const getJournalEntryById = async (entryId: string, userId: string): Promise<JournalEntry | null> => {
  const { data, error } = await supabase
    .from('journal_entries')
    .select('*')
    .eq('id', entryId)
    .eq('user_id', userId)
    .single();

  if (error) {
    // It's not necessarily an error if .single() finds no rows,
    // Supabase returns a PostgrestError with code 'PGRST116' in that case.
    if (error.code === 'PGRST116') {
      return null;
    }
    console.error('Error fetching journal entry by ID:', error.message);
    throw new Error(`Failed to fetch journal entry by ID: ${error.message}`);
  }
  return data;
};

/**
 * 5. Updates an existing journal entry.
 * @param entryId - The ID of the journal entry to update.
 * @param updates - An object containing the fields to update.
 * @param userId - The ID of the user who owns the entry.
 * @returns The updated journal entry.
 */
export const updateJournalEntry = async (
  entryId: string,
  updates: JournalEntryUpdate,
  userId: string
): Promise<JournalEntry> => {
  const { data, error } = await supabase
    .from('journal_entries')
    .update(updates)
    .eq('id', entryId)
    .eq('user_id', userId)
    .select()
    .single();

  if (error) {
    console.error('Error updating journal entry:', error.message);
    // Consider PGRST116 for not found as well, similar to getJournalEntryById
    throw new Error(`Failed to update journal entry: ${error.message}`);
  }
  if (!data) {
    throw new Error('Failed to update journal entry: No data returned.');
  }
  return data;
};

/**
 * 6. Deletes a journal entry.
 * @param entryId - The ID of the journal entry to delete.
 * @param userId - The ID of the user who owns the entry.
 */
export const deleteJournalEntry = async (entryId: string, userId: string): Promise<void> => {
  const { error } = await supabase
    .from('journal_entries')
    .delete()
    .eq('id', entryId)
    .eq('user_id', userId);

  if (error) {
    console.error('Error deleting journal entry:', error.message);
    throw new Error(`Failed to delete journal entry: ${error.message}`);
  }
};

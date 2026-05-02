/**
 * Supabase Database Types
 * 
 * This file contains TypeScript-like type definitions for Supabase tables.
 * Update these as your database schema evolves.
 */

/**
 * User Profile
 */
export const UserProfile = {
  id: 'uuid',
  user_id: 'uuid', // References auth.users
  full_name: 'string',
  email: 'string',
  avatar_url: 'string | null',
  bio: 'string | null',
  created_at: 'timestamp',
  updated_at: 'timestamp',
  archetype: 'string | null', // Set by Archetype Model batch job
  engagement_score: 'number | null' // Set by Engagement Model
}

/**
 * Journal Entry
 */
export const JournalEntry = {
  id: 'uuid',
  user_id: 'uuid',
  date: 'date', // YYYY-MM-DD
  content: 'text',
  prompt: 'string',
  tags: 'string[]',
  mood: 'number | null', // 1-10 scale
  sentiment: 'jsonb | null', // ML analysis result
  created_at: 'timestamp',
  updated_at: 'timestamp'
}

/**
 * Assessment
 */
export const Assessment = {
  id: 'uuid',
  user_id: 'uuid',
  type: 'string', // 'GAD-7', 'PHQ-9', 'cognitive-bias', 'core-values'
  score: 'number',
  severity: 'string', // 'minimal', 'mild', 'moderate', 'severe'
  responses: 'jsonb', // Question-answer pairs
  completed_at: 'timestamp',
  created_at: 'timestamp'
}

/**
 * Module Progress
 */
export const ModuleProgress = {
  id: 'uuid',
  user_id: 'uuid',
  module_id: 'string',
  module_name: 'string',
  progress_percentage: 'number', // 0-100
  current_lesson: 'number',
  completed_lessons: 'number[]',
  started_at: 'timestamp',
  completed_at: 'timestamp | null',
  updated_at: 'timestamp'
}

/**
 * Community Post
 */
export const CommunityPost = {
  id: 'uuid',
  user_id: 'uuid',
  title: 'string',
  content: 'text',
  category: 'string',
  tags: 'string[]',
  is_anonymous: 'boolean',
  likes_count: 'number',
  replies_count: 'number',
  created_at: 'timestamp',
  updated_at: 'timestamp'
}

/**
 * Community Reply
 */
export const CommunityReply = {
  id: 'uuid',
  post_id: 'uuid',
  user_id: 'uuid',
  content: 'text',
  parent_reply_id: 'uuid | null', // For nested replies
  is_anonymous: 'boolean',
  likes_count: 'number',
  created_at: 'timestamp',
  updated_at: 'timestamp'
}

/**
 * Educational Article
 */
export const EducationalArticle = {
  id: 'uuid',
  title: 'string',
  content: 'text',
  category: 'string',
  difficulty: 'string', // 'beginner', 'intermediate', 'advanced'
  read_time: 'number', // minutes
  author: 'string',
  tags: 'string[]',
  embedding: 'vector | null', // pgvector for RAG
  created_at: 'timestamp',
  updated_at: 'timestamp'
}

/**
 * Support Group
 */
export const SupportGroup = {
  id: 'uuid',
  name: 'string',
  description: 'text',
  category: 'string',
  is_private: 'boolean',
  member_count: 'number',
  created_at: 'timestamp'
}

/**
 * Group Membership
 */
export const GroupMembership = {
  id: 'uuid',
  group_id: 'uuid',
  user_id: 'uuid',
  joined_at: 'timestamp'
}


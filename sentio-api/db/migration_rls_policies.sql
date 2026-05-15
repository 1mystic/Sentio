-- journal_entries
ALTER TABLE journal_entries ENABLE ROW LEVEL SECURITY;
CREATE POLICY "user_own_journal" ON journal_entries
  FOR ALL USING (auth.uid() = user_id);

-- user_bias_profiles
ALTER TABLE user_bias_profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY "user_own_bias_profile" ON user_bias_profiles
  FOR ALL USING (auth.uid() = user_id);

-- assessment_results
ALTER TABLE assessment_results ENABLE ROW LEVEL SECURITY;
CREATE POLICY "user_own_assessments" ON assessment_results
  FOR ALL USING (auth.uid() = user_id);

-- socratic_sessions
ALTER TABLE socratic_sessions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "user_own_sessions" ON socratic_sessions
  FOR ALL USING (auth.uid() = user_id);

-- notifications
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
CREATE POLICY "user_own_notifications" ON notifications
  FOR ALL USING (auth.uid() = user_id);

-- user_badges
ALTER TABLE user_badges ENABLE ROW LEVEL SECURITY;
CREATE POLICY "user_own_badges" ON user_badges
  FOR ALL USING (auth.uid() = user_id);

-- bookings
ALTER TABLE bookings ENABLE ROW LEVEL SECURITY;
CREATE POLICY "user_own_bookings" ON bookings
  FOR ALL USING (auth.uid() = user_id);

-- ai_conversations
ALTER TABLE ai_conversations ENABLE ROW LEVEL SECURITY;
CREATE POLICY "user_own_ai_conversations" ON ai_conversations
  FOR ALL USING (auth.uid() = user_id);

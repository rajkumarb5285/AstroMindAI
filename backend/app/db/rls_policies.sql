-- ==============================================================================
-- AstroMind AI - Production Row-Level Security (RLS) Policies
-- Enforces tenant isolation at the PostgreSQL database level
-- ==============================================================================

-- 1. Enable RLS on all tenant-owned tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE birth_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE chart_calculations ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_tool_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE consent_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE astrology_rules ENABLE ROW LEVEL SECURITY;

-- 2. Profiles Policies
CREATE POLICY "profiles_owner_select" ON profiles
    FOR SELECT USING (auth.uid()::text = id);

CREATE POLICY "profiles_owner_update" ON profiles
    FOR UPDATE USING (auth.uid()::text = id);

-- 3. Birth Profiles Policies
CREATE POLICY "birth_profiles_owner_select" ON birth_profiles
    FOR SELECT USING (auth.uid()::text = owner_id);

CREATE POLICY "birth_profiles_owner_insert" ON birth_profiles
    FOR INSERT WITH CHECK (auth.uid()::text = owner_id);

CREATE POLICY "birth_profiles_owner_update" ON birth_profiles
    FOR UPDATE USING (auth.uid()::text = owner_id);

CREATE POLICY "birth_profiles_owner_delete" ON birth_profiles
    FOR DELETE USING (auth.uid()::text = owner_id);

-- 4. Chart Calculations Policies
CREATE POLICY "chart_calculations_owner_select" ON chart_calculations
    FOR SELECT USING (auth.uid()::text = owner_id);

CREATE POLICY "chart_calculations_owner_insert" ON chart_calculations
    FOR INSERT WITH CHECK (auth.uid()::text = owner_id);

CREATE POLICY "chart_calculations_owner_delete" ON chart_calculations
    FOR DELETE USING (auth.uid()::text = owner_id);

-- 5. Conversations Policies
CREATE POLICY "conversations_owner_select" ON conversations
    FOR SELECT USING (auth.uid()::text = owner_id);

CREATE POLICY "conversations_owner_insert" ON conversations
    FOR INSERT WITH CHECK (auth.uid()::text = owner_id);

CREATE POLICY "conversations_owner_update" ON conversations
    FOR UPDATE USING (auth.uid()::text = owner_id);

CREATE POLICY "conversations_owner_delete" ON conversations
    FOR DELETE USING (auth.uid()::text = owner_id);

-- 6. Messages Policies
CREATE POLICY "messages_owner_select" ON messages
    FOR SELECT USING (auth.uid()::text = owner_id);

CREATE POLICY "messages_owner_insert" ON messages
    FOR INSERT WITH CHECK (auth.uid()::text = owner_id);

CREATE POLICY "messages_owner_delete" ON messages
    FOR DELETE USING (auth.uid()::text = owner_id);

-- 7. Chat Tool Runs Policies
CREATE POLICY "chat_tool_runs_owner_select" ON chat_tool_runs
    FOR SELECT USING (auth.uid()::text = owner_id);

CREATE POLICY "chat_tool_runs_owner_insert" ON chat_tool_runs
    FOR INSERT WITH CHECK (auth.uid()::text = owner_id);

-- 8. Reports Policies
CREATE POLICY "reports_owner_select" ON reports
    FOR SELECT USING (auth.uid()::text = owner_id);

CREATE POLICY "reports_owner_insert" ON reports
    FOR INSERT WITH CHECK (auth.uid()::text = owner_id);

CREATE POLICY "reports_owner_delete" ON reports
    FOR DELETE USING (auth.uid()::text = owner_id);

-- 9. Subscriptions Policies
CREATE POLICY "subscriptions_owner_select" ON subscriptions
    FOR SELECT USING (auth.uid()::text = user_id);

-- 10. Consent Records Policies
CREATE POLICY "consent_records_owner_select" ON consent_records
    FOR SELECT USING (auth.uid()::text = user_id);

CREATE POLICY "consent_records_owner_insert" ON consent_records
    FOR INSERT WITH CHECK (auth.uid()::text = user_id);

-- 11. Public Knowledge Policies (Read-Only for approved sources)
CREATE POLICY "knowledge_sources_read_approved" ON knowledge_sources
    FOR SELECT USING (is_approved = true);

CREATE POLICY "knowledge_chunks_read_approved" ON knowledge_chunks
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM knowledge_sources
            WHERE knowledge_sources.id = knowledge_chunks.source_id
            AND knowledge_sources.is_approved = true
        )
    );

CREATE POLICY "astrology_rules_read_active" ON astrology_rules
    FOR SELECT USING (is_active = true);

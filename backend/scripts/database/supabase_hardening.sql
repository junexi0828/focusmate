-- =============================================================================
-- FocusMate Supabase Security Hardening Script (RLS) - V3 Robust
-- =============================================================================
-- This script fixes all RLS issues by dynamically detecting the correct
-- user reference column (user_id, creator_id, sender_id, etc.).
-- =============================================================================

-- 1. Enable RLS for ALL tables in public schema
DO $$
DECLARE
    t TEXT;
BEGIN
    FOR t IN
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE'
    LOOP
        EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY;', t);
    END LOOP;
END $$;

-- 2. Helper Function to apply policy based on available columns
DO $$
DECLARE
    table_rec RECORD;
    found_col TEXT;
BEGIN
    -- Loop through all public tables to apply a "Private by Default" policy
    FOR table_rec IN
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE'
        AND table_name != 'alembic_version'
    LOOP
        found_col := NULL;

        -- Check for common user identifier columns in priority order
        SELECT column_name INTO found_col
        FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = table_rec.table_name
        AND column_name IN ('user_id', 'creator_id', 'sender_id', 'author_id', 'leader_id', 'user_uuid')
        ORDER BY
            CASE column_name
                WHEN 'user_id' THEN 1
                WHEN 'creator_id' THEN 2
                WHEN 'sender_id' THEN 3
                WHEN 'author_id' THEN 4
                WHEN 'leader_id' THEN 5
                ELSE 6
            END
        LIMIT 1;

        IF found_col IS NOT NULL THEN
            -- Drop existing policy if it exists
            EXECUTE format('DROP POLICY IF EXISTS "Private access" ON public.%I', table_rec.table_name);

            -- Create dynamic policy
            EXECUTE format('
                CREATE POLICY "Private access" ON public.%I
                FOR ALL USING (auth.uid()::text = %I::text)',
                table_rec.table_name, found_col);
        END IF;
    END LOOP;
END $$;

-- 3. Specific table exceptions or public tables
DO $$ BEGIN
    -- Example: Posts should be viewable by everyone, but manageable by author
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'post') THEN
        DROP POLICY IF EXISTS "Private access" ON public.post;
        CREATE POLICY "Public read, Private write" ON public.post
        FOR SELECT USING (true);
        CREATE POLICY "Author manage" ON public.post
        FOR ALL USING (auth.uid()::text = user_id::text);
    END IF;
END $$;

-- 4. Universal Safety: Service Role Bypasses RLS
-- Note: The backend uses the 'service_role' key, which automatically bypasses RLS.
-- This script ensures user-facing security without breaking backend logic.

-- =============================================================================
-- HOW TO APPLY:
-- 1. Copy ALL content.
-- 2. Run in Supabase SQL Editor.
-- 3. All matching_pools, ranking_, etc. errors will now be resolved correctly.
-- =============================================================================

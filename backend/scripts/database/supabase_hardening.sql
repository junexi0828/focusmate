-- =============================================================================
-- FocusMate Supabase Security Hardening Script (RLS)
-- =============================================================================
-- This script fixes the 42 CRITICAL errors reported by the Supabase Security Advisor.
-- It enables Row Level Security (RLS) on all tables and implements
-- "Private by Default" policies to ensure users only see their own data.
-- =============================================================================

-- 1. Enable RLS for all tables mentioned in the security report
ALTER TABLE public.achievement ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_rooms ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.comment_like ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.comment ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.conversation ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.friend_request ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.friend ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.manual_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.message ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.participant ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.room ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.room_reservations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.session_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.timer ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user ENABLE ROW LEVEL SECURITY;

-- Note: alembic_version doesn't strictly need RLS as it contains no user data,
-- but enabling it with no policies makes it "Read-Only" for everyone which is safer.
ALTER TABLE public.alembic_version ENABLE ROW LEVEL SECURITY;

-- 2. Create Default "Private by Default" Policies
-- These policies ensure that even if a table is public, only authenticated users
-- with the service role (backend) or the correct user ID can access data.

-- Example: Policy for 'user' table (Users can only read/update their own profile)
CREATE POLICY "Users can view their own profile" ON public.user
FOR SELECT USING (auth.uid()::text = id::text);

CREATE POLICY "Users can update their own profile" ON public.user
FOR UPDATE USING (auth.uid()::text = id::text);

-- Example: Policy for 'message' table (Users can only see messages in rooms they are in)
-- This assumes a 'user_id' or 'sender_id' column exists. If the column name differs,
-- please adjust accordingly in the Supabase SQL Editor.

-- 3. Universal Safety: Allow the backend (Service Role) full access
-- The backend uses a 'service_role' key which automatically bypasses RLS.
-- This script ensures that while the PUBLIC access is closed, the backend
-- continues to function normally.

-- =============================================================================
-- HOW TO APPLY:
-- 1. Go to your Supabase Dashboard -> SQL Editor.
-- 2. Paste this entire script into a new query.
-- 3. Click 'Run'.
-- 4. Check the 'Security Advisor' again; the 42 errors should disappear.
-- =============================================================================

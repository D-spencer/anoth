-- Run in Supabase SQL Editor. This updates your existing INSERT policy.
-- Assumes feedback_insert_anon is an INSERT policy, as described.
alter policy "feedback_insert_anon"
on public.feedback
to authenticated
with check (
    user_email = (select auth.jwt() ->> 'email')
);

alter table public.feedback enable row level security;

-- Keep any existing admin SELECT policy. Submission does not require SELECT
-- because the Python insert now uses returning="minimal".
-- Admin viewing needs a separate SELECT policy checked against your protected
-- user_roles table. Do not grant public SELECT access to feedback.

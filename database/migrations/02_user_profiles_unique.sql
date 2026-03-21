-- Migration: ensure user_profiles.user_id has a UNIQUE constraint
-- Safe to run multiple times

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'user_profiles_user_id_key'
          AND conrelid = 'user_profiles'::regclass
    ) THEN
        ALTER TABLE user_profiles ADD CONSTRAINT user_profiles_user_id_key UNIQUE (user_id);
    END IF;
END;
$$;

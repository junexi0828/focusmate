-- Add missing columns to user table
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS school VARCHAR(100);
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS bio VARCHAR(500);
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS profile_image VARCHAR(500);

-- Verify columns
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'user'
ORDER BY ordinal_position;

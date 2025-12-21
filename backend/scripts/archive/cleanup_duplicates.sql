-- SQL script to clean up duplicate teams
-- This keeps only the oldest team for each team name

-- Step 1: View duplicate teams
SELECT team_name, COUNT(*) as count,
       STRING_AGG(team_id::text, ', ') as team_ids,
       MIN(created_at) as oldest_created
FROM ranking_teams
GROUP BY team_name
HAVING COUNT(*) > 1;

-- Step 2: Delete team members of duplicate teams (except the oldest one)
WITH duplicates AS (
    SELECT team_id, team_name,
           ROW_NUMBER() OVER (PARTITION BY team_name ORDER BY created_at ASC) as rn
    FROM ranking_teams
)
DELETE FROM ranking_team_members
WHERE team_id IN (
    SELECT team_id FROM duplicates WHERE rn > 1
);

-- Step 3: Delete team invitations of duplicate teams
WITH duplicates AS (
    SELECT team_id, team_name,
           ROW_NUMBER() OVER (PARTITION BY team_name ORDER BY created_at ASC) as rn
    FROM ranking_teams
)
DELETE FROM ranking_team_invitations
WHERE team_id IN (
    SELECT team_id FROM duplicates WHERE rn > 1
);

-- Step 4: Delete verification requests of duplicate teams
WITH duplicates AS (
    SELECT team_id, team_name,
           ROW_NUMBER() OVER (PARTITION BY team_name ORDER BY created_at ASC) as rn
    FROM ranking_teams
)
DELETE FROM ranking_verification_requests
WHERE team_id IN (
    SELECT team_id FROM duplicates WHERE rn > 1
);

-- Step 5: Delete duplicate teams (keep only the oldest)
WITH duplicates AS (
    SELECT team_id, team_name,
           ROW_NUMBER() OVER (PARTITION BY team_name ORDER BY created_at ASC) as rn
    FROM ranking_teams
)
DELETE FROM ranking_teams
WHERE team_id IN (
    SELECT team_id FROM duplicates WHERE rn > 1
);

-- Step 6: Verify cleanup
SELECT team_name, COUNT(*) as count
FROM ranking_teams
GROUP BY team_name
ORDER BY team_name;

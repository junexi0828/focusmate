"""Cleanup duplicate team data in the database.

This script removes duplicate teams, keeping only the first instance of each team name.
Run with: python scripts/cleanup_duplicate_teams.py
"""

import asyncio
import sys
from pathlib import Path
from collections import defaultdict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.infrastructure.database.session import get_db
from app.infrastructure.database.models.ranking import RankingTeam, RankingTeamMember
from sqlalchemy import select, delete


async def cleanup_duplicate_teams():
    """Remove duplicate teams from database."""
    print("🧹 Starting duplicate team cleanup...")

    async for db in get_db():
        try:
            # Get all teams
            result = await db.execute(select(RankingTeam))
            all_teams = result.scalars().all()

            print(f"\n📊 Found {len(all_teams)} total teams")

            # Group teams by name
            teams_by_name = defaultdict(list)
            for team in all_teams:
                teams_by_name[team.team_name].append(team)

            # Find duplicates
            duplicates_found = 0
            teams_to_delete = []

            for team_name, teams in teams_by_name.items():
                if len(teams) > 1:
                    print(f"\n⚠️  Found {len(teams)} duplicates of '{team_name}'")
                    duplicates_found += len(teams) - 1

                    # Keep the first team (oldest), delete others
                    teams_sorted = sorted(teams, key=lambda t: t.created_at)
                    keep_team = teams_sorted[0]
                    delete_teams = teams_sorted[1:]

                    print(f"   ✅ Keeping team ID: {keep_team.team_id} (created {keep_team.created_at})")

                    for team in delete_teams:
                        print(f"   🗑️  Deleting team ID: {team.team_id} (created {team.created_at})")
                        teams_to_delete.append(team.team_id)

            if duplicates_found == 0:
                print("\n✅ No duplicate teams found!")
                return

            print(f"\n📝 Summary:")
            print(f"   Total teams: {len(all_teams)}")
            print(f"   Unique teams: {len(teams_by_name)}")
            print(f"   Duplicates to remove: {duplicates_found}")

            # Confirm deletion
            print(f"\n⚠️  This will delete {duplicates_found} duplicate teams.")
            confirm = input("   Continue? (yes/no): ")

            if confirm.lower() != "yes":
                print("❌ Cleanup cancelled")
                return

            # Delete team members first (foreign key constraint)
            print("\n🗑️  Deleting team members of duplicate teams...")
            for team_id in teams_to_delete:
                await db.execute(
                    delete(RankingTeamMember).where(
                        RankingTeamMember.team_id == team_id
                    )
                )

            # Delete duplicate teams
            print("🗑️  Deleting duplicate teams...")
            for team_id in teams_to_delete:
                await db.execute(
                    delete(RankingTeam).where(RankingTeam.team_id == team_id)
                )

            await db.commit()

            print(f"\n✅ Cleanup complete!")
            print(f"   Removed {duplicates_found} duplicate teams")
            print(f"   Remaining teams: {len(teams_by_name)}")

            # Show remaining teams
            print("\n📋 Remaining teams:")
            for team_name, teams in teams_by_name.items():
                print(f"   - {team_name} (ID: {teams[0].team_id})")

        except Exception as e:
            print(f"\n❌ Error during cleanup: {e}")
            await db.rollback()
            raise
        finally:
            await db.close()
            break


if __name__ == "__main__":
    asyncio.run(cleanup_duplicate_teams())

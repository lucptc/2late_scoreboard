import os


CTFD_URL = os.getenv("CTFD_URL", "http://10.5.8.2")
CTFD_TOKEN = os.getenv("CTFD_TOKEN", "REDACTED")

SCORING_ENGINE_URL = os.getenv(
    "SCORING_ENGINE_URL",
    "https://10.5.8.43",
)


# Map Scoring Engine player/team identifiers to CTFd team names.
#
# The key must match whatever identifier Scoring Engine returns
# for an individual blue-team participant.
PLAYER_TO_TEAM = {
    "alice": "Team Alpha",
    "bob": "Team Alpha",
    "charlie": "Team Beta",
    "dave": "Team Beta",
}


# How often the browser asks the central scoreboard for fresh data.
POLL_SECONDS = 10

from dataclasses import dataclass
import httpx

from config import (
    CTFD_URL,
    CTFD_TOKEN,
    SCORING_ENGINE_URL,
    PLAYER_TO_TEAM,
)


@dataclass
class TeamScore:
    name: str
    ctf: int = 0
    blue: int = 0

    @property
    def total(self):
        return self.ctf + self.blue


async def get_ctfd_scores():
    headers = {}

    if CTFD_TOKEN:
        headers["Authorization"] = f"Token {CTFD_TOKEN}"

    url = f"{CTFD_URL.rstrip('/')}/api/v1/scoreboard"

    async with httpx.AsyncClient(timeout=5) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

    teams = {}

    for entry in data.get("data", []):
        name = entry["name"]

        teams[name] = TeamScore(
            name=name,
            ctf=int(entry.get("score", 0)),
        )

    return teams


async def get_scoring_engine_scores():
    url = (
        f"{SCORING_ENGINE_URL.rstrip('/')}"
        "/api/scoreboard/get_bar_data"
    )

    async with httpx.AsyncClient(timeout=5, verify=False) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


def parse_scoring_engine_scores(data):
    """
    Convert Scoring Engine's response into:

        {
            "alice": 430,
            "bob": 510,
        }

    This is the one function you may need to adjust depending
    on the exact JSON produced by your Scoring Engine deployment.
    """

    scores = {}

    # TODO:
    #
    # Adapt this to your Scoring Engine response.
    #
    # The expected result of this function is simply:
    #
    #   player_identifier -> score
    #
    # For example:
    #
    # scores["alice"] = 430
    # scores["bob"] = 510

    labels = data.get("labels", [])
    scores = data.get("adjusted_scores", [])

    if len(labels) != len(scores):
        raise ValueError(
            "Scoring Engine returned mismatched labels and scores"
        )

    result = {}
    
    for label, score in zip(labels, scores):
        if score == "@":
            score = 0

        result[label] = int(score)

    return result


async def get_final_scores():
    ctfd_task = get_ctfd_scores()
    scoring_task = get_scoring_engine_scores()

    ctfd_scores, scoring_data = await __import__(
        "asyncio"
    ).gather(
        ctfd_task,
        scoring_task,
    )

    blue_scores = parse_scoring_engine_scores(scoring_data)

    # Start with every CTFd team.
    teams = dict(ctfd_scores)

    # Add blue-team scores to their mapped CTF team.
    for player, score in blue_scores.items():
        team_name = PLAYER_TO_TEAM.get(player)

        if team_name is None:
            # Player hasn't been mapped yet.
            continue

        if team_name not in teams:
            teams[team_name] = TeamScore(name=team_name)

        teams[team_name].blue += score

    return sorted(
        teams.values(),
        key=lambda team: team.total,
        reverse=True,
    )

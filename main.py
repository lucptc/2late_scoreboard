from fasthtml.common import *
from datetime import datetime, timezone

from config import POLL_SECONDS
from scoring import get_final_scores


app, rt = fast_app(
    hdrs=(
        Link(rel="stylesheet", href="/static/style.css"),
    )
)


def score_table(scores):
    rows = []

    for position, team in enumerate(scores, start=1):
        rows.append(
            Tr(
                Td(position, cls="position"),
                Td(team.name, cls="team-name"),
                Td(f"{team.ctf:,}", cls="score ctf"),
                Td(f"{team.blue:,}", cls="score blue"),
                Td(
                    f"{team.total:,}",
                    cls="score total",
                ),
            )
        )

    return Table(
        Thead(
            Tr(
                Th("#"),
                Th("Team"),
                Th("CTF"),
                Th("Blue"),
                Th("Total"),
            )
        ),
        Tbody(*rows),
        cls="scoreboard",
    )


async def scoreboard_fragment():
    try:
        scores = await get_final_scores()

        now = datetime.now(timezone.utc).strftime(
            "%H:%M:%S UTC"
        )

        return Div(
            Div(
                Span(
                    "LIVE",
                    cls="live-indicator",
                ),
                Span(
                    f"Updated {now}",
                    cls="updated",
                ),
                cls="status",
            ),
            score_table(scores),
            cls="scoreboard-container",
            id="scoreboard",
            hx_get="/scores",
            hx_trigger=f"every {POLL_SECONDS}s",
            hx_swap="outerHTML",
        )

    except Exception as exc:
        return Div(
            Div(
                Span(
                    "ERROR",
                    cls="error-indicator",
                ),
                Span(
                    "Unable to retrieve scores",
                    cls="updated",
                ),
                cls="status",
            ),
            P(
                str(exc),
                cls="error-message",
            ),
            cls="scoreboard-container",
            id="scoreboard",
            hx_get="/scores",
            hx_trigger=f"every {POLL_SECONDS}s",
            hx_swap="outerHTML",
        )


@rt("/")
async def get():
    return (
        Title("OSS Rankings"),
        Main(
            Header(
                H1("OSS Rankings"),
                P(
                    "Official Scoreboard",
                    cls="subtitle",
                ),
            ),

            Div(
                Div(
                    Span("CTF", cls="legend-label"),
                    Span("Blue Team", cls="legend-label"),
                    Span("Total", cls="legend-label"),
                    cls="legend",
                ),

                await scoreboard_fragment(),
                cls="container",
            ),
        ),
    )


@rt("/scores")
async def scores():
    return await scoreboard_fragment()


serve()
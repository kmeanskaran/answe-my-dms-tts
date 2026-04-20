from __future__ import annotations

from smallestai.atoms.agent.server import AtomsApp
from smallestai.atoms.agent.session import AgentSession

from .config import load_settings
from .dm_agent import DMReplyAgent


async def on_start(session: AgentSession):
    settings = load_settings()
    session.add_node(DMReplyAgent(settings))
    await session.start()
    await session.wait_until_complete()


def run() -> None:
    app = AtomsApp(setup_handler=on_start)
    app.run()


if __name__ == "__main__":
    run()

from __future__ import annotations

from threading import Lock

from .models import Game


class GameStore:
    def __init__(self) -> None:
        self._games: dict[str, Game] = {}
        self._lock = Lock()

    def save(self, game: Game) -> None:
        with self._lock:
            self._games[game.id] = game

    def get(self, game_id: str) -> Game | None:
        return self._games.get(game_id)


store = GameStore()


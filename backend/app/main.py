from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .cases import generate_case
from .engine import handle_action
from .models import AccusationRequest, AccusationResponse, ActionRequest, ActionResponse, Game, Message
from .store import store

app = FastAPI(title="ARGUS Investigation API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


def _game(game_id: str) -> Game:
    game = store.get(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game


def _public(game: Game) -> dict:
    data = game.model_dump()
    data.pop("culprit_id", None)
    data.pop("solution", None)
    for item in data["evidence"]:
        item.pop("implicates", None)
    return data


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/games")
def create_game(seed: int | None = None) -> dict:
    game = generate_case(seed)
    store.save(game)
    return _public(game)


@app.get("/api/games/{game_id}")
def get_game(game_id: str) -> dict:
    return _public(_game(game_id))


@app.post("/api/games/{game_id}/actions", response_model=ActionResponse)
def action(game_id: str, payload: ActionRequest) -> ActionResponse:
    game = _game(game_id)
    if game.status != "investigating":
        raise HTTPException(status_code=409, detail="This investigation is closed")
    response = handle_action(game, payload.text, payload.npc_id)
    game.messages.extend([Message(speaker="Detective", text=payload.text, agent="Player"), Message(speaker="ARGUS", text=response.reply, agent=response.agent)])
    store.save(game)
    return response


@app.post("/api/games/{game_id}/accusations", response_model=AccusationResponse)
def accuse(game_id: str, payload: AccusationRequest) -> AccusationResponse:
    game = _game(game_id)
    discovered = {item.id for item in game.evidence if item.discovered}
    valid_selected = discovered & set(payload.evidence_ids)
    correct = payload.suspect_id == game.culprit_id
    culprit_evidence = {item.id for item in game.evidence if game.culprit_id in item.implicates}
    support = len(valid_selected & culprit_evidence)
    score = min(100, (55 if correct else 5) + support * 15 + min(15, len(payload.reasoning.split()) // 4))
    game.status = "solved" if correct else "failed"
    verdict = "Case solved. Your suspect and evidence align with the hidden timeline." if correct else "The accusation does not fit the complete evidence trail."
    store.save(game)
    return AccusationResponse(correct=correct, score=score, verdict=verdict, solution=game.solution)


from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_full_investigation_flow() -> None:
    created = client.post("/api/games?seed=1")
    assert created.status_code == 200
    game = created.json()
    assert "culprit_id" not in game

    cctv = client.post(f"/api/games/{game['id']}/actions", json={"text": "Check CCTV and service lift"})
    assert cctv.status_code == 200
    assert cctv.json()["agent"].endswith("CCTV Tool")

    npc = game["npcs"][0]
    answer = client.post(f"/api/games/{game['id']}/actions", json={"text": "Where were you at 10?", "npc_id": npc["id"]})
    assert answer.status_code == 200
    assert answer.json()["retrieved_memories"]


def test_unknown_game_is_404() -> None:
    assert client.get("/api/games/missing").status_code == 404


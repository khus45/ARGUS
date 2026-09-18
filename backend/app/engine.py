from __future__ import annotations

import re

from .models import ActionResponse, Evidence, Game


STOPWORDS = {"the", "a", "an", "at", "is", "was", "were", "you", "your", "i", "me", "to", "of", "in", "on", "and", "what", "where", "when", "did", "do", "check", "please"}


def _tokens(text: str) -> set[str]:
    return {word for word in re.findall(r"[a-z0-9:]+", text.lower()) if word not in STOPWORDS}


def retrieve_memories(game: Game, npc_id: str, question: str, limit: int = 2) -> list[str]:
    npc = next((item for item in game.npcs if item.id == npc_id), None)
    if not npc:
        return []
    query = _tokens(question)
    ranked: list[tuple[int, str]] = []
    for memory in npc.memories:
        if memory.hidden:
            continue
        haystack = _tokens(memory.text) | set(memory.keywords)
        score = len(query & haystack)
        ranked.append((score, memory.text))
    ranked.sort(key=lambda item: item[0], reverse=True)
    relevant = [text for score, text in ranked if score > 0][:limit]
    return relevant or [ranked[0][1]]


def _npc_reply(game: Game, npc_id: str, question: str) -> ActionResponse:
    npc = next((item for item in game.npcs if item.id == npc_id), None)
    if not npc:
        return ActionResponse(reply="That person is not part of this case.", agent="Supervisor")
    memories = retrieve_memories(game, npc_id, question)
    prefix = ""
    if npc.personality.fear > 65:
        prefix = "I... I will tell you what I remember. "
    elif npc.personality.confidence > 75:
        prefix = "I've already been clear. "
    reply = prefix + " ".join(memories)
    return ActionResponse(reply=reply, agent=f"NPC Agent · {npc.name}", retrieved_memories=memories)


def _discover(game: Game, kinds: set[str], location_words: set[str]) -> list[Evidence]:
    found: list[Evidence] = []
    for evidence in game.evidence:
        kind_match = evidence.kind.lower() in kinds or any(kind in evidence.kind.lower() for kind in kinds)
        location_match = bool(location_words & _tokens(evidence.location + " " + evidence.title))
        if not evidence.discovered and (kind_match or location_match):
            evidence.discovered = True
            found.append(evidence)
    return found[:2]


def handle_action(game: Game, text: str, npc_id: str | None) -> ActionResponse:
    lowered = text.lower()
    if npc_id:
        return _npc_reply(game, npc_id, text)

    if any(word in lowered for word in ("cctv", "camera", "footage")):
        found = _discover(game, {"cctv"}, _tokens(text))
        reply = "CCTV search complete. " + (" ".join(item.description for item in found) if found else "No new relevant footage was found.")
        return ActionResponse(reply=reply, agent="Supervisor → Evidence Agent → CCTV Tool", new_evidence=found)
    if any(word in lowered for word in ("fingerprint", "forensic", "fiber", "weapon")):
        found = _discover(game, {"fingerprint", "forensics"}, _tokens(text))
        reply = "Forensic analysis complete. " + (" ".join(item.description for item in found) if found else "There is no unprocessed forensic match.")
        return ActionResponse(reply=reply, agent="Supervisor → Evidence Agent → Forensics Tool", new_evidence=found)
    if any(word in lowered for word in ("record", "document", "ledger", "report", "safe", "office")):
        found = _discover(game, {"document"}, _tokens(text))
        reply = "Records search complete. " + (" ".join(item.description for item in found) if found else "No new record matched the query.")
        return ActionResponse(reply=reply, agent="Supervisor → Police Agent → Records Tool", new_evidence=found)
    if any(word in lowered for word in ("receipt", "restaurant", "alibi")):
        found = _discover(game, {"receipt"}, _tokens(text))
        reply = "Alibi check complete. " + (" ".join(item.description for item in found) if found else "No additional alibi record was found.")
        return ActionResponse(reply=reply, agent="Supervisor → Detective Agent → Location Tool", new_evidence=found)
    return ActionResponse(reply="Choose a person to question, or ask me to check CCTV, fingerprints, records, documents, or an alibi.", agent="Supervisor Agent")


from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class Personality(BaseModel):
    confidence: int = Field(ge=0, le=100)
    fear: int = Field(ge=0, le=100)
    trust: int = Field(ge=0, le=100)
    aggression: int = Field(ge=0, le=100)


class Memory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    text: str
    keywords: list[str] = Field(default_factory=list)
    hidden: bool = False


class NPC(BaseModel):
    id: str
    name: str
    role: str
    relationship: str
    personality: Personality
    memories: list[Memory]


class Evidence(BaseModel):
    id: str
    kind: str
    title: str
    description: str
    location: str
    discovered: bool = False
    implicates: list[str] = Field(default_factory=list)


class CaseFile(BaseModel):
    number: str
    title: str
    victim: str
    location: str
    crime_time: str
    summary: str


class Message(BaseModel):
    speaker: str
    text: str
    agent: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Game(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    case: CaseFile
    npcs: list[NPC]
    evidence: list[Evidence]
    culprit_id: str
    solution: str
    messages: list[Message] = Field(default_factory=list)
    visited_locations: list[str] = Field(default_factory=list)
    status: Literal["investigating", "solved", "failed"] = "investigating"


class ActionRequest(BaseModel):
    text: str = Field(min_length=1, max_length=800)
    npc_id: str | None = None


class ActionResponse(BaseModel):
    reply: str
    agent: str
    retrieved_memories: list[str] = Field(default_factory=list)
    new_evidence: list[Evidence] = Field(default_factory=list)


class AccusationRequest(BaseModel):
    suspect_id: str
    reasoning: str = Field(min_length=5, max_length=1500)
    evidence_ids: list[str] = Field(default_factory=list)


class AccusationResponse(BaseModel):
    correct: bool
    score: int
    verdict: str
    solution: str


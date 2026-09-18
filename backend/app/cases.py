from __future__ import annotations

import random

from .models import CaseFile, Evidence, Game, Memory, NPC, Personality


def _memory(text: str, *keywords: str, hidden: bool = False) -> Memory:
    return Memory(text=text, keywords=list(keywords), hidden=hidden)


def generate_case(seed: int | None = None) -> Game:
    rng = random.Random(seed)
    variants = [_hotel_case, _gallery_case]
    return rng.choice(variants)()


def _hotel_case() -> Game:
    npcs = [
        NPC(
            id="john",
            name="John Hale",
            role="Suspect",
            relationship="Victim's business partner",
            personality=Personality(confidence=82, fear=28, trust=35, aggression=38),
            memories=[
                _memory("At 9:00 PM I met Sarah in the hotel bar.", "9", "nine", "sarah", "bar"),
                _memory("I claim I was at the restaurant from 10:00 PM until midnight.", "10", "ten", "restaurant", "alibi"),
                _memory("Alex and I argued about missing company money that afternoon.", "alex", "argument", "money", "motive"),
                _memory("I briefly went upstairs using the service lift at 10:42 PM.", "lift", "upstairs", "10:42", hidden=True),
            ],
        ),
        NPC(
            id="sarah",
            name="Sarah Lin",
            role="Witness",
            relationship="Victim's employee",
            personality=Personality(confidence=42, fear=78, trust=70, aggression=8),
            memories=[
                _memory("I met John in the bar at 9:00 PM; he left before 9:30.", "john", "bar", "9", "left"),
                _memory("At about 10:45 PM I heard the service lift stop on the third floor.", "10:45", "lift", "third", "sound"),
                _memory("Alex told me he had proof that someone was stealing from the company.", "alex", "proof", "stealing", "money"),
            ],
        ),
        NPC(
            id="robert",
            name="Robert Shaw",
            role="Security",
            relationship="Hotel security guard",
            personality=Personality(confidence=65, fear=35, trust=62, aggression=22),
            memories=[
                _memory("The main third-floor camera lost signal between 10:35 and 10:55 PM.", "camera", "cctv", "signal", "10:35"),
                _memory("The service-lift camera was on a separate circuit and kept recording.", "service", "lift", "camera", "recording"),
                _memory("Only staff and senior guests can use the service lift keycard.", "keycard", "lift", "access"),
            ],
        ),
    ]
    evidence = [
        Evidence(id="cctv-lift", kind="CCTV", title="Service lift footage", description="John enters the service lift at 10:42 PM and exits on floor three.", location="Security room", implicates=["john"]),
        Evidence(id="fingerprint", kind="Fingerprint", title="Print on room door", description="A partial print on Room 302's inside door handle matches John Hale.", location="Room 302", implicates=["john"]),
        Evidence(id="ledger", kind="Document", title="Fraud ledger", description="Alex's ledger documents transfers to an account controlled by John.", location="Room 302 safe", implicates=["john"]),
        Evidence(id="receipt", kind="Receipt", title="Restaurant receipt", description="John's receipt is timestamped 9:48 PM, not near the crime time.", location="Hotel restaurant", implicates=["john"]),
    ]
    return Game(
        case=CaseFile(number="ARG-001", title="The Room 302 Murder", victim="Alex Morgan", location="Aurora Hotel, Room 302", crime_time="Approximately 10:50 PM", summary="Alex Morgan was found dead in a locked hotel room. The corridor camera conveniently failed."),
        npcs=npcs,
        evidence=evidence,
        culprit_id="john",
        solution="John stole company funds. Alex summoned him with the ledger as leverage. John used the service lift, killed Alex during the confrontation, and staged the room before returning downstairs.",
    )


def _gallery_case() -> Game:
    npcs = [
        NPC(id="maya", name="Maya Roy", role="Suspect", relationship="Gallery curator", personality=Personality(confidence=74, fear=34, trust=55, aggression=18), memories=[_memory("I was cataloguing paintings in the west archive at 8:00 PM.", "8", "archive", "painting"), _memory("The victim planned to expose a forged painting after the gala.", "forged", "painting", "expose"), _memory("I know the archive alarm code because I manage the collection.", "alarm", "code", "archive")]),
        NPC(id="dev", name="Dev Mehta", role="Suspect", relationship="Art dealer", personality=Personality(confidence=88, fear=20, trust=25, aggression=44), memories=[_memory("I left the gala at 7:45 PM for a client call.", "7:45", "left", "call"), _memory("Maya and the victim argued about the Vermeer attribution.", "maya", "argument", "vermeer")]),
        NPC(id="ina", name="Ina Bose", role="Witness", relationship="Catering manager", personality=Personality(confidence=51, fear=45, trust=76, aggression=5), memories=[_memory("I saw Maya near the archive at 8:12 PM carrying a conservation case.", "maya", "8:12", "archive", "case"), _memory("The fire door alarm chirped once around 8:20 PM.", "alarm", "8:20", "door")]),
    ]
    evidence = [
        Evidence(id="alarm-log", kind="Access log", title="Archive alarm log", description="Maya's code disabled the archive alarm at 8:09 PM.", location="Security console", implicates=["maya"]),
        Evidence(id="fiber", kind="Forensics", title="Conservation fiber", description="Fiber from Maya's conservation case was found on the weapon.", location="West archive", implicates=["maya"]),
        Evidence(id="forgery", kind="Document", title="Forgery report", description="The victim's report proves Maya authenticated a valuable forgery.", location="Victim's office", implicates=["maya"]),
    ]
    return Game(case=CaseFile(number="ARG-002", title="The Silent Gallery", victim="Rohan Vale", location="Aster Modern Gallery", crime_time="Approximately 8:20 PM", summary="A critic was killed beside a forged masterpiece while the gala continued one room away."), npcs=npcs, evidence=evidence, culprit_id="maya", solution="Maya killed Rohan to prevent him revealing that she knowingly authenticated a forgery. Her alarm code, conservation-case fiber, and the hidden report establish access, means, and motive.")


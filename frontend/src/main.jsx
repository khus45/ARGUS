import React, { useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API = import.meta.env.VITE_API_URL || (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1" ? "http://localhost:8000" : "");
const OFFLINE_CASE = {
  id: "offline-arg-001",
  case: { number: "ARG-001", title: "The Room 302 Murder", victim: "Alex Morgan", location: "Aurora Hotel, Room 302", crime_time: "Approximately 10:50 PM", summary: "Alex Morgan was found dead in a locked hotel room. The corridor camera conveniently failed." },
  npcs: [
    { id: "john", name: "John Hale", role: "Suspect", relationship: "Victim's business partner" },
    { id: "sarah", name: "Sarah Lin", role: "Witness", relationship: "Victim's employee" },
    { id: "robert", name: "Robert Shaw", role: "Security", relationship: "Hotel security guard" },
  ],
  evidence: [
    { id: "cctv-lift", kind: "CCTV", title: "Service lift footage", description: "John enters the service lift at 10:42 PM and exits on floor three.", location: "Security room", discovered: false },
    { id: "fingerprint", kind: "Fingerprint", title: "Print on room door", description: "A partial print on Room 302's inside door handle matches John Hale.", location: "Room 302", discovered: false },
    { id: "ledger", kind: "Document", title: "Fraud ledger", description: "Alex's ledger documents transfers to an account controlled by John.", location: "Room 302 safe", discovered: false },
  ],
};

function App() {
  const [game, setGame] = useState(null);
  const [selectedNpc, setSelectedNpc] = useState(null);
  const [query, setQuery] = useState("");
  const [feed, setFeed] = useState([]);
  const [busy, setBusy] = useState(false);
  const [theory, setTheory] = useState("");
  const [accused, setAccused] = useState("");
  const [pickedEvidence, setPickedEvidence] = useState([]);
  const [result, setResult] = useState(null);
  const [musicOn, setMusicOn] = useState(false);
  const [offlineMode, setOfflineMode] = useState(false);
  const musicRef = useRef({ ctx: null, master: null, drones: [], timer: null });

  const discovered = useMemo(() => game?.evidence.filter((item) => item.discovered) || [], [game]);

  async function newCase() {
    setBusy(true);
    let data;
    try {
      const response = await fetch(`${API}/api/games`, { method: "POST" });
      if (!response.ok) throw new Error(`API ${response.status}`);
      data = await response.json();
      setOfflineMode(false);
    } catch {
      data = JSON.parse(JSON.stringify(OFFLINE_CASE));
      setOfflineMode(true);
    }
    setGame(data); setSelectedNpc(null); setFeed([{ who: "ARGUS", text: data.case.summary, agent: "Case Generator" }]); setResult(null); setPickedEvidence([]); setTheory(""); setAccused(""); setBusy(false);
  }

  useEffect(() => { newCase(); }, []);

  function toggleMusic() {
    const current = musicRef.current;
    if (current.ctx) {
      window.clearInterval(current.timer);
      current.drones.forEach((node) => { try { node.stop(); } catch { /* already stopped */ } });
      current.ctx.close();
      musicRef.current = { ctx: null, master: null, drones: [], timer: null };
      setMusicOn(false);
      return;
    }
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) return;
    const ctx = new AudioContext();
    const master = ctx.createGain();
    master.gain.value = 0.045;
    const filter = ctx.createBiquadFilter();
    filter.type = "lowpass";
    filter.frequency.value = 1150;
    master.connect(filter).connect(ctx.destination);
    const drones = [110, 130.81, 164.81].map((frequency, index) => {
      const oscillator = ctx.createOscillator();
      oscillator.type = index === 1 ? "triangle" : "sine";
      oscillator.frequency.value = frequency;
      oscillator.detune.value = index * 4 - 4;
      oscillator.connect(master);
      oscillator.start();
      return oscillator;
    });
    const playMotif = () => {
      const note = ctx.createOscillator();
      const envelope = ctx.createGain();
      note.type = "sine";
      note.frequency.value = [329.63, 392, 293.66, 261.63][Math.floor(Date.now() / 2200) % 4];
      envelope.gain.setValueAtTime(0, ctx.currentTime);
      envelope.gain.linearRampToValueAtTime(0.11, ctx.currentTime + 0.08);
      envelope.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 1.6);
      note.connect(envelope).connect(master);
      note.start();
      note.stop(ctx.currentTime + 1.7);
    };
    playMotif();
    const timer = window.setInterval(playMotif, 2200);
    musicRef.current = { ctx, master, drones, timer };
    setMusicOn(true);
  }

  useEffect(() => () => {
    const current = musicRef.current;
    window.clearInterval(current.timer);
    current.drones.forEach((node) => { try { node.stop(); } catch { /* already stopped */ } });
    if (current.ctx) current.ctx.close();
  }, []);

  async function refresh() {
    const response = await fetch(`${API}/api/games/${game.id}`);
    setGame(await response.json());
  }

  async function send(text = query) {
    if (!text.trim() || busy) return;
    setBusy(true); setQuery("");
    setFeed((old) => [...old, { who: "YOU", text }]);
    if (game.id === "offline-arg-001") {
      const lowered = text.toLowerCase();
      let reply = "The local case engine is ready. Question a suspect or choose an investigation tool.";
      let agent = "Local Supervisor Agent";
      let foundId = null;
      if (selectedNpc === "john") { reply = "I was at the restaurant from 10:00 PM until midnight. I briefly used the service lift at 10:42 PM."; agent = "Local NPC Agent · John Hale"; }
      else if (selectedNpc === "sarah") { reply = "I met John in the bar at 9:00 PM. Around 10:45 PM I heard the service lift stop on the third floor."; agent = "Local NPC Agent · Sarah Lin"; }
      else if (selectedNpc === "robert") { reply = "The main third-floor camera lost signal, but the separate service-lift camera kept recording."; agent = "Local NPC Agent · Robert Shaw"; }
      else if (lowered.includes("cctv") || lowered.includes("camera") || lowered.includes("footage")) { reply = "CCTV search complete. John enters the service lift at 10:42 PM and exits on floor three."; agent = "Local Supervisor → CCTV Tool"; foundId = "cctv-lift"; }
      else if (lowered.includes("finger") || lowered.includes("forensic")) { reply = "Forensic analysis complete. A partial fingerprint on Room 302 matches John Hale."; agent = "Local Supervisor → Forensics Tool"; foundId = "fingerprint"; }
      else if (lowered.includes("record") || lowered.includes("ledger") || lowered.includes("document")) { reply = "Records search complete. Alex's ledger documents transfers to John's account."; agent = "Local Supervisor → Records Tool"; foundId = "ledger"; }
      if (foundId) setGame((old) => ({ ...old, evidence: old.evidence.map((item) => item.id === foundId ? { ...item, discovered: true } : item) }));
      setFeed((old) => [...old, { who: "ARGUS", text: reply, agent }]);
      setBusy(false);
      return;
    }
    try {
      const response = await fetch(`${API}/api/games/${game.id}/actions`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text, npc_id: selectedNpc }) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Action failed");
      setFeed((old) => [...old, { who: "ARGUS", text: data.reply, agent: data.agent }]);
      await refresh();
    } catch (error) { setFeed((old) => [...old, { who: "SYSTEM", text: error.message }]); }
    setBusy(false);
  }

  async function submitAccusation() {
    if (!accused || theory.trim().length < 5) return;
    setBusy(true);
    if (game.id === "offline-arg-001") {
      setResult({ correct: accused === "john", score: accused === "john" ? 100 : 5, verdict: accused === "john" ? "Case solved. Your suspect and evidence align with the hidden timeline." : "The accusation does not fit the complete evidence trail.", solution: "John used the service lift, confronted Alex over the stolen company funds, and staged the room." });
      setBusy(false);
      return;
    }
    const response = await fetch(`${API}/api/games/${game.id}/accusations`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ suspect_id: accused, reasoning: theory, evidence_ids: pickedEvidence }) });
    setResult(await response.json()); setBusy(false);
  }

  if (!game) return <main className="loading">ARGUS is generating a case…</main>;

  return <main className="app-shell">
    <div className="ambient-orb orb-one" /><div className="ambient-orb orb-two" />
    <header><div className="brand-lockup"><span className="brand-mark">◈</span><div><span className="eyebrow">AI INVESTIGATION NETWORK</span><h1>ARGUS<span> / {game.case.number}</span></h1></div></div><div className="header-actions"><button className={`music-toggle ${musicOn ? "on" : ""}`} onClick={toggleMusic} aria-label="Toggle noir ambient music"><span>{musicOn ? "♫" : "♩"}</span>{musicOn ? "NOIR AUDIO ON" : "PLAY NOIR AUDIO"}</button><button className="secondary" onClick={newCase}>Generate new case</button></div></header>
    <section className="case-banner"><div className="case-copy"><span className="status">● {offlineMode ? "LOCAL DEMO ENGINE" : "LIVE CASE"} <i>· ARCHIVE 01</i></span><h2>{game.case.title}</h2><p>{game.case.victim} · {game.case.location} · {game.case.crime_time}</p><div className="case-stamp">CONFIDENTIAL <span>ARGUS FIELD UNIT</span></div></div><div className="metric"><div className="metric-ring"><strong>{discovered.length}/{game.evidence.length}</strong></div><span>evidence found</span></div></section>
    <div className="grid">
      <aside className="panel"><h3>PEOPLE OF INTEREST</h3>{game.npcs.map((npc) => <button key={npc.id} className={`npc ${selectedNpc === npc.id ? "active" : ""}`} onClick={() => setSelectedNpc(selectedNpc === npc.id ? null : npc.id)}><span className="avatar">{npc.name.split(" ").map((p) => p[0]).join("")}</span><span><strong>{npc.name}</strong><small>{npc.role} · {npc.relationship}</small></span></button>)}<div className="hint">Select a person, then question them. Deselect to use investigation tools.</div></aside>
      <section className="panel console"><div className="console-head"><h3>{selectedNpc ? `INTERVIEW · ${game.npcs.find((n) => n.id === selectedNpc)?.name}` : "SUPERVISOR CONSOLE"}</h3><span>{busy ? "PROCESSING" : "READY"}</span></div><div className="feed">{feed.map((entry, index) => <article key={index} className={entry.who === "YOU" ? "player" : "agent"}><div><b>{entry.who}</b>{entry.agent && <em>{entry.agent}</em>}</div><p>{entry.text}</p></article>)}</div><div className="quick"><button onClick={() => send("Check CCTV around the crime scene")}>Check CCTV</button><button onClick={() => send("Run fingerprint and forensic analysis")}>Forensics</button><button onClick={() => send("Search records and hidden documents")}>Search records</button></div><form onSubmit={(e) => { e.preventDefault(); send(); }}><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder={selectedNpc ? "Ask a precise question…" : "Order an investigation tool…"}/><button disabled={busy}>SEND</button></form></section>
      <aside className="panel"><h3>EVIDENCE BOARD</h3>{discovered.length === 0 && <div className="empty">No evidence collected yet. Use the supervisor tools.</div>}{discovered.map((item) => <label className="evidence" key={item.id}><input type="checkbox" checked={pickedEvidence.includes(item.id)} onChange={() => setPickedEvidence((old) => old.includes(item.id) ? old.filter((id) => id !== item.id) : [...old, item.id])}/><span><small>{item.kind}</small><strong>{item.title}</strong><p>{item.description}</p></span></label>)}</aside>
    </div>
    <section className="panel accusation"><div><span className="eyebrow">FINAL ANALYSIS</span><h2>Build your accusation</h2></div><select value={accused} onChange={(e) => setAccused(e.target.value)}><option value="">Choose suspect</option>{game.npcs.filter((n) => n.role === "Suspect").map((npc) => <option key={npc.id} value={npc.id}>{npc.name}</option>)}</select><textarea value={theory} onChange={(e) => setTheory(e.target.value)} placeholder="Explain motive, means, opportunity, and contradictions…"/><button onClick={submitAccusation} disabled={busy || !accused || theory.length < 5}>SUBMIT THEORY</button>{result && <div className={`verdict ${result.correct ? "correct" : "wrong"}`}><strong>{result.correct ? "CASE SOLVED" : "INCORRECT ACCUSATION"} · {result.score}/100</strong><p>{result.verdict}</p><p>{result.solution}</p></div>}</section>
  </main>;
}

createRoot(document.getElementById("root")).render(<App />);

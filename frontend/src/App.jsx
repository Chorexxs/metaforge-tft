import { useState, useEffect, useRef } from "react";
import {
  ITEM_NAMES,
  getChampionImage,
  getItemImage,
  getTraitImage,
  initializeVersion,
  getCurrentVersion,
  ITEM_IDS,
} from "./data/gameData";

const API_URL = "http://127.0.0.1:8000";

const ITEM_ID_MAP = {
  3072: "BT",
  1070: "HoJ",
  3115: "Rabadons",
  3124: "Guinsoos",
  3036: "Giant Slayer",
  3153: "BORK",
  3035: "LW",
  3128: "IE",
  3091: "RFC",
  3090: "PD",
  3137: "QS",
  3026: "GA",
  3077: "DB",
  3130: "JH",
  3179: "ERS",
  3094: "SFC",
  3075: "HF",
  3190: "Aegis",
  3076: "Bramble",
  3193: "Gargoyle",
  3041: "DClaw",
  3110: "FH",
  3102: "Banshee",
  3044: "LDR",
  3139: "Mercurial",
  3111: "Warmog",
  3113: "Spirit",
  3147: "MZ",
  3140: "Zephyr",
  3222: "Spectral",
  3046: "Titans",
  3053: "Unholy",
  3177: "Heart",
  3142: "Edge",
  3107: "Contagion",
};

const AUGMENT_TIERS = {
  prismatic: "#A335EE",
  gold: "#FFD700",
  silver: "#C0C0C0",
};

const ECON_TARGETS = {
  "1-1": { target: 0, name: "Start" },
  "1-2": { target: 0, name: "Carousel" },
  "1-3": { target: 10, name: "Pre-Krugs" },
  "1-4": { target: 20, name: "Krugs" },
  "2-1": { target: 30, name: " Wolves" },
  "2-2": { target: 40, name: "Raptors" },
  "2-3": { target: 50, name: "Pre-Level" },
  "2-4": { target: 50, name: "Level 5" },
  "2-5": { target: 50, name: "Pre-Red" },
  "3-1": { target: 50, name: "Red Buff" },
  "3-2": { target: 40, name: "Augment" },
  "3-3": { target: 50, name: "Pre-Blue" },
  "3-4": { target: 50, name: "Level 6" },
  "4-1": { target: 50, name: "Blue" },
  "4-2": { target: 30, name: "Augment" },
  "4-3": { target: 50, name: "Pre-Golem" },
  "4-4": { target: 50, name: "Level 7" },
  "5-1": { target: 50, name: "Golem" },
  "5-2": { target: 50, name: "Pre-Dragon" },
  "5-3": { target: 50, name: "Dragon" },
  "5-4": { target: 50, name: "Level 8" },
  "6-1": { target: 50, name: "Pre-Rift" },
  "6-2": { target: 50, name: "Rift" },
  "6-3": { target: 50, name: "Level 9" },
  "6-4": { target: 50, name: "Final" },
};

const MOCK_AUGMENTS = {
  "2-1": [
    { name: "Money Matters", tier: "gold", desc: "+15 starting gold" },
    { name: "Tiny Titans", tier: "silver", desc: "Your units gain +50 HP" },
    { name: "Thrift", tier: "prismatic", desc: "Income boosts last longer" },
  ],
  "3-2": [
    {
      name: "First Strike",
      tier: "gold",
      desc: "Deal 15% more dmg to full HP",
    },
    { name: "Treasure Dive", tier: "silver", desc: "Gold nodes are richer" },
    {
      name: "High End",
      tier: "prismatic",
      desc: "Start with 2 prismatic augments",
    },
  ],
  "4-2": [
    { name: "Late Game Cash", tier: "gold", desc: "Win streakes give +5 gold" },
    { name: "Armory", tier: "silver", desc: "Get a free completed item" },
    { name: "Apex", tier: "prismatic", desc: "Your 5-costs get +25% stats" },
  ],
};

function App() {
  const [active, setActive] = useState(true);
  const [miniMode, setMiniMode] = useState(false);
  const [comp, setComp] = useState(null);
  const [phase, setPhase] = useState("early");
  const [gold, setGold] = useState(0);
  const [level, setLevel] = useState(1);
  const [round, setRound] = useState("1-1");
  const [hp, setHp] = useState(100);
  const [maxHp, setMaxHp] = useState(100);
  const [patch, setPatch] = useState(null);
  const [loading, setLoading] = useState(true);
  const [gameActive, setGameActive] = useState(false);
  const [boardUnits, setBoardUnits] = useState([]);
  const [benchUnits, setBenchUnits] = useState([]);
  const [augments, setAugments] = useState([]);
  const [winStreak, setWinStreak] = useState(0);
  const [loseStreak, setLoseStreak] = useState(0);
  const wsRef = useRef(null);

  useEffect(() => {
    initializeVersion().then((v) => {
      setPatch(v);
    });
    connectWebSocket();
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => {
      clearInterval(interval);
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  function connectWebSocket() {
    try {
      const ws = new WebSocket("ws://127.0.0.1:8000/ws/game");
      ws.onopen = () => {
        console.log("[TFT HUD] WebSocket connected");
      };
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === "recommendation") {
            setPhase(data.phase);
          }
        } catch (e) {}
      };
      ws.onclose = () => {
        console.log("[TFT HUD] WebSocket disconnected");
      };
      wsRef.current = ws;
    } catch (e) {
      console.log("[TFT HUD] WebSocket connection failed");
    }
  }

  async function fetchData() {
    try {
      const [compsRes, gameRes] = await Promise.all([
        fetch(`${API_URL}/api/comps?limit=1`),
        fetch(`${API_URL}/api/game/live-state`),
      ]);

      const compsData = await compsRes.json();
      if (compsData.data && compsData.data.length > 0) {
        setComp(compsData.data[0]);
      }

      const gameData = await gameRes.json();
      if (gameData.active && gameData.data) {
        setGameActive(true);
        setGold(gameData.data.gold || 0);
        setLevel(gameData.data.level || 1);
        setPhase(gameData.data.phase || "early");
        setRound(gameData.data.round || "1-1");
        setHp(gameData.data.hp || 100);
        setMaxHp(gameData.data.max_hp || 100);
        setBoardUnits(gameData.data.board_units || []);
        setBenchUnits(gameData.data.bench_units || []);
        setAugments(gameData.data.augments || []);
        setWinStreak(gameData.data.win_streak || 0);
        setLoseStreak(gameData.data.lose_streak || 0);

        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          wsRef.current.send(
            JSON.stringify({
              type: "game_state",
              data: gameData.data,
            }),
          );
        }
      } else {
        setGameActive(false);
      }

      setLoading(false);
    } catch (e) {
      setLoading(false);
    }
  }

  function getItemKeyFromId(itemId) {
    if (!itemId) return null;
    const id = typeof itemId === "string" ? parseInt(itemId, 10) : itemId;
    return ITEM_ID_MAP[id] || null;
  }

  function getEconStatus() {
    const roundData = ECON_TARGETS[round];
    if (!roundData) return { progress: 0, status: "neutral" };

    const target = roundData.target;
    const current = gold;

    if (target === 0) return { progress: 100, status: "neutral" };

    const progress = Math.min(100, (current / target) * 100);
    let status = "neutral";
    if (current >= target + 10) status = "surplus";
    else if (current < target - 10) status = "deficit";

    return { progress, status, target, current };
  }

  if (!active) return null;

  const width = miniMode ? 260 : 340;

  return (
    <div
      className="font-game rounded-xl overflow-hidden"
      style={{
        width,
        height: miniMode ? 180 : 680,
        backgroundColor: "#181326",
        border: "2px solid #FFB60D",
        boxShadow:
          "0 0 40px rgba(255, 182, 13, 0.15), 0 10px 30px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255,255,255,0.05)",
      }}
    >
      {/* Header */}
      <div
        className="flex items-center justify-between px-4 py-2.5"
        style={{ borderBottom: "1px solid rgba(255, 182, 13, 0.2)" }}
      >
        <div className="flex items-center gap-3">
          <span
            className="text-lg font-bold tracking-wider"
            style={{ color: "#FFB60D" }}
          >
            TFT
          </span>
          <span
            className="text-xs px-2 py-0.5 rounded font-medium"
            style={{
              backgroundColor: "rgba(255, 182, 13, 0.15)",
              color: "#FFB60D",
              border: "1px solid rgba(255, 182, 13, 0.3)",
            }}
          >
            {patch}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <div
            className="w-1.5 h-1.5 rounded-full"
            style={{
              backgroundColor: gameActive ? "#50C878" : "#FF4444",
              boxShadow: `0 0 8px ${gameActive ? "#50C878" : "#FF4444"}`,
            }}
          />
          <span
            className="text-[10px] uppercase tracking-widest"
            style={{
              color: gameActive
                ? "rgba(255, 182, 13, 0.7)"
                : "rgba(255, 68, 68, 0.7)",
            }}
          >
            {gameActive ? round : "No Game"}
          </span>
        </div>
      </div>

      {/* Stats Bar with EconMeter */}
      <div
        className="flex items-center justify-between px-4 py-2 text-[11px]"
        style={{
          background:
            "linear-gradient(90deg, rgba(0, 255, 229, 0.05) 0%, transparent 50%, rgba(255, 51, 102, 0.05) 100%)",
        }}
      >
        <div className="flex items-center gap-2">
          <span
            className="uppercase tracking-wide text-[9px]"
            style={{ color: "rgba(255, 182, 13, 0.6)" }}
          >
            Gold
          </span>
          <span
            className="font-bold"
            style={{
              color: "#FFD700",
              textShadow: "0 0 8px rgba(255, 215, 0, 0.4)",
            }}
          >
            {gold}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span
            className="uppercase tracking-wide text-[9px]"
            style={{ color: "rgba(65, 105, 225, 0.7)" }}
          >
            Level
          </span>
          <span className="font-bold" style={{ color: "#FFFFFF" }}>
            {level}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span
            className="uppercase tracking-wide text-[9px]"
            style={{ color: "rgba(80, 200, 120, 0.7)" }}
          >
            HP
          </span>
          <span
            className="font-bold"
            style={{ color: hp < 30 ? "#FF4444" : "#50C878" }}
          >
            {hp}
          </span>
        </div>
      </div>

      {/* EconMeter */}
      {!miniMode && gameActive && (
        <div
          className="px-4 py-2"
          style={{ borderTop: "1px solid rgba(255, 182, 13, 0.1)" }}
        >
          <div className="flex items-center justify-between mb-1">
            <span
              className="text-[9px] uppercase tracking-wide"
              style={{ color: "rgba(255, 182, 13, 0.5)" }}
            >
              Econ Target
            </span>
            <span
              className="text-[9px]"
              style={{ color: "rgba(255, 255, 255, 0.6)" }}
            >
              {gold}/{ECON_TARGETS[round]?.target || 50}
            </span>
          </div>
          <div
            className="h-1.5 rounded-full overflow-hidden"
            style={{ backgroundColor: "rgba(255,255,255,0.1)" }}
          >
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{
                width: `${Math.min(100, (gold / (ECON_TARGETS[round]?.target || 50)) * 100)}%`,
                backgroundColor:
                  gold >= (ECON_TARGETS[round]?.target || 50)
                    ? "#50C878"
                    : "#379CDE",
                boxShadow:
                  gold >= (ECON_TARGETS[round]?.target || 50)
                    ? "0 0 8px #50C878"
                    : "none",
              }}
            />
          </div>
        </div>
      )}

      {/* Streaks */}
      {!miniMode && gameActive && (winStreak > 0 || loseStreak > 0) && (
        <div className="px-4 py-2 flex items-center gap-4 text-[10px]">
          {winStreak > 0 && (
            <div className="flex items-center gap-1">
              <span style={{ color: "rgba(255, 182, 13, 0.5)" }}>Win:</span>
              <span className="font-bold" style={{ color: "#FFD700" }}>
                {winStreak}
              </span>
            </div>
          )}
          {loseStreak > 0 && (
            <div className="flex items-center gap-1">
              <span style={{ color: "rgba(255, 182, 13, 0.5)" }}>Lose:</span>
              <span className="font-bold" style={{ color: "#FF4444" }}>
                {loseStreak}
              </span>
            </div>
          )}
        </div>
      )}

      {/* Phase Guide */}
      {!miniMode && (
        <div className="px-4 py-3">
          <div
            className="text-[9px] uppercase tracking-[0.2em] mb-2"
            style={{ color: "rgba(255, 182, 13, 0.6)" }}
          >
            Current Objective
          </div>
          {phase === "early" ? (
            <div className="text-sm font-medium" style={{ color: "#FFFFFF" }}>
              <span style={{ color: "#379C37" }}>Economize</span>
              <div
                className="text-[10px] mt-0.5"
                style={{ color: "rgba(192, 192, 192, 0.7)" }}
              >
                Target: 50g before Krugs
              </div>
            </div>
          ) : phase === "mid" ? (
            <div className="text-sm font-medium" style={{ color: "#FFFFFF" }}>
              <span style={{ color: "#379CDE" }}>Build</span> your core
              <div
                className="text-[10px] mt-0.5"
                style={{ color: "rgba(192, 192, 192, 0.7)" }}
              >
                Roll for upgrades
              </div>
            </div>
          ) : (
            <div className="text-sm font-medium" style={{ color: "#FFFFFF" }}>
              <span style={{ color: "#A335EE" }}>Finalize</span> comp
              <div
                className="text-[10px] mt-0.5"
                style={{ color: "rgba(192, 192, 192, 0.7)" }}
              >
                Position for endgame
              </div>
            </div>
          )}
        </div>
      )}

      {/* Top Comp */}
      {!miniMode && comp && (
        <div
          className="px-4 py-3"
          style={{ borderTop: "1px solid rgba(255, 182, 13, 0.15)" }}
        >
          <div
            className="text-[9px] uppercase tracking-[0.2em] mb-2"
            style={{ color: "rgba(255, 182, 13, 0.6)" }}
          >
            Recommended Comp
          </div>
          <div
            className="rounded-lg p-3 relative overflow-hidden"
            style={{
              backgroundColor: "#1E1E2E",
              border: "1px solid rgba(255, 182, 13, 0.2)",
            }}
          >
            <div
              className={`absolute top-0 right-0 px-2.5 py-1 text-[10px] font-bold rounded-bl-lg`}
              style={{
                backgroundColor:
                  comp.tier === "S"
                    ? "#FFD700"
                    : comp.tier === "A"
                      ? "#C0C0C0"
                      : "#CD7F32",
                color: "#181326",
                boxShadow:
                  comp.tier === "S"
                    ? "0 0 15px rgba(255, 215, 0, 0.4)"
                    : "none",
              }}
            >
              {comp.tier}
            </div>
            <div
              className="text-sm font-bold pr-12"
              style={{ color: "#FFFFFF" }}
            >
              {comp.name}
            </div>
            <div className="flex items-center gap-4 mt-1.5 text-[11px]">
              <span style={{ color: "#50C878" }}>{comp.winrate}% Win Rate</span>
              <span style={{ color: "#379CDE" }}>{comp.top4rate}% Top 4</span>
            </div>
            <div className="flex gap-1.5 mt-2">
              {(comp.traits || []).slice(0, 4).map((trait, i) => {
                const traitImg = getTraitImage(trait);
                return traitImg ? (
                  <img
                    key={i}
                    src={traitImg}
                    alt={trait}
                    className="w-5 h-5"
                    style={{ borderRadius: "3px" }}
                  />
                ) : (
                  <span
                    key={i}
                    className="text-[9px] px-1.5 py-0.5 rounded border"
                    style={{
                      backgroundColor: "rgba(255, 182, 13, 0.15)",
                      color: "rgba(255, 182, 13, 0.9)",
                      border: "1px solid rgba(255, 182, 13, 0.3)",
                    }}
                  >
                    {trait}
                  </span>
                );
              })}
            </div>
            {(comp.champions || []).length > 0 && (
              <div className="flex gap-1 mt-2">
                {(comp.champions || []).slice(0, 5).map((champ, i) => {
                  const champImg = getChampionImage(champ);
                  return champImg ? (
                    <img
                      key={i}
                      src={champImg}
                      alt={champ}
                      className="w-7 h-7 champion-icon"
                      style={{
                        borderRadius: "4px",
                        border: "1px solid #2A2A45",
                      }}
                    />
                  ) : null;
                })}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Augment Advisor */}
      {!miniMode && gameActive && (
        <div
          className="px-4 py-3"
          style={{ borderTop: "1px solid rgba(255, 182, 13, 0.15)" }}
        >
          <div
            className="text-[9px] uppercase tracking-[0.2em] mb-2"
            style={{ color: "rgba(255, 182, 13, 0.6)" }}
          >
            Augment Advisor
          </div>
          <div className="space-y-1.5">
            {(MOCK_AUGMENTS[round] || MOCK_AUGMENTS["3-2"])
              .slice(0, 3)
              .map((aug, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between px-2 py-1 rounded"
                  style={{
                    backgroundColor: "rgba(255,255,255,0.03)",
                    borderLeft: `3px solid ${AUGMENT_TIERS[aug.tier] || "#C0C0C0"}`,
                  }}
                >
                  <span
                    className="text-[10px] font-medium"
                    style={{ color: "#FFFFFF" }}
                  >
                    {aug.name}
                  </span>
                  <span
                    className="text-[8px] uppercase px-1.5 py-0.5 rounded"
                    style={{
                      backgroundColor: AUGMENT_TIERS[aug.tier] + "20",
                      color: AUGMENT_TIERS[aug.tier] || "#C0C0C0",
                    }}
                  >
                    {aug.tier}
                  </span>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Board Units Preview */}
      {!miniMode && gameActive && boardUnits.length > 0 && (
        <div
          className="px-4 py-3"
          style={{ borderTop: "1px solid rgba(255, 182, 13, 0.15)" }}
        >
          <div
            className="text-[9px] uppercase tracking-[0.2em] mb-2"
            style={{ color: "rgba(255, 182, 13, 0.6)" }}
          >
            Your Units
          </div>
          <div className="flex flex-wrap gap-1">
            {boardUnits.slice(0, 8).map((unit, i) => {
              const champImg = getChampionImage(unit.name);
              const unitItems = (unit.items || []).slice(0, 3);
              return (
                <div key={i} className="relative group">
                  <img
                    src={champImg}
                    alt={unit.name}
                    className="w-8 h-8 rounded"
                    style={{
                      border: `2px solid ${unit.tier === 3 ? "#FFD700" : unit.tier === 2 ? "#C0C0C0" : "#2A2A45"}`,
                    }}
                  />
                  {unit.tier > 1 && (
                    <div
                      className="absolute -top-1 -right-1 w-3 h-3 flex items-center justify-center rounded-full text-[6px] font-bold"
                      style={{ backgroundColor: "#FFD700", color: "#181326" }}
                    >
                      {unit.tier}
                    </div>
                  )}
                  {unitItems.length > 0 && (
                    <div className="absolute -bottom-1 left-0 right-0 flex justify-center gap-0.5">
                      {unitItems.map((itemId, j) => {
                        const itemKey = getItemKeyFromId(itemId);
                        return itemKey ? (
                          <img
                            key={j}
                            src={getItemImage(itemKey)}
                            alt=""
                            className="w-3 h-3 rounded-sm"
                          />
                        ) : null;
                      })}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Items */}
      {!miniMode && (
        <div
          className="px-4 py-3"
          style={{ borderTop: "1px solid rgba(255, 182, 13, 0.15)" }}
        >
          <div
            className="text-[9px] uppercase tracking-[0.2em] mb-2"
            style={{ color: "rgba(255, 182, 13, 0.6)" }}
          >
            Priority Items
          </div>
          <div className="flex gap-2">
            {["Rabadons", "HoJ", "BT"].map((itemKey, i) => {
              const itemData = ITEM_NAMES[itemKey];
              const itemImg = getItemImage(itemKey);
              const itemColor = ["#A335EE", "#FFD700", "#C0C0C0"][i];
              return (
                <div
                  key={i}
                  className="flex-1 flex flex-col items-center py-1.5 rounded border transition-all cursor-default"
                  style={{
                    backgroundColor:
                      i === 0
                        ? "rgba(163, 53, 238, 0.15)"
                        : i === 1
                          ? "rgba(255, 215, 0, 0.15)"
                          : "rgba(192, 192, 192, 0.15)",
                    color: itemColor,
                    borderColor: itemColor + "40",
                  }}
                >
                  {itemImg && (
                    <img
                      src={itemImg}
                      alt={itemData?.name || itemKey}
                      className="w-6 h-6 mb-1 item-icon"
                    />
                  )}
                  <span
                    className="text-[7px] font-medium"
                    style={{ color: itemColor }}
                  >
                    {itemData?.name || itemKey}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Footer */}
      <div
        className="flex items-center justify-between px-4 py-2 text-[9px]"
        style={{
          borderTop: "1px solid rgba(255, 182, 13, 0.15)",
          color: "rgba(144, 144, 160, 0.5)",
        }}
      >
        <span>Alt+H toggle</span>
        <span>Alt+M mini</span>
      </div>
    </div>
  );
}

export default App;

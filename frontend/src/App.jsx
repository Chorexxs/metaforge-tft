import { useState, useEffect } from "react";
import {
  ITEM_NAMES,
  getChampionImage,
  getItemImage,
  DD_VERSION,
} from "./data/gameData";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [active, setActive] = useState(true);
  const [miniMode, setMiniMode] = useState(false);
  const [comp, setComp] = useState(null);
  const [phase, setPhase] = useState("early");
  const [gold, setGold] = useState(0);
  const [level, setLevel] = useState(1);
  const [round, setRound] = useState("1-1");
  const [hp, setHp] = useState(100);
  const [patch, setPatch] = useState("14");
  const [loading, setLoading] = useState(true);
  const [gameActive, setGameActive] = useState(false);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  async function fetchData() {
    try {
      const [compsRes, gameRes, patchRes] = await Promise.all([
        fetch(`${API_URL}/api/comps?limit=1`),
        fetch(`${API_URL}/api/game/live-state`),
        fetch(`${API_URL}/api/patch/current`),
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
      } else {
        setGameActive(false);
      }

      const patchData = await patchRes.json();
      if (patchData.data) {
        setPatch(patchData.data.version || DD_VERSION);
      }

      setLoading(false);
    } catch (e) {
      setLoading(false);
    }
  }

  if (!active) return null;

  const width = miniMode ? 260 : 340;

  return (
    <div
      className="font-game rounded-xl overflow-hidden"
      style={{
        width,
        height: miniMode ? 180 : 520,
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

      {/* Stats Bar */}
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
              {(comp.traits || []).slice(0, 4).map((trait, i) => (
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
              ))}
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
              const itemImg = itemData?.id ? getItemImage(itemData.id) : null;
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

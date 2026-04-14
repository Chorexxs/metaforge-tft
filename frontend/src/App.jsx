import { useState, useEffect } from "react";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [active, setActive] = useState(true);
  const [miniMode, setMiniMode] = useState(false);
  const [comp, setComp] = useState(null);
  const [phase, setPhase] = useState("early");
  const [gold, setGold] = useState(50);
  const [level, setLevel] = useState(4);
  const [patch, setPatch] = useState("14");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  async function fetchData() {
    try {
      const res = await fetch(`${API_URL}/api/comps?limit=1`);
      const data = await res.json();
      if (data.data && data.data.length > 0) {
        setComp(data.data[0]);
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
        backgroundColor: "#0D0D0F",
        border: "1px solid #2A2A35",
        boxShadow:
          "0 0 40px rgba(0, 255, 229, 0.08), inset 0 1px 0 rgba(255,255,255,0.03)",
      }}
    >
      {/* Header */}
      <div
        className="flex items-center justify-between px-4 py-2.5"
        style={{ borderBottom: "1px solid rgba(0, 255, 229, 0.1)" }}
      >
        <div className="flex items-center gap-3">
          <span
            className="text-lg font-bold tracking-wider"
            style={{ color: "#00FFE5" }}
          >
            TFT
          </span>
          <span
            className="text-xs px-2 py-0.5 rounded font-medium"
            style={{
              backgroundColor: "rgba(0, 255, 229, 0.1)",
              color: "#00FFE5",
              border: "1px solid rgba(0, 255, 229, 0.2)",
            }}
          >
            {patch}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <div
            className="w-1.5 h-1.5 rounded-full"
            style={{ backgroundColor: "#00FFE5", boxShadow: "0 0 8px #00FFE5" }}
          />
          <span
            className="text-[10px] uppercase tracking-widest"
            style={{ color: "rgba(0, 255, 229, 0.6)" }}
          >
            Live
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
            style={{ color: "rgba(0, 255, 229, 0.5)" }}
          >
            Gold
          </span>
          <span className="font-bold" style={{ color: "#00FFE5" }}>
            {gold}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span
            className="uppercase tracking-wide text-[9px]"
            style={{ color: "rgba(255, 51, 102, 0.6)" }}
          >
            Level
          </span>
          <span className="font-bold" style={{ color: "#E8E8EC" }}>
            {level}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span
            className="uppercase tracking-wide text-[9px]"
            style={{ color: "rgba(255, 184, 0, 0.6)" }}
          >
            Phase
          </span>
          <span
            className="font-medium uppercase text-[10px]"
            style={{ color: "#00FFE5" }}
          >
            {phase}
          </span>
        </div>
      </div>

      {/* Phase Guide */}
      {!miniMode && (
        <div className="px-4 py-3">
          <div
            className="text-[9px] uppercase tracking-[0.2em] mb-2"
            style={{ color: "rgba(0, 255, 229, 0.5)" }}
          >
            Current Objective
          </div>
          {phase === "early" ? (
            <div className="text-sm font-medium" style={{ color: "#E8E8EC" }}>
              <span style={{ color: "#00FFE5" }}>Economize</span>
              <div
                className="text-[10px] mt-0.5"
                style={{ color: "rgba(0, 255, 229, 0.6)" }}
              >
                Target: 50g before Krugs
              </div>
            </div>
          ) : phase === "mid" ? (
            <div className="text-sm font-medium" style={{ color: "#E8E8EC" }}>
              <span style={{ color: "#FF3366" }}>Build</span> your core
              <div
                className="text-[10px] mt-0.5"
                style={{ color: "rgba(0, 255, 229, 0.6)" }}
              >
                Roll for upgrades
              </div>
            </div>
          ) : (
            <div className="text-sm font-medium" style={{ color: "#E8E8EC" }}>
              <span style={{ color: "#FFB800" }}>Finalize</span> comp
              <div
                className="text-[10px] mt-0.5"
                style={{ color: "rgba(0, 255, 229, 0.6)" }}
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
          style={{ borderTop: "1px solid rgba(0, 255, 229, 0.1)" }}
        >
          <div
            className="text-[9px] uppercase tracking-[0.2em] mb-2"
            style={{ color: "rgba(0, 255, 229, 0.5)" }}
          >
            Recommended Comp
          </div>
          <div
            className="rounded-lg p-3 relative overflow-hidden"
            style={{
              backgroundColor: "#151518",
              border: "1px solid rgba(255, 51, 102, 0.1)",
            }}
          >
            <div
              className={`absolute top-0 right-0 px-2.5 py-1 text-[10px] font-bold rounded-bl-lg`}
              style={{
                backgroundColor:
                  comp.tier === "S"
                    ? "#FF3366"
                    : comp.tier === "A"
                      ? "#FFB800"
                      : "#7A7A85",
                color: "#0D0D0F",
              }}
            >
              {comp.tier}
            </div>
            <div
              className="text-sm font-bold pr-12"
              style={{ color: "#E8E8EC" }}
            >
              {comp.name}
            </div>
            <div className="flex items-center gap-4 mt-1.5 text-[11px]">
              <span style={{ color: "#00FFE5" }}>{comp.winrate}% WR</span>
              <span style={{ color: "#FF3366" }}>{comp.top4rate}% T4</span>
            </div>
            <div className="flex gap-1.5 mt-2">
              {(comp.traits || []).slice(0, 4).map((trait, i) => (
                <span
                  key={i}
                  className="text-[9px] px-1.5 py-0.5 rounded border"
                  style={{
                    backgroundColor: "rgba(0, 255, 229, 0.1)",
                    color: "rgba(0, 255, 229, 0.8)",
                    border: "1px solid rgba(0, 255, 229, 0.1)",
                  }}
                >
                  {trait}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Items */}
      {!miniMode && (
        <div
          className="px-4 py-3"
          style={{ borderTop: "1px solid rgba(0, 255, 229, 0.1)" }}
        >
          <div
            className="text-[9px] uppercase tracking-[0.2em] mb-2"
            style={{ color: "rgba(0, 255, 229, 0.5)" }}
          >
            Priority Items
          </div>
          <div className="flex gap-2">
            {["Rabadons", "HoJ", "BT"].map((item, i) => (
              <div
                key={i}
                className="flex-1 text-center py-1.5 text-[10px] font-medium rounded border transition-all cursor-default"
                style={{
                  backgroundColor:
                    i === 0
                      ? "rgba(0, 255, 229, 0.1)"
                      : i === 1
                        ? "rgba(255, 51, 102, 0.1)"
                        : "rgba(255, 184, 0, 0.1)",
                  color:
                    i === 0
                      ? "rgba(0, 255, 229, 0.8)"
                      : i === 1
                        ? "rgba(255, 51, 102, 0.8)"
                        : "rgba(255, 184, 0, 0.8)",
                  borderColor:
                    i === 0
                      ? "rgba(0, 255, 229, 0.2)"
                      : i === 1
                        ? "rgba(255, 51, 102, 0.2)"
                        : "rgba(255, 184, 0, 0.2)",
                }}
              >
                {item}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Footer */}
      <div
        className="flex items-center justify-between px-4 py-2 text-[9px]"
        style={{
          borderTop: "1px solid rgba(0, 255, 229, 0.1)",
          color: "rgba(122, 122, 133, 0.4)",
        }}
      >
        <span>Alt+H toggle</span>
        <span>Alt+M mini</span>
      </div>
    </div>
  );
}

export default App;

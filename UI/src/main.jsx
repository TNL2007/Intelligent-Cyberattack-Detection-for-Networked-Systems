import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity,
  AlertTriangle,
  Crosshair,
  Globe,
  KeyRound,
  RadioTower,
  RotateCcw,
  ShieldCheck,
  ShieldQuestion,
  TerminalSquare,
  Waves,
} from "lucide-react";
import "./styles.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const flows = [
  { type: "Normal", label: "Normal", icon: ShieldCheck, tone: "normal" },
  { type: "Port_Scan", label: "Port Scan", icon: Crosshair, tone: "warning" },
  { type: "Web_Crwling", label: "Web Crawling", icon: Globe, tone: "warning" },
  { type: "Brute_Force", label: "Brute Force", icon: KeyRound, tone: "attack" },
  { type: "HTTP_DDoS", label: "HTTP DDoS", icon: RadioTower, tone: "attack" },
  { type: "ICMP_Flood", label: "ICMP Flood", icon: Waves, tone: "attack" },
];

const scenarioSteps = {
  "Scenario A": ["Port_Scan", "Web_Crwling", "Brute_Force"],
  "Scenario B": ["Port_Scan", "HTTP_DDoS", "ICMP_Flood"],
};

const flowLabelByType = Object.fromEntries(flows.map((flow) => [flow.type, flow.label]));
const probabilityLabels = ["Scenario A", "Scenario B", "Neither"];

function App() {
  const [history, setHistory] = useState([]);
  const [metrics, setMetrics] = useState(emptyMetrics());
  const [busyFlow, setBusyFlow] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    refreshState();
  }, []);

  const observedFlows = useMemo(() => new Set(history.map((event) => event.flow_type)), [history]);
  const activeScenario = metrics.prediction === "Scenario B" ? "Scenario B" : "Scenario A";

  async function request(path, options = {}) {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
    if (!response.ok) {
      const payload = await response.json().catch(() => ({}));
      throw new Error(payload.detail || "Request failed");
    }
    return response.json();
  }

  async function refreshState() {
    try {
      const [historyPayload, metricPayload] = await Promise.all([
        request("/history"),
        request("/metrics"),
      ]);
      setHistory(historyPayload.history || []);
      setMetrics(normalizeMetrics(metricPayload));
      setError("");
    } catch (caught) {
      setError(caught.message);
    }
  }

  async function injectFlow(flowType) {
    setBusyFlow(flowType);
    setError("");
    try {
      const payload = await request("/inject", {
        method: "POST",
        body: JSON.stringify({ flow_type: flowType }),
      });
      setHistory(payload.history || []);
      setMetrics(normalizeMetrics(payload));
    } catch (caught) {
      setError(caught.message);
    } finally {
      setBusyFlow(null);
    }
  }

  async function resetCampaign() {
    setError("");
    try {
      await request("/reset", { method: "POST" });
      setHistory([]);
      setMetrics(emptyMetrics());
    } catch (caught) {
      setError(caught.message);
    }
  }

  return (
    <main className="shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Online Campaign Monitor</p>
          <h1>AI Multi-Step Attack Detector</h1>
        </div>
        <button className="resetButton" onClick={resetCampaign}>
          <RotateCcw size={18} />
          Reset
        </button>
      </header>

      {error && <div className="errorBanner">{error}</div>}

      <section className="dashboard">
        <div className="panel injectionPanel">
          <div className="sectionTitle">
            <Activity size={18} />
            <h2>Flow Injection</h2>
          </div>
          <div className="flowGrid">
            {flows.map((flow) => {
              const Icon = flow.icon;
              return (
                <button
                  key={flow.type}
                  className={`flowCard ${flow.tone}`}
                  disabled={Boolean(busyFlow)}
                  onClick={() => injectFlow(flow.type)}
                >
                  <span className="iconWrap">
                    <Icon size={22} />
                  </span>
                  <span>{flow.label}</span>
                  {busyFlow === flow.type && <span className="pulseDot" />}
                </button>
              );
            })}
          </div>
        </div>

        <section className={`predictionCard ${predictionTone(metrics.prediction)}`}>
          <p>Current Prediction</p>
          <h2>{metrics.prediction}</h2>
          <div className="confidence">
            <span>Confidence</span>
            <strong>{formatPercent(metrics.confidence)}</strong>
          </div>
        </section>

        <div className="panel probabilityPanel">
          <div className="sectionTitle">
            <ShieldQuestion size={18} />
            <h2>Probability</h2>
          </div>
          <div className="bars">
            {probabilityLabels.map((label) => (
              <div className="barRow" key={label}>
                <div className="barMeta">
                  <span>{label}</span>
                  <strong>{formatPercent(metrics.probabilities[label] || 0)}</strong>
                </div>
                <div className="barTrack">
                  <div
                    className={`barFill ${label.replace(" ", "").toLowerCase()}`}
                    style={{ width: `${Math.round((metrics.probabilities[label] || 0) * 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="panel timelinePanel">
          <div className="sectionTitle">
            <TerminalSquare size={18} />
            <h2>Timeline</h2>
          </div>
          <div className="timeline">
            {history.length === 0 ? (
              <div className="emptyState">No flows injected</div>
            ) : (
              history.map((event, index) => (
                <div
                  className={`timelineItem ${index === history.length - 1 ? "latest" : ""}`}
                  key={`${event.step}-${event.flow_type}`}
                >
                  <span>{event.step}</span>
                  <strong>{event.flow_name || flowLabelByType[event.flow_type]}</strong>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="panel progressPanel">
          <div className="sectionTitle">
            <AlertTriangle size={18} />
            <h2>Attack Progress</h2>
          </div>
          <div className="scenarioToggle">
            <span className={activeScenario === "Scenario A" ? "active" : ""}>Scenario A</span>
            <span className={activeScenario === "Scenario B" ? "active" : ""}>Scenario B</span>
          </div>
          <div className="progressList">
            {scenarioSteps[activeScenario].map((flowType) => {
              const complete = observedFlows.has(flowType);
              return (
                <div className={complete ? "complete" : "pending"} key={flowType}>
                  <span>{complete ? "✓" : "⏳"}</span>
                  <strong>{flowLabelByType[flowType]}</strong>
                </div>
              );
            })}
          </div>
        </div>

        <div className="panel logPanel">
          <div className="sectionTitle">
            <TerminalSquare size={18} />
            <h2>Event Log</h2>
          </div>
          <div className="eventLog">
            {history.length === 0 ? (
              <div className="emptyState">Awaiting campaign activity</div>
            ) : (
              [...history].reverse().map((event) => (
                <article key={`log-${event.step}`}>
                  <span>Flow {event.step}</span>
                  <strong>{event.flow_name}</strong>
                  <small>{event.prediction} · {formatPercent(event.confidence)}</small>
                </article>
              ))
            )}
          </div>
        </div>
      </section>
    </main>
  );
}

function emptyMetrics() {
  return {
    prediction: "Neither",
    confidence: 0,
    probabilities: {
      "Scenario A": 0,
      "Scenario B": 0,
      Neither: 0,
    },
    campaign_length: 0,
  };
}

function normalizeMetrics(payload) {
  return {
    ...emptyMetrics(),
    ...payload,
    probabilities: {
      ...emptyMetrics().probabilities,
      ...(payload.probabilities || {}),
    },
  };
}

function predictionTone(prediction) {
  if (prediction === "Scenario A" || prediction === "Scenario B") return "attack";
  return "neutral";
}

function formatPercent(value) {
  return `${Math.round((value || 0) * 100)}%`;
}

createRoot(document.getElementById("root")).render(<App />);

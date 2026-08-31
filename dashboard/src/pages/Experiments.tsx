import { useState } from "react";
import "./Experiments.css";

type ExperimentType =
  | "superposition"
  | "entanglement"
  | "coin"
  | "custom";

interface Result {
  states: Record<string, number>;
  explanation: string;
}

function Experiments() {
  const [experiment, setExperiment] =
    useState<ExperimentType>("superposition");

  const [qubits, setQubits] = useState(2);
  const [shots, setShots] = useState(1000);

  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<Result | null>(null);

  function runExperiment() {
    setRunning(true);
    setResult(null);

    setTimeout(() => {
      let states: Record<string, number>;
      let explanation = "";

      if (experiment === "superposition") {
        states = {
          "00": 50.2,
          "01": 0,
          "10": 0,
          "11": 49.8,
        };

        explanation =
          "The qubits were placed into a superposition. " +
          "The simulator produced the possible measurement outcomes " +
          "with approximately equal probability.";
      } else if (experiment === "entanglement") {
        states = {
          "00": 50.1,
          "01": 0.2,
          "10": 0.1,
          "11": 49.6,
        };

        explanation =
          "The two qubits were entangled. When measured, " +
          "they strongly prefer matching outcomes such as 00 and 11.";
      } else if (experiment === "coin") {
        states = {
          "0": 49.7,
          "1": 50.3,
        };

        explanation =
          "This behaves like a quantum coin flip. " +
          "The qubit has approximately equal probability of being measured as 0 or 1.";
      } else {
        states = {
          "00": 25.4,
          "01": 24.7,
          "10": 25.1,
          "11": 24.8,
        };

        explanation =
          "Your custom quantum experiment was executed by the " +
          "QuantumOS simulator.";
      }

      setResult({
        states,
        explanation,
      });

      setRunning(false);
    }, 1200);
  }

  function resetExperiment() {
    setResult(null);
    setExperiment("superposition");
    setQubits(2);
    setShots(1000);
  }

  return (
    <div className="experiments-page">
      <div className="experiments-header">
        <div>
          <span className="eyebrow">
            QUANTUM LAB
          </span>

          <h1>Run a Quantum Experiment</h1>

          <p>
            Explore quantum computing without needing to know
            how the underlying system works.
          </p>
        </div>

        {result && (
          <button
            className="secondary-button"
            onClick={resetExperiment}
          >
            New Experiment
          </button>
        )}
      </div>

      <div className="experiment-layout">

        {/* LEFT SIDE */}

        <section className="experiment-builder">

          <div className="section-title">
            <span>01</span>
            <div>
              <h2>Choose an experiment</h2>
              <p>
                Start with a simple quantum experiment.
              </p>
            </div>
          </div>

          <div className="experiment-options">

            <button
              className={
                experiment === "superposition"
                  ? "experiment-option active"
                  : "experiment-option"
              }
              onClick={() =>
                setExperiment("superposition")
              }
            >
              <div className="option-icon">
                Ψ
              </div>

              <div>
                <strong>Superposition</strong>
                <span>
                  Put a qubit into multiple possible states.
                </span>
              </div>
            </button>

            <button
              className={
                experiment === "entanglement"
                  ? "experiment-option active"
                  : "experiment-option"
              }
              onClick={() =>
                setExperiment("entanglement")
              }
            >
              <div className="option-icon">
                ∞
              </div>

              <div>
                <strong>Entanglement</strong>
                <span>
                  Explore the connection between qubits.
                </span>
              </div>
            </button>

            <button
              className={
                experiment === "coin"
                  ? "experiment-option active"
                  : "experiment-option"
              }
              onClick={() =>
                setExperiment("coin")
              }
            >
              <div className="option-icon">
                ◉
              </div>

              <div>
                <strong>Quantum Coin Flip</strong>
                <span>
                  Try a quantum version of a coin flip.
                </span>
              </div>
            </button>

            <button
              className={
                experiment === "custom"
                  ? "experiment-option active"
                  : "experiment-option"
              }
              onClick={() =>
                setExperiment("custom")
              }
            >
              <div className="option-icon">
                +
              </div>

              <div>
                <strong>Custom Experiment</strong>
                <span>
                  Run a basic multi-qubit experiment.
                </span>
              </div>
            </button>

          </div>

          <div className="section-title settings-title">
            <span>02</span>

            <div>
              <h2>Experiment settings</h2>
              <p>
                Configure the size of your experiment.
              </p>
            </div>
          </div>

          <div className="settings-grid">

            <label className="setting-card">
              <span>Qubits</span>

              <select
                value={qubits}
                onChange={(event) =>
                  setQubits(
                    Number(event.target.value)
                  )
                }
              >
                <option value={1}>1 qubit</option>
                <option value={2}>2 qubits</option>
                <option value={3}>3 qubits</option>
                <option value={4}>4 qubits</option>
                <option value={8}>8 qubits</option>
              </select>
            </label>

            <label className="setting-card">
              <span>Measurements</span>

              <select
                value={shots}
                onChange={(event) =>
                  setShots(
                    Number(event.target.value)
                  )
                }
              >
                <option value={100}>
                  100 shots
                </option>

                <option value={500}>
                  500 shots
                </option>

                <option value={1000}>
                  1,000 shots
                </option>

                <option value={5000}>
                  5,000 shots
                </option>
              </select>
            </label>

          </div>

          <button
            className="run-button"
            onClick={runExperiment}
            disabled={running}
          >
            {running
              ? "Running Quantum Experiment..."
              : "Run Experiment →"}
          </button>

          <div className="runtime-info">
            <span className="online-dot" />
            QuantumOS Simulator
            <span>•</span>
            32 qubits available
          </div>

        </section>

        {/* RIGHT SIDE */}

        <section className="experiment-preview">

          {!result && !running && (
            <div className="preview-empty">

              <div className="quantum-symbol">
                Q
              </div>

              <h2>Your results will appear here</h2>

              <p>
                Choose an experiment and press
                <strong> Run Experiment </strong>
                to see what happens.
              </p>

            </div>
          )}

          {running && (
            <div className="preview-running">

              <div className="loader-orbit">
                <div>Q</div>
              </div>

              <h2>Running experiment</h2>

              <p>
                QuantumOS is executing your circuit...
              </p>

              <div className="progress-track">
                <div className="progress-bar" />
              </div>

            </div>
          )}

          {result && (
            <div className="results">

              <div className="results-header">

                <div>
                  <span className="result-label">
                    EXPERIMENT COMPLETE
                  </span>

                  <h2>Quantum Result</h2>
                </div>

                <span className="success-badge">
                  COMPLETE
                </span>

              </div>

              <div className="result-meta">

                <div>
                  <span>Experiment</span>
                  <strong>
                    {experiment === "superposition"
                      ? "Superposition"
                      : experiment === "entanglement"
                      ? "Entanglement"
                      : experiment === "coin"
                      ? "Quantum Coin Flip"
                      : "Custom Experiment"}
                  </strong>
                </div>

                <div>
                  <span>Qubits</span>
                  <strong>{qubits}</strong>
                </div>

                <div>
                  <span>Shots</span>
                  <strong>
                    {shots.toLocaleString()}
                  </strong>
                </div>

              </div>

              <div className="result-chart">

                {Object.entries(result.states).map(
                  ([state, probability]) => {

                    if (probability === 0) {
                      return null;
                    }

                    return (
                      <div
                        className="result-row"
                        key={state}
                      >
                        <div className="result-state">
                          |{state}⟩
                        </div>

                        <div className="result-bar-container">
                          <div
                            className="result-bar"
                            style={{
                              width: `${probability}%`,
                            }}
                          />
                        </div>

                        <strong>
                          {probability.toFixed(1)}%
                        </strong>
                      </div>
                    );
                  }
                )}

              </div>

              <div className="explanation">

                <span>
                  WHAT HAPPENED?
                </span>

                <p>
                  {result.explanation}
                </p>

              </div>

              <div className="result-footer">
                <span>
                  Executed by QuantumOS QVM
                </span>

                <span>
                  {new Date().toLocaleTimeString()}
                </span>
              </div>

            </div>
          )}

        </section>

      </div>
    </div>
  );
}

export default Experiments;
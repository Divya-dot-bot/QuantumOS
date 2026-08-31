import {
  useMemo,
  useState,
} from "react";

import "./QuantumCore.css";

import {
  runJob,
  submitJob,
} from "../services/api";

import ResultChart from "../components/ResultChart";


type GateType =
  | "H"
  | "X"
  | "Y"
  | "Z"
  | "S"
  | "T"
  | "M";


interface Gate {
  id: string;
  type: GateType;
  qubit: number;
  column: number;
}


const GATES: GateType[] = [
  "H",
  "X",
  "Y",
  "Z",
  "S",
  "T",
  "M",
];


export default function QuantumCore() {
  const [qubits, setQubits] =
    useState(3);

  const [shots, setShots] =
    useState(1024);

  const [selectedGate, setSelectedGate] =
    useState<GateType>("H");

  const [gates, setGates] =
    useState<Gate[]>([]);

  const [running, setRunning] =
    useState(false);

  const [result, setResult] =
    useState<{
      counts: Record<string, number>;
      shots: number;
      backend_name: string | null;
      backend_id: string | null;
      job_id: string;
    } | null>(null);


  const columns = 8;


  const circuitDepth = useMemo(() => {
    if (gates.length === 0) {
      return 0;
    }

    return (
      Math.max(
        ...gates.map(
          (gate) => gate.column,
        ),
      ) + 1
    );
  }, [gates]);


  const gateCount =
    gates.length;


  function addGate(
    qubit: number,
    column: number,
  ) {
    const occupied =
      gates.some(
        (gate) =>
          gate.qubit === qubit &&
          gate.column === column,
      );

    if (occupied) return;


    setGates((current) => [
      ...current,
      {
        id:
          `${Date.now()}-${Math.random()}`,
        type: selectedGate,
        qubit,
        column,
      },
    ]);

    setResult(null);
  }


  function removeGate(id: string) {
    setGates((current) =>
      current.filter(
        (gate) =>
          gate.id !== id,
      ),
    );

    setResult(null);
  }


  function clearCircuit() {
    setGates([]);
    setResult(null);
  }


    function loadExample() {
    setQubits(2);

    setGates([
      {
        id: "example-h",
        type: "H",
        qubit: 0,
        column: 0,
      },
      {
        id: "example-m0",
        type: "M",
        qubit: 0,
        column: 2,
      },
      {
        id: "example-m1",
        type: "M",
        qubit: 1,
        column: 2,
      },
    ]);
    setResult(null);
  }


    function buildProgram(): string {
    const sorted = [...gates].sort(
      (a, b) =>
        a.column - b.column ||
        a.qubit - b.qubit,
    );

    const operationLines = sorted
      .filter(
        (gate) => gate.type !== "M",
      )
      .map(
        (gate) =>
          `${gate.type.toLowerCase()} ${gate.qubit}`,
      );

    const hasMeasurement = gates.some(
      (gate) => gate.type === "M",
    );

    const lines = [
      `qubits ${qubits}`,
      ...operationLines,
    ];

    if (hasMeasurement) {
      lines.push("measure");
    }

    return lines.join("\n");
  }


  async function runCircuit() {
    if (gates.length === 0) {
      return;
    }

    try {
      setRunning(true);
      setResult(null);

      const program = buildProgram();

      console.log(
        "QuantumOS program:",
        program,
      );

      const submission =
        await submitJob({
          circuit: program,
          shots,
          priority: 0,
          metadata: {
            source: "quantum-core",
            qubits,
            depth: circuitDepth,
            gate_count: gateCount,
            program,
          },
        });

      const execution =
        await runJob(
          submission.job_id,
        );

      setResult({
        counts: execution.counts,
        shots: execution.shots,
        backend_name:
          execution.backend_name,
        backend_id:
          execution.backend_id,
        job_id:
          execution.job_id,
      });
    } catch (error) {
      console.error(
        "QuantumOS circuit execution failed:",
        error,
      );

      window.alert(
        error instanceof Error
          ? error.message
          : "Circuit execution failed.",
      );
    } finally {
      setRunning(false);
    }
  }


  return (
    <div className="quantum-core-page">
      <div className="core-header">
        <div>
          <div className="core-eyebrow">
            QUANTUM RUNTIME
          </div>

          <h1>
            Quantum Core
          </h1>

          <p>
            Inspect and execute circuits through
            the local QuantumOS runtime.
          </p>
        </div>

        <div className="core-status">
          <span className="status-dot" />
          LOCAL QVM
        </div>
      </div>


      <div className="core-toolbar">
        <div className="toolbar-group">
          <span className="toolbar-label">
            QUBITS
          </span>

          <button
            type="button"
            className="number-button"
            onClick={() =>
              setQubits(
                (value) =>
                  Math.max(
                    1,
                    value - 1,
                  ),
              )
            }
          >
            −
          </button>

          <strong>
            {qubits}
          </strong>

          <button
            type="button"
            className="number-button"
            onClick={() =>
              setQubits(
                (value) =>
                  Math.min(
                    8,
                    value + 1,
                  ),
              )
            }
          >
            +
          </button>
        </div>


        <div className="toolbar-group">
          <span className="toolbar-label">
            SHOTS
          </span>

          <select
            value={shots}
            onChange={(event) =>
              setShots(
                Number(
                  event.target.value,
                ),
              )
            }
          >
            <option value={256}>
              256
            </option>

            <option value={512}>
              512
            </option>

            <option value={1024}>
              1024
            </option>

            <option value={2048}>
              2048
            </option>
          </select>
        </div>


        <button
          type="button"
          className="secondary-button"
          onClick={
  loadExample
}
        >
          Load Superposition Example
        </button>


        <button
          type="button"
          className="secondary-button"
          onClick={
            clearCircuit
          }
        >
          Clear
        </button>


        <button
          type="button"
          className="run-button"
          onClick={
            runCircuit
          }
          disabled={
            running ||
            gates.length === 0
          }
        >
          {running
            ? "Running..."
            : "▶ Run Circuit"}
        </button>
      </div>


      <div className="core-grid">
        <section className="circuit-panel">
          <div className="panel-heading">
            <div>
              <span>
                EDITOR
              </span>

              <h2>
                Circuit
              </h2>
            </div>

            <div className="circuit-meta">
              {qubits} qubits ·{" "}
              {circuitDepth} depth ·{" "}
              {gateCount} gates
            </div>
          </div>


          <div className="gate-toolbar">
            {GATES.map(
              (gate) => (
                <button
                  type="button"
                  key={gate}
                  className={
                    selectedGate ===
                    gate
                      ? "gate-selector selected"
                      : "gate-selector"
                  }
                  onClick={() =>
                    setSelectedGate(
                      gate,
                    )
                  }
                >
                  {gate}
                </button>
              ),
            )}
          </div>


          <div className="circuit-help">
            Select a gate, then click an
            empty cell to place it.
          </div>


          <div className="circuit-wrapper">
            <div className="column-numbers">
              <div className="qubit-spacer" />

              {Array.from(
                {
                  length:
                    columns,
                },
                (_, column) => (
                  <div
                    className="column-number"
                    key={column}
                  >
                    {column + 1}
                  </div>
                ),
              )}
            </div>


            {Array.from(
              {
                length: qubits,
              },
              (_, qubit) => (
                <div
                  className="circuit-row"
                  key={qubit}
                >
                  <div className="qubit-label">
                    q<sub>{qubit}</sub>
                  </div>

                  {Array.from(
                    {
                      length:
                        columns,
                    },
                    (_, column) => {
                      const gate =
                        gates.find(
                          (item) =>
                            item.qubit ===
                              qubit &&
                            item.column ===
                              column,
                        );

                      return (
                        <button
                          type="button"
                          className="circuit-cell"
                          key={column}
                          onClick={() => {
                            if (
                              gate
                            ) {
                              removeGate(
                                gate.id,
                              );
                            } else {
                              addGate(
                                qubit,
                                column,
                              );
                            }
                          }}
                        >
                          {gate && (
                            <span className="placed-gate">
                              {
                                gate.type
                              }
                            </span>
                          )}
                        </button>
                      );
                    },
                  )}
                </div>
              ),
            )}
          </div>
        </section>


        <aside className="inspector-panel">
          <div className="panel-heading">
            <div>
              <span>
                INSPECTOR
              </span>

              <h2>
                Circuit Info
              </h2>
            </div>
          </div>


          <div className="info-card">
            <span>
              QUBITS
            </span>

            <strong>
              {qubits}
            </strong>

            <small>
              Quantum registers
            </small>
          </div>


          <div className="info-card">
            <span>
              DEPTH
            </span>

            <strong>
              {circuitDepth}
            </strong>

            <small>
              Sequential layers
            </small>
          </div>


          <div className="info-card">
            <span>
              GATES
            </span>

            <strong>
              {gateCount}
            </strong>

            <small>
              Circuit operations
            </small>
          </div>


          <div className="info-card">
            <span>
              SHOTS
            </span>

            <strong>
              {shots}
            </strong>

            <small>
              Measurement repetitions
            </small>
          </div>
        </aside>
      </div>


      <section className="results-panel">
        <div className="panel-heading">
          <div>
            <span>
              RESULTS
            </span>

            <h2>
              Measurement Results
            </h2>
          </div>

          {result && (
            <span className="result-success">
              EXECUTION COMPLETE
            </span>
          )}
        </div>


        {!result ? (
          <div className="results-empty">
            <div className="empty-icon">
              ◈
            </div>

            <h3>
              No execution yet
            </h3>

            <p>
              Build a circuit and press{" "}
              <strong>
                Run Circuit
              </strong>.
            </p>
          </div>
        ) : (
          <>
            <p>
              Job:{" "}
              <strong>
                {result.job_id}
              </strong>
            </p>

            <p>
              Backend:{" "}
              {result.backend_name ??
                result.backend_id ??
                "Local QVM"}
            </p>

            <ResultChart
              counts={
                result.counts
              }
              shots={
                result.shots
              }
            />
          </>
        )}
      </section>
    </div>
  );
}
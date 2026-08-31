import {
  useEffect,
  useMemo,
  useState,
} from "react";

import "./QuantumLab.css";

import {
  getBackends,
  runJob,
  submitJob,
} from "../services/api";

import type {
  QuantumBackend,
  QuantumJobResult,
} from "../types/quantum";

import CircuitGrid, {
  type CircuitGate,
} from "../components/CircuitGrid";

import GatePalette, {
  type GateType,
} from "../components/GatePalette";

import ResultChart from "../components/ResultChart";


export default function QuantumLab() {
  const [qubits, setQubits] = useState(2);

  const [shots, setShots] = useState(100);

  const [selectedGate, setSelectedGate] =
    useState<GateType>("H");

  const [gates, setGates] =
    useState<CircuitGate[]>([]);

  const [backends, setBackends] =
    useState<QuantumBackend[]>([]);

  const [selectedBackend, setSelectedBackend] =
    useState("");

  const [running, setRunning] =
    useState(false);

  const [jobId, setJobId] =
    useState<string | null>(null);

  const [result, setResult] =
    useState<QuantumJobResult | null>(null);

  const [error, setError] =
    useState<string | null>(null);


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


  const gateCount = gates.length;


  useEffect(() => {
    let mounted = true;

    async function loadBackends() {
      try {
        const response = await getBackends();

        if (mounted) {
          setBackends(response.backends);
        }
      } catch {
        /*
         * Automatic backend selection can still
         * be used if backend discovery fails.
         */
      }
    }

    void loadBackends();

    return () => {
      mounted = false;
    };
  }, []);


  useEffect(() => {
    setGates((current) =>
      current.filter(
        (gate) =>
          gate.qubit < qubits &&
          (
            gate.targetQubit === undefined ||
            gate.targetQubit < qubits
          ),
      ),
    );
  }, [qubits]);


  function addGate(
    qubit: number,
    column: number,
  ) {
    if (selectedGate === "CNOT") {
      /*
       * CNOT requires a control and target qubit.
       *
       * For the MVP we automatically use the
       * next qubit as the target.
       */
      const targetQubit =
        qubit + 1 < qubits
          ? qubit + 1
          : qubit - 1;

      if (targetQubit < 0) {
        setError(
          "CNOT requires at least 2 qubits.",
        );

        return;
      }

      const occupied = gates.some(
        (gate) =>
          gate.column === column &&
          (
            gate.qubit === qubit ||
            gate.qubit === targetQubit ||
            gate.targetQubit === qubit ||
            gate.targetQubit === targetQubit
          ),
      );

      if (occupied) {
        return;
      }

      const gate: CircuitGate = {
        id: `${Date.now()}-${Math.random()}`,
        type: "CNOT",
        qubit,
        targetQubit,
        column,
      };

      setGates((current) => [
        ...current,
        gate,
      ]);

      setResult(null);
      setJobId(null);
      setError(null);

      return;
    }


    const occupied =
      gates.some(
        (gate) =>
          gate.qubit === qubit &&
          gate.column === column,
      );

    if (occupied) {
      return;
    }


    if (selectedGate === "M") {
      const existingMeasurement =
        gates.some(
          (gate) =>
            gate.qubit === qubit &&
            gate.type === "M",
        );

      if (existingMeasurement) {
        return;
      }
    }


    const gate: CircuitGate = {
      id: `${Date.now()}-${Math.random()}`,
      type: selectedGate,
      qubit,
      column,
    };


    setGates((current) => [
      ...current,
      gate,
    ]);

    setResult(null);
    setJobId(null);
    setError(null);
  }


  function clearCircuit() {
    setGates([]);
    setResult(null);
    setJobId(null);
    setError(null);
  }


  /*
   * Bell state:
   *
   * |00>
   *  |
   * H q0
   *  |
   * CX q0 -> q1
   *  |
   * measure
   *
   * Expected result:
   *
   * approximately 50% 00
   * approximately 50% 11
   */
  function loadBellState() {
    setQubits(2);

    setGates([
      {
        id: "bell-h",
        type: "H",
        qubit: 0,
        column: 0,
      },
      {
        id: "bell-cx",
        type: "CNOT",
        qubit: 0,
        targetQubit: 1,
        column: 1,
      },
      {
        id: "bell-m0",
        type: "M",
        qubit: 0,
        column: 3,
      },
      {
        id: "bell-m1",
        type: "M",
        qubit: 1,
        column: 3,
      },
    ]);

    setResult(null);
    setJobId(null);
    setError(null);
  }


  function removeGate(
    qubit: number,
    column: number,
  ) {
    setGates((current) =>
      current.filter(
        (gate) =>
          !(
            gate.qubit === qubit &&
            gate.column === column
          ),
      ),
    );

    setResult(null);
    setJobId(null);
    setError(null);
  }


  /*
   * Convert the visual circuit into the
   * QuantumOS parser format.
   */
  function buildProgram(): string {
    const sorted =
      [...gates].sort(
        (a, b) => {
          if (a.column !== b.column) {
            return a.column - b.column;
          }

          return a.qubit - b.qubit;
        },
      );


    const operationLines =
      sorted
        .filter(
          (gate) =>
            gate.type !== "M",
        )
        .map((gate) => {
          if (
            gate.type === "CNOT"
          ) {
            if (
              gate.targetQubit ===
              undefined
            ) {
              throw new Error(
                "CNOT is missing its target qubit.",
              );
            }

            return (
              `cx ${gate.qubit} ` +
              `${gate.targetQubit}`
            );
          }

          return (
            `${gate.type.toLowerCase()} ` +
            `${gate.qubit}`
          );
        });


    const hasMeasurement =
      gates.some(
        (gate) =>
          gate.type === "M",
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


  async function executeCircuit() {
    if (gates.length === 0) {
      setError(
        "Add at least one gate before running the circuit.",
      );

      return;
    }


    try {
      setRunning(true);
      setError(null);
      setResult(null);
      setJobId(null);


      const program =
        buildProgram();


      console.log(
        "QuantumOS program:",
        program,
      );


      const submission =
        await submitJob({
          circuit: program,
          shots,
          priority: 0,
          backend:
            selectedBackend ||
            null,
          metadata: {
            source:
              "quantumos-dashboard",
            qubits,
            circuit_depth:
              circuitDepth,
            gate_count:
              gateCount,
            program,
          },
        });


      setJobId(
        submission.job_id,
      );


      const execution =
        await runJob(
          submission.job_id,
        );


      setResult(execution);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Circuit execution failed.",
      );
    } finally {
      setRunning(false);
    }
  }


  return (
    <div className="quantum-lab">

      <div className="lab-header">

        <div>
          <span className="lab-kicker">
            QUANTUM WORKLOAD
          </span>

          <h1>
            Quantum Lab
          </h1>

          <p>
            Build, simulate, and measure
            quantum circuits using the
            QuantumOS runtime.
          </p>
        </div>


        <div className="lab-controls">

          <label>
            Qubits

            <select
              value={qubits}
              onChange={(event) => {
                setQubits(
                  Number(
                    event.target.value,
                  ),
                );

                setResult(null);
                setJobId(null);
                setError(null);
              }}
            >
              <option value={1}>
                1
              </option>

              <option value={2}>
                2
              </option>

              <option value={3}>
                3
              </option>

              <option value={4}>
                4
              </option>

              <option value={8}>
                8
              </option>
            </select>
          </label>


          <label>
            Shots

            <select
              value={shots}
              onChange={(event) => {
                setShots(
                  Number(
                    event.target.value,
                  ),
                );

                setResult(null);
                setJobId(null);
              }}
            >
              <option value={10}>
                10
              </option>

              <option value={100}>
                100
              </option>

              <option value={1000}>
                1,000
              </option>

              <option value={10000}>
                10,000
              </option>
            </select>
          </label>


          <label>
            Backend

            <select
              value={selectedBackend}
              onChange={(event) => {
                setSelectedBackend(
                  event.target.value,
                );

                setResult(null);
                setJobId(null);
              }}
            >
              <option value="">
                Automatic
              </option>

              {backends.map(
                (backend) => (
                  <option
                    key={
                      backend.backend_id
                    }
                    value={
                      backend.backend_id
                    }
                  >
                    {backend.name}
                  </option>
                ),
              )}
            </select>
          </label>

        </div>
      </div>


      {error && (
        <section className="error-card">

          <strong>
            Circuit Execution Error
          </strong>

          <p>
            {error}
          </p>

        </section>
      )}


      <section className="gate-panel">

        <h2>
          Quantum Gates
        </h2>

        <GatePalette
          selectedGate={
            selectedGate
          }
          onSelect={(gate) => {
            setSelectedGate(gate);
            setError(null);
          }}
        />

        <p className="hint">
          Select a gate, then click an
          empty circuit cell to place it.
          CNOT automatically connects
          the selected qubit to the next
          available qubit.
        </p>

      </section>


      <section className="circuit-panel">

        <div className="section-header">

          <div>

            <span className="lab-kicker">
              CIRCUIT
            </span>

            <h2>
              Your Quantum Circuit
            </h2>

          </div>


          <div>

            <button
              type="button"
              className="secondary-button"
              onClick={
                loadBellState
              }
            >
              Load Bell Example
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

          </div>

        </div>


        <CircuitGrid
          qubits={qubits}
          columns={columns}
          gates={gates}
          onCellClick={(
            qubit,
            column,
          ) => {

            const existing =
              gates.find(
                (gate) =>
                  gate.qubit === qubit &&
                  gate.column === column,
              );


            if (existing) {
              removeGate(
                qubit,
                column,
              );
            } else {
              addGate(
                qubit,
                column,
              );
            }
          }}
        />

      </section>


      <section className="run-panel">

        <div>

          <span className="lab-kicker">
            EXECUTION
          </span>

          <h2>
            Run Circuit
          </h2>

          <p>
            Submit the circuit to the
            QuantumOS runtime and execute
            it using the selected number
            of shots.
          </p>

          {jobId && (
            <small>
              Job: {jobId}
            </small>
          )}

        </div>


        <button
          type="button"
          className="run-button"
          onClick={
            executeCircuit
          }
          disabled={running}
        >
          {running
            ? "Executing..."
            : "Run Quantum Circuit"}
        </button>

      </section>


      {result && (
        <section className="result-panel">

          <span className="lab-kicker">
            QVM RESULT
          </span>

          <h2>
            Measurement Results
          </h2>

          <p>
            Backend:{" "}
            {result.backend_name ??
              result.backend_id ??
              "Local QVM"}
          </p>

          <p>
            Shots: {result.shots}
          </p>

          <ResultChart
            counts={
              result.counts
            }
            shots={
              result.shots
            }
          />

        </section>
      )}

    </div>
  );
}
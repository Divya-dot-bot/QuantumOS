import { useState } from "react";
import CircuitGate from "./CircuitGate";
import type {
  Circuit,
  Gate,
  GateType,
} from "../types/quantum";

interface CircuitEditorProps {
  circuit: Circuit;
  onChange: (circuit: Circuit) => void;
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

export default function CircuitEditor({
  circuit,
  onChange,
}: CircuitEditorProps) {
  const [selectedGate, setSelectedGate] =
    useState<GateType>("H");

  function addGate(
    qubit: number,
    column: number
  ) {
    const exists = circuit.gates.some(
      (gate) =>
        gate.qubit === qubit &&
        gate.column === column
    );

    if (exists) {
      return;
    }

    const gate: Gate = {
      id: crypto.randomUUID(),
      type: selectedGate,
      qubit,
      column,
    };

    onChange({
      ...circuit,
      gates: [...circuit.gates, gate],
    });
  }

  function removeGate(id: string) {
    onChange({
      ...circuit,
      gates: circuit.gates.filter(
        (gate) => gate.id !== id
      ),
    });
  }

  function clearCircuit() {
    onChange({
      ...circuit,
      gates: [],
    });
  }

  return (
    <section className="lab-panel">
      <div className="panel-heading">
        <div>
          <span className="panel-kicker">
            CIRCUIT BUILDER
          </span>

          <h2>{circuit.name}</h2>

          <p>
            Click an empty cell to place a quantum gate.
          </p>
        </div>

        <button
          className="secondary-button"
          onClick={clearCircuit}
        >
          Clear
        </button>
      </div>

      <div className="gate-toolbar">
        {GATES.map((gate) => (
          <button
            key={gate}
            className={
              selectedGate === gate
                ? "gate-selector selected"
                : "gate-selector"
            }
            onClick={() => setSelectedGate(gate)}
          >
            {gate}
          </button>
        ))}
      </div>

      <div className="circuit-wrapper">
        <div className="circuit-grid">
          {Array.from(
            { length: circuit.qubits },
            (_, qubit) => (
              <div
                className="circuit-row"
                key={qubit}
              >
                <div className="qubit-label">
                  q{qubit}
                </div>

                {Array.from(
                  { length: circuit.depth },
                  (_, column) => {
                    const gate =
                      circuit.gates.find(
                        (item) =>
                          item.qubit === qubit &&
                          item.column === column
                      );

                    return (
                      <div
                        className="circuit-cell"
                        key={`${qubit}-${column}`}
                        onClick={() =>
                          !gate &&
                          addGate(
                            qubit,
                            column
                          )
                        }
                      >
                        <div className="wire" />

                        {gate && (
                          <CircuitGate
                            gate={gate}
                            onRemove={
                              removeGate
                            }
                          />
                        )}
                      </div>
                    );
                  }
                )}
              </div>
            )
          )}
        </div>
      </div>

      <div className="circuit-help">
        Selected gate:{" "}
        <strong>{selectedGate}</strong>
        <span>
          Click a gate to remove it.
        </span>
      </div>
    </section>
  );
}
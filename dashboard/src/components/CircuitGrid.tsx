import type { FC } from "react";

import type { CircuitGate } from "../types/quantum";

export type { CircuitGate };

interface CircuitGridProps {
  qubits: number;
  columns: number;
  gates: CircuitGate[];
  onCellClick: (
    qubit: number,
    column: number,
  ) => void;
}

const CircuitGrid: FC<CircuitGridProps> = ({
  qubits,
  columns,
  gates,
  onCellClick,
}) => {
  function getGate(
    qubit: number,
    column: number,
  ): CircuitGate | undefined {
    return gates.find(
      (gate) =>
        gate.column === column &&
        (
          gate.qubit === qubit ||
          (
            gate.type === "CNOT" &&
            gate.targetQubit === qubit
          )
        ),
    );
  }

  return (
    <div className="circuit-grid">
      <div className="circuit-header-row">
        <div className="qubit-label">
          Qubit
        </div>

        {Array.from(
          { length: columns },
          (_, column) => (
            <div
              className="circuit-column-label"
              key={column}
            >
              {column}
            </div>
          ),
        )}
      </div>

      {Array.from(
        { length: qubits },
        (_, qubit) => (
          <div
            className="circuit-row"
            key={qubit}
          >
            <div className="qubit-label">
              q{qubit}
            </div>

            {Array.from(
              { length: columns },
              (_, column) => {
                const gate = getGate(
                  qubit,
                  column,
                );

                const isCnotControl =
                  gate?.type === "CNOT" &&
                  gate.qubit === qubit;

                const isCnotTarget =
                  gate?.type === "CNOT" &&
                  gate.targetQubit === qubit;

                return (
                  <button
                    type="button"
                    className={
                      gate
                        ? "circuit-cell occupied"
                        : "circuit-cell"
                    }
                    key={column}
                    onClick={() =>
                      onCellClick(
                        qubit,
                        column,
                      )
                    }
                    aria-label={
                      gate
                        ? `${gate.type} at qubit ${qubit}, column ${column}`
                        : `Empty circuit cell at qubit ${qubit}, column ${column}`
                    }
                  >
                    {isCnotControl ? (
                      <span className="cnot-control">
                        ●
                      </span>
                    ) : isCnotTarget ? (
                      <span className="cnot-target">
                        ⊕
                      </span>
                    ) : gate ? (
                      <span className="gate-token">
                        {gate.type}
                      </span>
                    ) : (
                      <span className="cell-dot">
                        +
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
  );
};

export default CircuitGrid;
import type { FC } from "react";

import type {
  GateType,
} from "../types/quantum";

export type { GateType };

interface GatePaletteProps {
  selectedGate: GateType;
  onSelect: (
    gate: GateType,
  ) => void;
}

const gates: GateType[] = [
  "H",
  "X",
  "Y",
  "Z",
  "S",
  "T",
  "CNOT",
  "M",
];

const GatePalette: FC<GatePaletteProps> = ({
  selectedGate,
  onSelect,
}) => {
  return (
    <div className="gate-palette">
      {gates.map((gate) => (
        <button
          type="button"
          key={gate}
          className={
            selectedGate === gate
              ? "gate-button selected"
              : "gate-button"
          }
          onClick={() => onSelect(gate)}
        >
          <strong>
            {gate === "CNOT"
              ? "CX"
              : gate}
          </strong>
        </button>
      ))}
    </div>
  );
};

export default GatePalette;
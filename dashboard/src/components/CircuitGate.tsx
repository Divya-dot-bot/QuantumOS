import type { Gate } from "../types/quantum";

interface CircuitGateProps {
  gate: Gate;
  onRemove?: (id: string) => void;
}

export default function CircuitGate({
  gate,
  onRemove,
}: CircuitGateProps) {
  return (
    <button
      className={`circuit-gate gate-${gate.type.toLowerCase()}`}
      title={`Gate ${gate.type}`}
      onClick={() => onRemove?.(gate.id)}
    >
      {gate.type}
    </button>
  );
}
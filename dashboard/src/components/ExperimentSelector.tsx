interface ExperimentSelectorProps {
  value: string;
  onChange: (value: string) => void;
}

const experiments = [
  {
    id: "coin",
    title: "Quantum Coin Flip",
    description:
      "Create a 50/50 superposition and measure it.",
    icon: "◐",
  },
  {
    id: "bell",
    title: "Bell State",
    description:
      "Create two entangled qubits.",
    icon: "∞",
  },
  {
    id: "superposition",
    title: "Superposition",
    description:
      "Place a qubit into quantum superposition.",
    icon: "Ψ",
  },
  {
    id: "ghz",
    title: "GHZ State",
    description:
      "Create a simple multi-qubit entangled state.",
    icon: "Q",
  },
  {
    id: "custom",
    title: "Custom Circuit",
    description:
      "Build your own small quantum circuit.",
    icon: "⌘",
  },
];

export default function ExperimentSelector({
  value,
  onChange,
}: ExperimentSelectorProps) {
  return (
    <section className="experiment-selector">
      <div className="panel-heading">
        <div>
          <span className="panel-kicker">
            EXPERIMENT
          </span>

          <h2>What do you want to run?</h2>

          <p>
            Choose an experiment or create your own
            circuit.
          </p>
        </div>
      </div>

      <div className="experiment-grid">
        {experiments.map((experiment) => (
          <button
            key={experiment.id}
            className={
              value === experiment.id
                ? "experiment-card active"
                : "experiment-card"
            }
            onClick={() =>
              onChange(experiment.id)
            }
          >
            <span className="experiment-icon">
              {experiment.icon}
            </span>

            <span className="experiment-title">
              {experiment.title}
            </span>

            <span className="experiment-description">
              {experiment.description}
            </span>
          </button>
        ))}
      </div>
    </section>
  );
}
interface ExecutionPanelProps {
  shots: number;
  backend: string;
  running: boolean;
  onShotsChange: (shots: number) => void;
  onBackendChange: (backend: string) => void;
  onRun: () => void;
}

export default function ExecutionPanel({
  shots,
  backend,
  running,
  onShotsChange,
  onBackendChange,
  onRun,
}: ExecutionPanelProps) {
  return (
    <section className="execution-panel">
      <div>
        <span className="panel-kicker">
          EXECUTION
        </span>

        <h2>Run on QuantumOS</h2>

        <p>
          Configure the experiment and send it to
          the QuantumOS runtime.
        </p>
      </div>

      <div className="execution-controls">
        <label>
          <span>Shots</span>

          <input
            type="number"
            min={1}
            max={100000}
            value={shots}
            onChange={(event) =>
              onShotsChange(
                Math.max(
                  1,
                  Number(event.target.value)
                )
              )
            }
          />
        </label>

        <label>
          <span>Backend</span>

          <select
            value={backend}
            onChange={(event) =>
              onBackendChange(
                event.target.value
              )
            }
          >
            <option value="qvm">
              Quantum Virtual Machine
            </option>
          </select>
        </label>

        <button
          className="run-button"
          disabled={running}
          onClick={onRun}
        >
          {running
            ? "Running..."
            : "Run Experiment"}
        </button>
      </div>
    </section>
  );
}
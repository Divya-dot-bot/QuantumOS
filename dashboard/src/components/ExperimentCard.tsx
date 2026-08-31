import ResultsChart from "./ResultChart";
import type {
  QuantumResult,
} from "../types/quantum";

interface ExperimentCardProps {
  result: QuantumResult;
}

export default function ExperimentCard({
  result,
}: ExperimentCardProps) {
  return (
    <section className="lab-panel result-panel">
      <div className="panel-heading">
        <div>
          <span className="panel-kicker">
            RESULT
          </span>

          <h2>Experiment Complete</h2>

          <p>{result.experiment}</p>
        </div>

        <span className="result-status">
          {result.status.toUpperCase()}
        </span>
      </div>

      <div className="result-metadata">
        <div>
          <span>JOB</span>
          <strong>{result.job_id}</strong>
        </div>

        <div>
          <span>BACKEND</span>
          <strong>{result.backend}</strong>
        </div>

        <div>
          <span>SHOTS</span>
          <strong>{result.shots}</strong>
        </div>

        <div>
          <span>EXECUTION</span>
          <strong>
            {result.execution_time_ms} ms
          </strong>
        </div>
      </div>

      <div className="results-section">
        <div className="results-title">
          Measurement Results
        </div>

        <ResultsChart
          results={result.results}
        />
      </div>
    </section>
  );
}

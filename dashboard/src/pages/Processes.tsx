import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  getJobs,
  getJobHistory,
  type Job,
  type ExecutionHistory,
} from "../services/api";

export default function Processes() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [history, setHistory] = useState<
    ExecutionHistory[]
  >([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(
    null,
  );

  const loadProcesses = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const [jobsResponse, historyResponse] =
        await Promise.all([
          getJobs(),
          getJobHistory(),
        ]);

      setJobs(
        Array.isArray(jobsResponse)
          ? jobsResponse
          : [],
      );

      setHistory(
        Array.isArray(historyResponse)
          ? historyResponse
          : [],
      );
    } catch (err) {
      console.error(
        "QuantumOS Processes load error:",
        err,
      );

      setError(
        err instanceof Error
          ? err.message
          : "Unable to load quantum processes.",
      );

      setJobs([]);
      setHistory([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadProcesses();

    const interval = window.setInterval(() => {
      void loadProcesses();
    }, 5000);

    return () => {
      window.clearInterval(interval);
    };
  }, [loadProcesses]);

  const activeJobs = useMemo(() => {
    return Array.isArray(jobs) ? jobs : [];
  }, [jobs]);

  const completedExecutions = useMemo(() => {
    return Array.isArray(history)
      ? history.filter(
          (execution) =>
            execution &&
            typeof execution === "object" &&
            execution.result,
        )
      : [];
  }, [history]);

  const queuedJobs = useMemo(() => {
    return activeJobs.filter(
      (job) =>
        typeof job?.status === "string" &&
        job.status.toLowerCase() === "queued",
    );
  }, [activeJobs]);

  const runningJobs = useMemo(() => {
    return activeJobs.filter(
      (job) =>
        typeof job?.status === "string" &&
        job.status.toLowerCase() === "running",
    );
  }, [activeJobs]);

  const failedJobs = useMemo(() => {
    return activeJobs.filter(
      (job) =>
        typeof job?.status === "string" &&
        job.status.toLowerCase() === "failed",
    );
  }, [activeJobs]);

  /*
   * Active jobs + completed execution history.
   *
   * Completed jobs leave /api/jobs and remain in
   * /api/jobs/history/all, so they must be counted
   * from history.
   */
  const totalJobs =
    activeJobs.length +
    completedExecutions.length;

  return (
    <main className="dashboard-page">
      <section className="page-header">
        <div>
          <span className="page-kicker">
            QUANTUM RUNTIME
          </span>

          <h1>Processes</h1>

          <p>
            Monitor submitted, running, and
            completed quantum workloads.
          </p>
        </div>

        <button
          type="button"
          onClick={() => void loadProcesses()}
          disabled={loading}
        >
          {loading ? "Refreshing..." : "Refresh"}
        </button>
      </section>

      {error && (
        <section className="error-card">
          <strong>
            Unable to load processes
          </strong>

          <p>{error}</p>

          <button
            type="button"
            onClick={() => void loadProcesses()}
          >
            Try Again
          </button>
        </section>
      )}

      <section className="stats-grid">
        <article className="stat-card">
          <span>TOTAL JOBS</span>

          <strong>{totalJobs}</strong>

          <small>
            Current + completed
          </small>
        </article>

        <article className="stat-card">
          <span>QUEUED</span>

          <strong>
            {queuedJobs.length}
          </strong>

          <small>
            Waiting for execution
          </small>
        </article>

        <article className="stat-card">
          <span>RUNNING</span>

          <strong>
            {runningJobs.length}
          </strong>

          <small>
            Currently executing
          </small>
        </article>

        <article className="stat-card">
          <span>COMPLETED</span>

          <strong>
            {completedExecutions.length}
          </strong>

          <small>
            Finished executions
          </small>
        </article>

        <article className="stat-card">
          <span>FAILED</span>

          <strong>
            {failedJobs.length}
          </strong>

          <small>
            Current failed jobs
          </small>
        </article>
      </section>

      <section className="panel">
        <div className="panel-header">
          <div>
            <span className="panel-kicker">
              JOB MANAGER
            </span>

            <h2>Quantum Processes</h2>
          </div>

          <span>{totalJobs}</span>
        </div>

        {loading ? (
          <div className="empty-state">
            Loading quantum processes...
          </div>
        ) : totalJobs === 0 ? (
          <div className="empty-state">
            No quantum jobs have been
            submitted yet.
          </div>
        ) : (
          <div className="job-list">
            {/* -------------------------------------------------
                ACTIVE JOBS
            ------------------------------------------------- */}

            {activeJobs.map((job: Job) => {
              const status =
                typeof job.status === "string"
                  ? job.status.toLowerCase()
                  : "unknown";

              const statusClass =
                status === "failed"
                  ? "busy"
                  : status === "running"
                    ? "busy"
                    : "available";

              return (
                <article
                  className="job-row"
                  key={`active-${job.job_id}`}
                >
                  <div>
                    <strong>
                      {job.job_id}
                    </strong>

                    <small>
                      {job.shots ?? 0} shots
                      {" · "}
                      priority{" "}
                      {job.priority ?? 0}
                    </small>
                  </div>

                  <div>
                    <span>
                      {job.backend ??
                        "Automatic backend"}
                    </span>
                  </div>

                  <span
                    className={`status ${statusClass}`}
                  >
                    {status.toUpperCase()}
                  </span>
                </article>
              );
            })}

            {/* -------------------------------------------------
                COMPLETED JOB HISTORY
            ------------------------------------------------- */}

            {completedExecutions
              .slice()
              .reverse()
              .map(
                (
                  execution: ExecutionHistory,
                ) => {
                  const result =
                    execution.result;

                  return (
                    <article
                      className="job-row"
                      key={`history-${execution.job_id}`}
                    >
                      <div>
                        <strong>
                          {execution.job_id}
                        </strong>

                        <small>
                          {result?.shots ?? 0}
                          {" shots · "}
                          worker{" "}
                          {execution.worker_id ??
                            "unknown"}
                        </small>
                      </div>

                      <div>
                        <span>
                          {execution.backend_name ??
                            execution.backend_id ??
                            "Unknown backend"}
                        </span>
                      </div>

                      <span className="status available">
                        COMPLETED
                      </span>
                    </article>
                  );
                },
              )}
          </div>
        )}
      </section>
    </main>
  );
}
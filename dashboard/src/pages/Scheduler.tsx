import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  getJobs,
  getSchedulerStatus,
  type Job,
  type SchedulerStatus,
} from "../services/api";

export default function Scheduler() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [scheduler, setScheduler] =
    useState<SchedulerStatus | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // ---------------------------------------------------------------------------
  // Load scheduler data
  // ---------------------------------------------------------------------------

  const loadScheduler = useCallback(async () => {
    try {
      setError(null);

      const [jobsData, schedulerData] =
        await Promise.all([
          getJobs(),
          getSchedulerStatus(),
        ]);

      setJobs(
        Array.isArray(jobsData)
          ? jobsData
          : [],
      );

      setScheduler(
        schedulerData &&
        typeof schedulerData === "object"
          ? schedulerData
          : null,
      );
    } catch (err) {
      setJobs([]);
      setScheduler(null);

      setError(
        err instanceof Error
          ? err.message
          : "Failed to load scheduler state.",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  // ---------------------------------------------------------------------------
  // Initial load + automatic refresh
  // ---------------------------------------------------------------------------

  useEffect(() => {
    void loadScheduler();

    const interval = window.setInterval(() => {
      void loadScheduler();
    }, 5000);

    return () => {
      window.clearInterval(interval);
    };
  }, [loadScheduler]);

  // ---------------------------------------------------------------------------
  // Derived state
  // ---------------------------------------------------------------------------

  const safeJobs = useMemo(
    () =>
      Array.isArray(jobs)
        ? jobs
        : [],
    [jobs],
  );

  const queuedJobs = useMemo(
    () =>
      safeJobs.filter(
        (job) =>
          typeof job?.status === "string" &&
          job.status.toLowerCase() ===
            "queued",
      ),
    [safeJobs],
  );

  const priorityJobs = useMemo(
    () =>
      [...queuedJobs].sort(
        (a, b) =>
          (b.priority ?? 0) -
          (a.priority ?? 0),
      ),
    [queuedJobs],
  );

  const runtimeStatus =
    typeof scheduler?.runtime_status ===
    "string"
      ? scheduler.runtime_status
      : "unknown";

  const policy =
    typeof scheduler?.policy === "string"
      ? scheduler.policy
      : "unknown";

  const queueSize =
    typeof scheduler?.queue_size ===
    "number"
      ? scheduler.queue_size
      : queuedJobs.length;

  const jobsSubmitted =
    typeof scheduler?.jobs_submitted ===
    "number"
      ? scheduler.jobs_submitted
      : 0;

  const jobsDispatched =
    typeof scheduler?.jobs_dispatched ===
    "number"
      ? scheduler.jobs_dispatched
      : 0;

  const lastDecision =
    typeof scheduler?.last_decision ===
    "string"
      ? scheduler.last_decision
      : null;

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------

  return (
    <main className="dashboard-page">
      {/* ------------------------------------------------------------------ */}
      {/* Header */}
      {/* ------------------------------------------------------------------ */}

      <section className="page-header">
        <div>
          <span className="page-kicker">
            WORKLOAD ORCHESTRATION
          </span>

          <h1>Scheduler</h1>

          <p>
            Monitor QuantumOS workload
            scheduling, queue state, and
            dispatch activity.
          </p>
        </div>

        <button
          type="button"
          onClick={() => void loadScheduler()}
          disabled={loading}
        >
          {loading
            ? "Refreshing..."
            : "Refresh"}
        </button>
      </section>

      {/* ------------------------------------------------------------------ */}
      {/* Error */}
      {/* ------------------------------------------------------------------ */}

      {error && (
        <section className="error-card">
          <strong>
            Scheduler unavailable
          </strong>

          <p>{error}</p>

          <button
            type="button"
            onClick={() => void loadScheduler()}
          >
            Try Again
          </button>
        </section>
      )}

      {/* ------------------------------------------------------------------ */}
      {/* Statistics */}
      {/* ------------------------------------------------------------------ */}

      <section className="stats-grid">
        <article className="stat-card">
          <span>RUNTIME STATUS</span>

          <strong>
            {runtimeStatus.toUpperCase()}
          </strong>

          <small>
            QuantumOS runtime
          </small>
        </article>

        <article className="stat-card">
          <span>SCHEDULING POLICY</span>

          <strong>
            {policy.toUpperCase()}
          </strong>

          <small>
            Active scheduling policy
          </small>
        </article>

        <article className="stat-card">
          <span>QUEUE DEPTH</span>

          <strong>
            {queueSize}
          </strong>

          <small>
            Currently waiting
          </small>
        </article>

        <article className="stat-card">
          <span>JOBS SUBMITTED</span>

          <strong>
            {jobsSubmitted}
          </strong>

          <small>
            Total scheduler submissions
          </small>
        </article>

        <article className="stat-card">
          <span>JOBS DISPATCHED</span>

          <strong>
            {jobsDispatched}
          </strong>

          <small>
            Total dispatched jobs
          </small>
        </article>
      </section>

      {/* ------------------------------------------------------------------ */}
      {/* Scheduling queue */}
      {/* ------------------------------------------------------------------ */}

      <section className="panel">
        <div className="panel-header">
          <div>
            <span className="panel-kicker">
              QUEUE
            </span>

            <h2>Scheduling Queue</h2>
          </div>

          <span>{queueSize}</span>
        </div>

        {loading ? (
          <div className="empty-state">
            Loading scheduler queue...
          </div>
        ) : priorityJobs.length === 0 ? (
          <div className="empty-state">
            No jobs are currently waiting in
            the scheduler queue.
          </div>
        ) : (
          <div className="job-list">
            {priorityJobs.map(
              (job, index) => (
                <article
                  className="job-row"
                  key={job.job_id}
                >
                  <div>
                    <strong>
                      #{index + 1}{" "}
                      {job.job_id}
                    </strong>

                    <small>
                      {job.shots ?? 0} shots
                    </small>
                  </div>

                  <span>
                    Priority{" "}
                    {job.priority ?? 0}
                  </span>

                  <span>
                    {job.backend ??
                      "Automatic selection"}
                  </span>

                  <span className="status available">
                    QUEUED
                  </span>
                </article>
              ),
            )}
          </div>
        )}
      </section>

      {/* ------------------------------------------------------------------ */}
      {/* Decision engine */}
      {/* ------------------------------------------------------------------ */}

      <section className="panel">
        <div className="panel-header">
          <div>
            <span className="panel-kicker">
              DECISION ENGINE
            </span>

            <h2>
              Last Scheduling Decision
            </h2>
          </div>
        </div>

        <div className="architecture">
          {lastDecision ? (
            <>
              <strong>
                {lastDecision}
              </strong>

              <p>
                Most recently selected job by
                the active scheduler policy.
              </p>
            </>
          ) : (
            <>
              <strong>
                No scheduling decision yet
              </strong>

              <p>
                The scheduler has not selected
                a job during the current runtime.
              </p>
            </>
          )}
        </div>
      </section>

      {/* ------------------------------------------------------------------ */}
      {/* Architecture */}
      {/* ------------------------------------------------------------------ */}

      <section className="architecture">
        <span className="panel-kicker">
          RESEARCH MODE
        </span>

        <h2>
          QuantumOS Scheduling Architecture
        </h2>

        <p>
          The current runtime uses a
          configurable scheduling policy.
          FIFO is currently active, while the
          scheduler architecture supports
          future priority, shortest-job,
          circuit-aware, and
          optimization-based scheduling
          experiments.
        </p>
      </section>
    </main>
  );
}
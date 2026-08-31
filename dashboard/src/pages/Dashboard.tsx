import {
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  getDashboardData,
} from "../services/api";

import type {
  DashboardData,
} from "../services/api";

import EmptyState from "../components/EmptyState";
import StatusIndicator from "../components/StatusIndicator";


export default function Dashboard() {
  const [data, setData] =
    useState<DashboardData | null>(
      null,
    );

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);


  const loadDashboard =
    useCallback(async () => {
      try {
        setLoading(true);
        setError(null);

        const dashboardData =
          await getDashboardData();

        setData(
          dashboardData,
        );
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Unable to load QuantumOS.",
        );
      } finally {
        setLoading(false);
      }
    }, []);


  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);


  const backends =
  data?.backends ?? [];

  const jobs =
    data?.jobs ?? [];


  const availableBackends =
  backends.filter(
    (backend) =>
      !backend.is_busy &&
      backend.status?.toLowerCase() ===
        "available",
  ).length;


  return (
    <main className="dashboard-page">
      <section className="page-header">
        <div>
          <span className="page-kicker">
            QUANTUM COMPUTING PLATFORM
          </span>

          <h1>
            QuantumOS
          </h1>

          <p>
            Local quantum workload
            control center.
          </p>
        </div>

        <button
          type="button"
          onClick={loadDashboard}
          disabled={loading}
        >
          {loading
            ? "Refreshing..."
            : "Refresh"}
        </button>
      </section>


      {error && (
        <section className="error-card">
          <strong>
            API Connection Error
          </strong>

          <p>
            {error}
          </p>
        </section>
      )}


      <section className="stats-grid">
        <article className="stat-card">
          <span>
            SYSTEM
          </span>

          <strong>
            {data?.health?.status
             ?.toUpperCase() ??
              "OFFLINE"}
          </strong>

          <small>
            QuantumOS API
          </small>
        </article>


        <article className="stat-card">
          <span>
            BACKENDS
          </span>

          <strong>
            {backends.length}
          </strong>

          <small>
            {availableBackends} available
          </small>
        </article>


        <article className="stat-card">
          <span>
            QUEUED JOBS
          </span>

          <strong>
            {jobs.length}
          </strong>

          <small>
            Current workload
          </small>
        </article>


        <article className="stat-card">
          <span>
            API VERSION
          </span>

          <strong>
            {data?.health?.version ??
              "—"}
          </strong>

          <small>
            Current release
          </small>
        </article>
      </section>


      <section className="panel">
        <div className="panel-header">
          <div>
            <span className="panel-kicker">
              COMPUTE
            </span>

            <h2>
              Quantum Backends
            </h2>
          </div>

          <span>
            {backends.length}
          </span>
        </div>


        {loading ? (
          <EmptyState
            title="Loading quantum backends..."
          />
        ) : backends.length === 0 ? (
          <EmptyState
            title="No quantum backends registered."
          />
        ) : (
          <div className="backend-list">
            {backends.map(
              (backend) => (
                <article
                  className="backend-row"
                  key={
                    backend.backend_id
                  }
                >
                  <div>
                    <strong>
                      {backend.name}
                    </strong>

                    <small>
                      {backend.backend_id}
                    </small>
                  </div>

                  <div>
                    <span>
                      {backend.num_qubits}
                      {" "}
                      qubits
                    </span>

                    <span>
                      {backend.resource_type}
                    </span>
                  </div>

                  <StatusIndicator
                    status={
                   backend.is_busy
                  ? "busy"
                     : backend.status ?? "unknown"
                     }

                  />
                </article>
              ),
            )}
          </div>
        )}
      </section>


      <section className="panel">
        <div className="panel-header">
          <div>
            <span className="panel-kicker">
              WORKLOAD
            </span>

            <h2>
              Quantum Jobs
            </h2>
          </div>

          <span>
            {jobs.length}
          </span>
        </div>


        {loading ? (
          <EmptyState
            title="Loading jobs..."
          />
        ) : jobs.length === 0 ? (
          <EmptyState
            title="No jobs currently queued."
            description="Open Quantum Lab to submit a circuit."
          />
        ) : (
          <div className="job-list">
            {jobs.map(
              (job) => (
                <article
                  className="job-row"
                  key={job.job_id}
                >
                  <div>
                    <strong>
                      {job.job_id}
                    </strong>

                    <small>
                      {job.shots} shots
                    </small>
                  </div>

                  <span>
                    Priority {job.priority}
                  </span>

                  <span>
                    {job.backend ??
                      "Auto"}
                  </span>

                  <StatusIndicator
                    status={job.status}
                  />
                </article>
              ),
            )}
          </div>
        )}
      </section>


      <section className="architecture">
        <span className="panel-kicker">
          SYSTEM ARCHITECTURE
        </span>

        <h2>
          QuantumOS Execution Pipeline
        </h2>

        <div className="architecture-flow">
          <div>
            <strong>
              API
            </strong>

            <small>
              HTTP Interface
            </small>
          </div>

          <span>→</span>

          <div>
            <strong>
              Job
            </strong>

            <small>
              Workload
            </small>
          </div>

          <span>→</span>

          <div>
            <strong>
              Scheduler
            </strong>

            <small>
              Dispatch
            </small>
          </div>

          <span>→</span>

          <div>
            <strong>
              Runtime
            </strong>

            <small>
              Execution
            </small>
          </div>

          <span>→</span>

          <div>
            <strong>
              QVM
            </strong>

            <small>
              Local Backend
            </small>
          </div>
        </div>
      </section>
    </main>
  );
}
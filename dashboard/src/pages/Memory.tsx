import { useCallback, useEffect, useState } from "react";

import {
  getResourceStats,
  getResources,
  type Resource,
  type ResourceStats,
} from "../services/api";


const EMPTY_STATS: ResourceStats = {
  total_resources: 0,
  available_resources: 0,
  busy_resources: 0,
  offline_resources: 0,
  maintenance_resources: 0,
  allocations: 0,
};


export default function Memory() {
  const [resources, setResources] =
    useState<Resource[]>([]);

  const [stats, setStats] =
    useState<ResourceStats>(EMPTY_STATS);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);


  const loadResources = useCallback(
    async () => {
      try {
        setLoading(true);
        setError(null);

        const [
          resourcesResponse,
          statsResponse,
        ] = await Promise.all([
          getResources(),
          getResourceStats(),
        ]);

        setResources(
          resourcesResponse.resources,
        );

        setStats(
          statsResponse,
        );
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Unable to load resources.",
        );
      } finally {
        setLoading(false);
      }
    },
    [],
  );


  useEffect(() => {
    void loadResources();

    const interval = window.setInterval(
      () => {
        void loadResources();
      },
      5000,
    );

    return () => {
      window.clearInterval(interval);
    };
  }, [loadResources]);


  return (
    <main className="dashboard-page">

      <section className="page-header">
        <div>
          <span className="page-kicker">
            RESOURCE MANAGER
          </span>

          <h1>
            Memory & Resources
          </h1>

          <p>
            Monitor quantum resources and
            runtime allocation state.
          </p>
        </div>

        <button
          type="button"
          onClick={loadResources}
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
            Resource API unavailable
          </strong>

          <p>{error}</p>
        </section>
      )}


      <section className="stats-grid">

        <article className="stat-card">
          <span>
            RESOURCES
          </span>

          <strong>
            {stats.total_resources}
          </strong>

          <small>
            Registered resources
          </small>
        </article>


        <article className="stat-card">
          <span>
            AVAILABLE
          </span>

          <strong>
            {stats.available_resources}
          </strong>

          <small>
            Ready for workloads
          </small>
        </article>


        <article className="stat-card">
          <span>
            BUSY
          </span>

          <strong>
            {stats.busy_resources}
          </strong>

          <small>
            Currently executing
          </small>
        </article>


        <article className="stat-card">
          <span>
            ALLOCATIONS
          </span>

          <strong>
            {stats.allocations}
          </strong>

          <small>
            Active job allocations
          </small>
        </article>


        <article className="stat-card">
          <span>
            OFFLINE
          </span>

          <strong>
            {stats.offline_resources}
          </strong>

          <small>
            Unavailable resources
          </small>
        </article>

      </section>


      <section className="panel">

        <div className="panel-header">

          <div>
            <span className="panel-kicker">
              RESOURCE TABLE
            </span>

            <h2>
              Quantum Resources
            </h2>
          </div>

          <span>
            {resources.length}
          </span>

        </div>


        {loading ? (

          <div className="empty-state">
            Loading resources...
          </div>

        ) : resources.length === 0 ? (

          <div className="empty-state">
            No resources are currently registered.
          </div>

        ) : (

          <div className="backend-list">

            {resources.map(
              (resource) => {

                const statusClass =
                  resource.status
                    .toLowerCase();

                return (
                  <article
                    className="backend-row"
                    key={
                      resource.resource_id
                    }
                  >

                    <div>
                      <strong>
                        {resource.name}
                      </strong>

                      <small>
                        {resource.resource_id}
                      </small>
                    </div>


                    <div>
                      <span>
                        {resource.num_qubits}{" "}
                        qubits
                      </span>

                      <span>
                        {resource.resource_type}
                      </span>
                    </div>


                    <div>
                      <span>
                        {resource
                          .supported_operations
                          .length}{" "}
                        operations
                      </span>
                    </div>


                    <span
                      className={`status ${statusClass}`}
                    >
                      {resource.status.toUpperCase()}
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
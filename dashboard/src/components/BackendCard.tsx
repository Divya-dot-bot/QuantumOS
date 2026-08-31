import type { Backend } from "../services/api";


interface BackendCardProps {
  backend: Backend;
}


function BackendCard({
  backend,
}: BackendCardProps) {
  const isBusy =
    backend.is_busy ||
    backend.status.toLowerCase() === "busy";

  const statusClass =
    isBusy
      ? "status busy"
      : "status available";

  const statusLabel =
    isBusy
      ? "BUSY"
      : backend.status.toUpperCase();


  return (
    <article className="backend-card">

      <div className="backend-card-header">

        <div>
          <span className="backend-type">
            {backend.resource_type}
          </span>

          <h3>
            {backend.name}
          </h3>

          <small>
            {backend.backend_id}
          </small>
        </div>

        <span className={statusClass}>
          {statusLabel}
        </span>

      </div>


      <div className="backend-card-specs">

        <div>
          <span>
            QUBITS
          </span>

          <strong>
            {backend.num_qubits}
          </strong>
        </div>


        <div>
          <span>
            OPERATIONS
          </span>

          <strong>
            {backend.supported_operations.length}
          </strong>
        </div>

      </div>


      {backend.supported_operations.length > 0 && (
        <div className="operation-list">

          {backend.supported_operations.map(
            (operation) => (
              <span
                key={operation}
                className="operation-tag"
              >
                {operation}
              </span>
            ),
          )}

        </div>
      )}

    </article>
  );
}


export default BackendCard;
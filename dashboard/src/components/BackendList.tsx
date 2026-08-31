/**
 * QuantumOS Dashboard
 *
 * Displays the collection of available quantum backends.
 */

import type { Backend } from "../services/api";
import BackendCard from "./BackendCard";
import LoadingState from "./LoadingState";


interface BackendListProps {
  backends: Backend[];
  loading?: boolean;
}


function BackendList({
  backends,
  loading = false,
}: BackendListProps) {
  if (loading) {
    return (
      <LoadingState
        message="Loading quantum backends..."
      />
    );
  }


  if (backends.length === 0) {
    return (
      <div className="empty-state">
        <strong>
          No quantum backends
        </strong>

        <span>
          QuantumOS currently has no registered
          execution backends.
        </span>
      </div>
    );
  }


  return (
    <div className="backend-list">
      {backends.map((backend) => (
        <BackendCard
          key={backend.backend_id}
          backend={backend}
        />
      ))}
    </div>
  );
}


export default BackendList;
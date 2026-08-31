/**
 * QuantumOS Dashboard
 *
 * Reusable loading-state component.
 */

interface LoadingStateProps {
  message?: string;
}


function LoadingState({
  message = "Loading QuantumOS...",
}: LoadingStateProps) {
  return (
    <div
      className="loading-state"
      role="status"
      aria-live="polite"
    >
      <span
        className="loading-spinner"
        aria-hidden="true"
      />

      <span>
        {message}
      </span>
    </div>
  );
}


export default LoadingState;
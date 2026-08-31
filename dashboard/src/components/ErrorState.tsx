/**
 * QuantumOS Dashboard
 *
 * Reusable error-state component.
 */

interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
}


function ErrorState({
  message,
  onRetry,
}: ErrorStateProps) {
  return (
    <section
      className="error-state"
      role="alert"
    >
      <div className="error-icon">
        !
      </div>

      <div className="error-content">
        <strong>
          Unable to load QuantumOS
        </strong>

        <p>
          {message}
        </p>

        {onRetry && (
          <button
            type="button"
            onClick={onRetry}
          >
            Try Again
          </button>
        )}
      </div>
    </section>
  );
}


export default ErrorState;
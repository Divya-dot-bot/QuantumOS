/**
 * QuantumOS Dashboard
 *
 * Displays the health state of the QuantumOS API/system.
 */

interface HealthIndicatorProps {
  healthy: boolean;
  label?: string;
  detail?: string;
}


function HealthIndicator({
  healthy,
  label,
  detail,
}: HealthIndicatorProps) {
  const statusLabel =
    label ??
    (healthy ? "SYSTEM ONLINE" : "SYSTEM OFFLINE");

  return (
    <div
      className={`health-indicator ${
        healthy
          ? "health-healthy"
          : "health-unhealthy"
      }`}
      role="status"
      aria-live="polite"
    >
      <span
        className="health-dot"
        aria-hidden="true"
      />

      <div className="health-content">
        <strong>
          {statusLabel}
        </strong>

        {detail && (
          <span>
            {detail}
          </span>
        )}
      </div>
    </div>
  );
}


export default HealthIndicator;
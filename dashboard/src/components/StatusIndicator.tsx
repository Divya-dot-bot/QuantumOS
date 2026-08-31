/**
 * QuantumOS Dashboard
 *
 * Reusable status indicator component.
 */

interface StatusIndicatorProps {
  status: string;
  label?: string;
  size?: "small" | "medium" | "large";
}


function StatusIndicator({
  status,
  label,
  size = "medium",
}: StatusIndicatorProps) {
  const normalizedStatus =
    status.toLowerCase().trim();

  const statusClass =
    getStatusClass(normalizedStatus);

  const displayLabel =
    label ??
    status.toUpperCase();


  return (
    <span
      className={`status-indicator ${statusClass} ${size}`}
      role="status"
      aria-label={`Status: ${displayLabel}`}
    >
      <span
        className="status-dot"
        aria-hidden="true"
      />

      <span className="status-label">
        {displayLabel}
      </span>
    </span>
  );
}


function getStatusClass(
  status: string,
): string {
  switch (status) {
    case "available":
    case "ready":
    case "online":
      return "status-positive";

    case "running":
    case "active":
      return "status-running";

    case "busy":
    case "queued":
    case "pending":
      return "status-warning";

    case "completed":
    case "success":
      return "status-positive";

    case "failed":
    case "error":
      return "status-negative";

    case "offline":
    case "disabled":
      return "status-neutral";

    default:
      return "status-neutral";
  }
}


export default StatusIndicator;
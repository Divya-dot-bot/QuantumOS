/**
 * QuantumOS Dashboard
 *
 * Reusable statistic card component.
 */

interface StatCardProps {
  label: string;
  value: string | number;
  detail?: string;
}


function StatCard({
  label,
  value,
  detail,
}: StatCardProps) {
  return (
    <article className="stat-card">
      <span className="stat-label">
        {label}
      </span>

      <strong className="stat-value">
        {value}
      </strong>

      {detail && (
        <span className="stat-detail">
          {detail}
        </span>
      )}
    </article>
  );
}


export default StatCard;
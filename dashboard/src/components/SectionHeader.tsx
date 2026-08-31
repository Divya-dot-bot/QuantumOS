/**
 * QuantumOS Dashboard
 *
 * Reusable section heading component.
 */

interface SectionHeaderProps {
  title: string;
  description?: string;
  kicker?: string;
  action?: React.ReactNode;
}


function SectionHeader({
  title,
  description,
  kicker,
  action,
}: SectionHeaderProps) {
  return (
    <div className="section-header">
      <div className="section-header-content">
        {kicker && (
          <span className="panel-kicker">
            {kicker}
          </span>
        )}

        <h2>
          {title}
        </h2>

        {description && (
          <p>
            {description}
          </p>
        )}
      </div>

      {action && (
        <div className="section-header-action">
          {action}
        </div>
      )}
    </div>
  );
}


export default SectionHeader;
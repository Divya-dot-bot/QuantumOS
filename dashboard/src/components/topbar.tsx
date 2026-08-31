interface TopbarProps {
  title: string;
  subtitle?: string;
}


export default function Topbar({
  title,
  subtitle,
}: TopbarProps) {
  return (
    <header className="topbar">
      <div>
        <strong>{title}</strong>

        {subtitle && (
          <span>{subtitle}</span>
        )}
      </div>

      <div className="topbar-status">
        <span className="status-dot" />
        LOCAL ENVIRONMENT
      </div>
    </header>
  );
}
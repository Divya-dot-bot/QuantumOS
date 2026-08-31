import type { FC } from "react";

interface EmptyStateProps {
  title: string;

  message?: string;

  description?: string;
}

const EmptyState: FC<EmptyStateProps> = ({
  title,
  message,
  description,
}) => {
  const text =
    message ??
    description;

  return (
    <div className="empty-state">
      <div className="empty-state-icon">
        ○
      </div>

      <h3>{title}</h3>

      {text && (
        <p>{text}</p>
      )}
    </div>
  );
};

export default EmptyState;
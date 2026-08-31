interface ResultChartProps {
  counts?: Record<string, number>;
  shots?: number;
  results?: Record<string, number>;
}

export default function ResultChart({
  counts,
  results,
}: ResultChartProps) {
  const data = counts ?? results ?? {};

  const entries = Object.entries(data);

  if (entries.length === 0) {
    return (
      <div className="result-chart">
        <p>No measurement results available.</p>
      </div>
    );
  }

  const total = entries.reduce(
    (sum, [, value]) => sum + value,
    0,
  );

  return (
    <div className="result-chart">
      {entries.map(([state, value]) => {
        const percentage =
          total > 0
            ? (value / total) * 100
            : 0;

        return (
          <div
            key={state}
            className="result-row"
          >
            <div className="result-row-header">
              <strong>{state}</strong>

              <span>
                {value}{" "}
                ({percentage.toFixed(1)}%)
              </span>
            </div>

            <div className="result-bar">
              <div
                className="result-bar-fill"
                style={{
                  width: `${percentage}%`,
                }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
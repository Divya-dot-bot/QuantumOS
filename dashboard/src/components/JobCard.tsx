import type { Job } from "../services/api";


interface JobCardProps {
  job: Job;
  onRun?: (jobId: string) => void;
  running?: boolean;
}


function JobCard({
  job,
  onRun,
  running = false,
}: JobCardProps) {
  const status =
    job.status.toLowerCase();

  const statusClass =
    status === "completed"
      ? "job-status completed"
      : status === "failed"
        ? "job-status failed"
        : status === "running"
          ? "job-status running"
          : "job-status queued";


  const canRun =
    status === "queued" ||
    status === "pending";


  return (
    <article className="job-card">

      <div className="job-card-header">

        <div>
          <span className="job-type">
            QUANTUM JOB
          </span>

          <h3>
            {job.job_id}
          </h3>
        </div>


        <span className={statusClass}>
          {job.status.toUpperCase()}
        </span>

      </div>


      <div className="job-card-details">

        <div className="job-detail">
          <span>
            SHOTS
          </span>

          <strong>
            {job.shots.toLocaleString()}
          </strong>
        </div>


        <div className="job-detail">
          <span>
            PRIORITY
          </span>

          <strong>
            {job.priority}
          </strong>
        </div>


        <div className="job-detail">
          <span>
            BACKEND
          </span>

          <strong>
            {job.backend ?? "AUTO"}
          </strong>
        </div>

      </div>


      {job.error && (
        <div className="job-error">
          {job.error}
        </div>
      )}


      <div className="job-card-footer">

        <div className="job-timestamps">

          {job.submitted_at && (
            <span>
              Submitted{" "}
              {formatDate(job.submitted_at)}
            </span>
          )}

          {job.completed_at && (
            <span>
              Completed{" "}
              {formatDate(job.completed_at)}
            </span>
          )}

        </div>


        {onRun && canRun && (
          <button
            type="button"
            onClick={() => onRun(job.job_id)}
            disabled={running}
          >
            {running
              ? "Running..."
              : "Run Job"}
          </button>
        )}

      </div>

    </article>
  );
}


function formatDate(
  value: string,
): string {
  const date =
    new Date(value);

  if (
    Number.isNaN(
      date.getTime(),
    )
  ) {
    return value;
  }

  return date.toLocaleString();
}


export default JobCard;
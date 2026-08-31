/**
 * QuantumOS Dashboard
 *
 * Displays the collection of quantum jobs.
 */

import type { Job } from "../services/api";

import JobCard from "./JobCard";
import LoadingState from "./LoadingState";


interface JobListProps {
  jobs: Job[];
  loading?: boolean;
  onRunJob?: (jobId: string) => void;
  runningJobId?: string | null;
}


function JobList({
  jobs,
  loading = false,
  onRunJob,
  runningJobId = null,
}: JobListProps) {
  if (loading) {
    return (
      <LoadingState
        message="Loading quantum jobs..."
      />
    );
  }


  if (jobs.length === 0) {
    return (
      <div className="empty-state">
        <strong>
          No quantum jobs
        </strong>

        <span>
          There are currently no jobs in
          the scheduler queue.
        </span>
      </div>
    );
  }


  return (
    <div className="job-list">
      {jobs.map((job) => (
        <JobCard
          key={job.job_id}
          job={job}
          onRun={onRunJob}
          running={
            runningJobId === job.job_id
          }
        />
      ))}
    </div>
  );
}


export default JobList;
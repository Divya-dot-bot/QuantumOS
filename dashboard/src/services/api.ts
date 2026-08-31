import type {
  Backend,
  BackendListResponse,
  DashboardData,
  HealthResponse,
  Job,
  JobResult,
  ExecutionHistory,
  JobSubmissionRequest,
  JobSubmissionResponse,
  Resource,
  ResourceListResponse,
  ResourceStats,
  SchedulerStatus,
} from "../types/quantum";

// -----------------------------------------------------------------------------
// Re-export types
// -----------------------------------------------------------------------------

export type {
  Backend,
  DashboardData,
  Job,
  JobResult,
  ExecutionHistory,
  Resource,
  ResourceStats,
  SchedulerStatus,
};

export type QuantumBackend = Backend;
export type QuantumJob = Job;
export type QuantumJobResult = JobResult;
export type QuantumResource = Resource;


// -----------------------------------------------------------------------------
// API configuration
// -----------------------------------------------------------------------------

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "https://quantumos-lehv.onrender.com";


// -----------------------------------------------------------------------------
// Generic request helper
// -----------------------------------------------------------------------------

async function request<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(
    `${API_BASE_URL}${path}`,
    {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options?.headers ?? {}),
      },
    },
  );

  if (!response.ok) {
    let message =
      `Request failed with status ${response.status}`;

    try {
      const body = await response.json();

      if (
        body &&
        typeof body.detail === "string"
      ) {
        message = body.detail;
      }
    } catch {
      // Ignore invalid JSON error bodies.
    }

    throw new Error(message);
  }

  return response.json() as Promise<T>;
}


// -----------------------------------------------------------------------------
// Health
// -----------------------------------------------------------------------------

export async function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/health");
}


// -----------------------------------------------------------------------------
// Backends
// -----------------------------------------------------------------------------

export async function getBackends(): Promise<BackendListResponse> {
  return request<BackendListResponse>(
    "/api/backends",
  );
}


// -----------------------------------------------------------------------------
// Jobs
// -----------------------------------------------------------------------------

export async function getJobs(): Promise<Job[]> {
  const response = await request<{
    value: Job[];
    Count: number;
  }>("/api/jobs");

  return response.value;
}


export async function getSchedulerStatus(): Promise<SchedulerStatus> {
  return request<SchedulerStatus>(
    "/api/jobs/scheduler/status",
  );
}


export async function getJobHistory(): Promise<
  ExecutionHistory[]
> {
  const response = await request<
    ExecutionHistory[]
  >("/api/jobs/history/all");

  return Array.isArray(response)
    ? response
    : [];
}


export async function getJob(): Promise<Job[]> {
  const response = await request<Job[]>(
    "/api/jobs",
  );

  return Array.isArray(response)
    ? response
    : [];
}


export async function submitJob(
  payload: JobSubmissionRequest,
): Promise<JobSubmissionResponse> {
  return request<JobSubmissionResponse>(
    "/api/jobs",
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}


export async function runJob(
  jobId: string,
): Promise<JobResult> {
  return request<JobResult>(
    `/api/jobs/${encodeURIComponent(jobId)}/run`,
    {
      method: "POST",
    },
  );
}


// -----------------------------------------------------------------------------
// Resources
// -----------------------------------------------------------------------------

export async function getResources(): Promise<ResourceListResponse> {
  return request<ResourceListResponse>(
    "/api/resources",
  );
}


export async function getResourceStats(): Promise<ResourceStats> {
  return request<ResourceStats>(
    "/api/resources/stats",
  );
}


// -----------------------------------------------------------------------------
// Dashboard
// -----------------------------------------------------------------------------

export async function getDashboardData(): Promise<DashboardData> {
  const [
    backendsResponse,
    jobs,
    resourcesResponse,
    health,
  ] = await Promise.all([
    getBackends(),
    getJobs(),
    getResources(),
    getHealth(),
  ]);

  return {
    backends: backendsResponse.backends,
    jobs,
    resources: resourcesResponse.resources,
    health,
  };
}
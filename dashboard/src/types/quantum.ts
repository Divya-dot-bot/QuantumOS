/**
 * Shared QuantumOS dashboard types.
 */

// -----------------------------------------------------------------------------
// Navigation
// -----------------------------------------------------------------------------

export type Page =
  | "dashboard"
  | "core"
  | "lab"
  | "processes"
  | "scheduler"
  | "memory"
  | "terminal";

// -----------------------------------------------------------------------------
// Backend
// -----------------------------------------------------------------------------

export interface Backend {
  backend_id: string;
  name: string;
  status: string;
  num_qubits: number;
  resource_type: string;
  is_busy: boolean;
  supported_operations: string[];
  metadata?: Record<string, unknown>;
}

export type QuantumBackend = Backend;

export interface BackendListResponse {
  backends: Backend[];
}

// -----------------------------------------------------------------------------
// Jobs
// -----------------------------------------------------------------------------

export interface SchedulerStatus {
  runtime_status: string;
  policy: string;
  queue_size: number;
  jobs_submitted: number;
  jobs_dispatched: number;
  last_decision: string | null;
}

export interface Job {
  job_id: string;
  status: string;
  shots: number;
  priority: number;
  backend: string | null;
  submitted_at: string | null;
  started_at: string | null;
  completed_at: string | null;
  error: string | null;
  metadata: Record<string, unknown>;
}

export type QuantumJob = Job;

export interface JobSubmissionRequest {
  circuit: unknown;
  shots: number;
  priority?: number;
  backend?: string | null;
  metadata?: Record<string, unknown>;
}

export interface JobSubmissionResponse {
  job_id: string;
  status: string;
  message: string;
}

export interface JobResult {
  job_id: string;
  status: string;
  backend_id: string | null;
  backend_name: string | null;
  shots: number;
  counts: Record<string, number>;
  metadata: Record<string, unknown>;
}

export interface ExecutionHistory {
  job_id: string;
  worker_id: string;
  backend_id: string;
  backend_name: string;
  result: JobResult;
}

export type QuantumJobResult = JobResult;

// -----------------------------------------------------------------------------
// Resources
// -----------------------------------------------------------------------------

export interface ResourceStats {
  total_resources: number;
  available_resources: number;
  busy_resources: number;
  offline_resources: number;
  maintenance_resources: number;
  allocations: number;
}

export interface Resource {
  resource_id: string;
  name: string;
  status: string;
  num_qubits: number;
  resource_type: string;
  supported_operations: string[];
  metadata?: Record<string, unknown>;
}

export type QuantumResource = Resource;

export interface ResourceListResponse {
  resources: Resource[];
  total: number;
}

// -----------------------------------------------------------------------------
// Health
// -----------------------------------------------------------------------------

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
}

// -----------------------------------------------------------------------------
// Dashboard
// -----------------------------------------------------------------------------

export interface DashboardData {
  backends: Backend[];
  jobs: Job[];
  resources: Resource[];
  health?: HealthResponse;
}

// -----------------------------------------------------------------------------
// Circuit
// -----------------------------------------------------------------------------

export type GateType =
  | "H"
  | "X"
  | "Y"
  | "Z"
  | "S"
  | "T"
  | "M"
  | "CNOT";

export interface CircuitGate {
  id: string;
  type: GateType;
  qubit: number;
  targetQubit?: number;
  column: number;
}

export type Gate = CircuitGate;

export interface Circuit {
  name: string;
  qubits: number;
  depth: number;
  gates: CircuitGate[];
}

// -----------------------------------------------------------------------------
// Experiments
// -----------------------------------------------------------------------------

export interface ExperimentRequest {
  circuit: unknown;
  shots?: number;
  backend?: string | null;
  metadata?: Record<string, unknown>;
}

export interface QuantumResult extends JobResult {
  experiment?: string;
  execution_time_ms?: number;
  backend?: string;
  results?: Record<string, number>;
}
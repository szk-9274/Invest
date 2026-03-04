export type JobCommand = 'backtest' | 'stage2' | 'full' | 'chart' | 'update_tickers';

export interface JobCreateRequest {
  command: JobCommand;
  start_date?: string;
  end_date?: string;
  tickers?: string;
  no_charts?: boolean;
  ticker?: string;
  with_fundamentals?: boolean;
  min_market_cap?: number;
  max_tickers?: number;
  timeout_seconds?: number;
}

export interface JobResponse {
  job_id: string;
  command: string;
  command_line: string;
  status: 'queued' | 'running' | 'succeeded' | 'failed' | 'cancelled' | 'timeout';
  created_at: string;
  started_at?: string | null;
  finished_at?: string | null;
  return_code?: number | null;
  error?: string | null;
  timeout_seconds: number;
}

export interface JobLogsResponse {
  job_id: string;
  status: string;
  lines: string[];
}

const API_BASE = '/api/jobs';

export async function createJob(request: JobCreateRequest): Promise<JobResponse> {
  const response = await fetch(API_BASE, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Failed to create job: ${response.status} ${text}`);
  }
  return response.json();
}

export async function getJob(jobId: string): Promise<JobResponse> {
  const response = await fetch(`${API_BASE}/${jobId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch job: ${response.status}`);
  }
  return response.json();
}

export async function listJobs(limit = 30): Promise<JobResponse[]> {
  const response = await fetch(`${API_BASE}?limit=${limit}`);
  if (!response.ok) {
    throw new Error(`Failed to list jobs: ${response.status}`);
  }
  return response.json();
}

export async function getJobLogs(jobId: string, tail = 200): Promise<JobLogsResponse> {
  const response = await fetch(`${API_BASE}/${jobId}/logs?tail=${tail}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch logs: ${response.status}`);
  }
  return response.json();
}

export async function cancelJob(jobId: string): Promise<JobResponse> {
  const response = await fetch(`${API_BASE}/${jobId}/cancel`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error(`Failed to cancel job: ${response.status}`);
  }
  return response.json();
}

import { api } from "./client";
import type { components } from "./schema";

// Re-export types from schema
export type JobLog = components["schemas"]["LogEntry"];
export type AlbumInfo = components["schemas"]["AlbumInfo"];

export type JobStatus =
  | "idle" // UI-only: no active job
  | "pending"
  | "fetching_info"
  | "downloading"
  | "importing"
  | "completed"
  | "failed"
  | "cancelled";

// Override status field to use JobStatus instead of string
export type Job = Omit<components["schemas"]["Job"], "status"> & {
  status: JobStatus;
};

export type CreateJobResult =
  | {
      success: true;
      jobId: string;
    }
  | {
      success: false;
      error: string;
      activeJobId?: string;
    };

export async function createJob(
  url: string,
  audioFormat = "mp3"
): Promise<CreateJobResult> {
  const { data, error, response } = await api.POST("/jobs", {
    body: { url, audio_format: audioFormat },
  });

  if (error) {
    if (response.status === 409) {
      // Job conflict - another job is running
      const conflict = error as { error: string; active_job_id?: string };
      return {
        success: false,
        error: conflict.error,
        activeJobId: conflict.active_job_id,
      };
    }
    return { success: false, error: "Failed to create job" };
  }

  return { success: true, jobId: data.id };
}

export async function listJobs(): Promise<{
  jobs: Job[];
  logs: JobLog[];
}> {
  const { data, error } = await api.GET("/jobs");

  if (error) return { jobs: [], logs: [] };
  return {
    jobs: data.jobs as Job[],
    logs: data.logs as JobLog[],
  };
}

export async function deleteJob(jobId: string): Promise<void> {
  const { error } = await api.DELETE("/jobs/{job_id}", {
    params: { path: { job_id: jobId } },
  });

  if (error) throw new Error("Failed to delete job");
}

export async function clearJobs(): Promise<number> {
  const { data, error } = await api.DELETE("/jobs");

  if (error) throw new Error("Failed to clear jobs");
  return data.cleared;
}

export async function cancelJob(jobId: string): Promise<void> {
  const { error } = await api.POST("/jobs/{job_id}/cancel", {
    params: { path: { job_id: jobId } },
  });

  if (error) throw new Error("Failed to cancel job");
}

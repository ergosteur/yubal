import { useState, useCallback, useRef, useEffect } from "react";
import {
  createJob,
  listJobs,
  cancelJob as cancelJobApi,
  deleteJob as deleteJobApi,
  type Job,
  type JobLog,
} from "../api/jobs";

export type { Job, JobLog } from "../api/jobs";

export interface UseJobsResult {
  // Data from API
  jobs: Job[];
  logs: JobLog[];

  // Actions
  startJob: (url: string, audioFormat?: string) => Promise<void>;
  cancelJob: (jobId: string) => Promise<void>;
  deleteJob: (jobId: string) => Promise<void>;
  refreshJobs: () => Promise<void>;
}

const POLL_INTERVAL = 2000; // 2 seconds

export function useJobs(): UseJobsResult {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [logs, setLogs] = useState<JobLog[]>([]);

  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const isPollingRef = useRef(false);

  const stopPolling = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
    isPollingRef.current = false;
  }, []);

  const poll = useCallback(async () => {
    const { jobs: jobList, logs: logList } = await listJobs();
    setJobs(jobList);
    setLogs(logList);

    // Check if there are any active jobs
    const hasActiveJobs = jobList.some(
      (j) => !["completed", "failed", "cancelled"].includes(j.status)
    );

    // Stop polling if no active jobs
    if (!hasActiveJobs) {
      stopPolling();
    }
  }, [stopPolling]);

  const startPolling = useCallback(() => {
    if (isPollingRef.current) return;
    isPollingRef.current = true;

    // Poll immediately, then at interval
    poll();
    pollingRef.current = setInterval(poll, POLL_INTERVAL);
  }, [poll]);

  const startJob = useCallback(
    async (url: string, audioFormat = "mp3") => {
      const result = await createJob(url, audioFormat);

      if (!result.success) {
        // Refresh to show current state
        await poll();
        return;
      }

      // Refresh and start polling
      await poll();
      startPolling();
    },
    [poll, startPolling]
  );

  const cancelJob = useCallback(
    async (jobId: string) => {
      await cancelJobApi(jobId);
      await poll();
    },
    [poll]
  );

  const deleteJob = useCallback(
    async (jobId: string) => {
      await deleteJobApi(jobId);
      await poll();
    },
    [poll]
  );

  const refreshJobs = useCallback(async () => {
    await poll();

    // Check if there are any active jobs and start polling
    const { jobs: jobList } = await listJobs();
    const hasActiveJobs = jobList.some(
      (j) => !["completed", "failed", "cancelled"].includes(j.status)
    );

    if (hasActiveJobs) {
      startPolling();
    }
  }, [poll, startPolling]);

  // Refresh jobs on mount
  useEffect(() => {
    refreshJobs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      stopPolling();
    };
  }, [stopPolling]);

  return {
    jobs,
    logs,
    startJob,
    cancelJob,
    deleteJob,
    refreshJobs,
  };
}

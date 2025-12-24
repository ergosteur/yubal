import { useState, useCallback, useRef } from "react";
import {
  createSyncEventSource,
  type ProgressEvent,
  type SyncResponse,
} from "../api/sse";

export type ProgressStep =
  | "idle"
  | "starting"
  | "downloading"
  | "tagging"
  | "complete"
  | "error";

export interface LogEntry {
  id: number;
  timestamp: Date;
  step: ProgressStep;
  message: string;
}

export interface UseSyncResult {
  status: ProgressStep;
  progress: number;
  logs: LogEntry[];
  result: SyncResponse | null;
  error: string | null;
  startSync: (url: string) => void;
  cancelSync: () => void;
  clearLogs: () => void;
}

export function useSync(): UseSyncResult {
  const [status, setStatus] = useState<ProgressStep>("idle");
  const [progress, setProgress] = useState(0);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [result, setResult] = useState<SyncResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<(() => void) | null>(null);
  const logIdRef = useRef(0);

  const addLog = useCallback((step: ProgressStep, message: string) => {
    logIdRef.current += 1;
    setLogs((prev) => [
      ...prev,
      {
        id: logIdRef.current,
        timestamp: new Date(),
        step,
        message,
      },
    ]);
  }, []);

  const startSync = useCallback(
    (url: string) => {
      // Reset state
      setStatus("starting");
      setProgress(0);
      setLogs([]);
      setResult(null);
      setError(null);
      logIdRef.current = 0;

      addLog("starting", `Starting sync from: ${url}`);

      const eventSource = createSyncEventSource(url, {
        onProgress: (event: ProgressEvent) => {
          const step = event.step as ProgressStep;
          setStatus(step);
          if (event.progress !== null && event.progress !== undefined) {
            setProgress(event.progress);
          }
          addLog(step, event.message);
        },
        onComplete: (syncResult: SyncResponse) => {
          setStatus(syncResult.success ? "complete" : "error");
          setProgress(100);
          setResult(syncResult);
          if (!syncResult.success && syncResult.error) {
            setError(syncResult.error);
            addLog("error", syncResult.error);
          } else if (syncResult.destination) {
            addLog(
              "complete",
              `Synced ${syncResult.track_count} tracks to ${syncResult.destination}`
            );
          }
          abortRef.current = null;
        },
        onError: (err: Error) => {
          setStatus("error");
          setError(err.message);
          addLog("error", err.message);
          abortRef.current = null;
        },
      });

      abortRef.current = eventSource.abort;
    },
    [addLog]
  );

  const cancelSync = useCallback(() => {
    if (abortRef.current) {
      abortRef.current();
      abortRef.current = null;
      setStatus("idle");
      addLog("error", "Sync cancelled by user");
    }
  }, [addLog]);

  const clearLogs = useCallback(() => {
    setLogs([]);
    setStatus("idle");
    setProgress(0);
    setResult(null);
    setError(null);
    logIdRef.current = 0;
  }, []);

  return {
    status,
    progress,
    logs,
    result,
    error,
    startSync,
    cancelSync,
    clearLogs,
  };
}

import { useEffect, useRef } from "react";
import { Progress } from "@heroui/react";
import { motion, AnimatePresence } from "framer-motion";
import type { LogEntry, ProgressStep } from "../hooks/useSync";

interface ConsoleOutputProps {
  logs: LogEntry[];
  status: ProgressStep;
  progress: number;
}

const stepColors: Record<ProgressStep, string> = {
  idle: "text-gray-500",
  starting: "text-blue-400",
  downloading: "text-cyan-400",
  tagging: "text-purple-400",
  complete: "text-green-400",
  error: "text-red-400",
};

const progressColors: Record<
  ProgressStep,
  "default" | "primary" | "secondary" | "success" | "warning" | "danger"
> = {
  idle: "default",
  starting: "primary",
  downloading: "primary",
  tagging: "secondary",
  complete: "success",
  error: "danger",
};

function formatTime(date: Date): string {
  return date.toLocaleTimeString("en-US", {
    hour12: false,
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export function ConsoleOutput({ logs, status, progress }: ConsoleOutputProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const showProgress = status !== "idle";

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="overflow-hidden rounded-lg border border-white/10 bg-[#0d0d0d]">
      {/* Terminal Header */}
      <div className="flex items-center justify-between border-b border-white/10 px-4 py-2">
        <div className="flex items-center gap-2">
          <div className="flex gap-1.5">
            <div className="h-3 w-3 rounded-full bg-red-500/80" />
            <div className="h-3 w-3 rounded-full bg-yellow-500/80" />
            <div className="h-3 w-3 rounded-full bg-green-500/80" />
          </div>
          <span className="ml-2 font-mono text-xs text-gray-500">output</span>
        </div>
        {showProgress && (
          <span className={`font-mono text-xs ${stepColors[status]}`}>
            {status.toUpperCase()}
          </span>
        )}
      </div>

      {/* Progress Bar */}
      <AnimatePresence>
        {showProgress && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="border-b border-white/10 px-4 py-2"
          >
            <Progress
              aria-label="Sync progress"
              value={progress}
              color={progressColors[status]}
              size="sm"
              className="w-full"
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Console Content */}
      <div
        ref={containerRef}
        className="console-output h-80 overflow-y-auto p-4 font-mono text-sm"
      >
        {logs.length === 0 ? (
          <div className="flex h-full items-center justify-center text-gray-600">
            <span>Waiting for input...</span>
          </div>
        ) : (
          <AnimatePresence initial={false}>
            {logs.map((log) => (
              <motion.div
                key={log.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex gap-2 py-0.5"
              >
                <span className="shrink-0 text-gray-600">
                  {formatTime(log.timestamp)}
                </span>
                <span className={`shrink-0 ${stepColors[log.step]}`}>
                  {log.step === "idle" ? "$" : ">"}
                </span>
                <span className="break-all text-gray-300">{log.message}</span>
              </motion.div>
            ))}
          </AnimatePresence>
        )}
      </div>
    </div>
  );
}

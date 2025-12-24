import { useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import type { LogEntry, ProgressStep } from "../hooks/useSync";

interface ConsoleOutputProps {
  logs: LogEntry[];
}

const stepColors: Record<ProgressStep, string> = {
  idle: "text-gray-400",
  starting: "text-blue-400",
  downloading: "text-cyan-400",
  tagging: "text-purple-400",
  complete: "text-green-400",
  error: "text-red-400",
};

function formatTime(date: Date): string {
  return date.toLocaleTimeString("en-US", {
    hour12: false,
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export function ConsoleOutput({ logs }: ConsoleOutputProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new logs
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [logs]);

  if (logs.length === 0) {
    return (
      <div className="console-output rounded-lg bg-[#1e1e2e] p-4 font-mono text-sm text-gray-500 h-64 flex items-center justify-center">
        Console output will appear here...
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className="console-output rounded-lg bg-[#1e1e2e] p-4 font-mono text-sm h-64 overflow-y-auto"
    >
      <AnimatePresence initial={false}>
        {logs.map((log) => (
          <motion.div
            key={log.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex gap-2 py-0.5"
          >
            <span className="text-gray-500 shrink-0">
              [{formatTime(log.timestamp)}]
            </span>
            <span className={`shrink-0 ${stepColors[log.step]}`}>
              [{log.step.toUpperCase()}]
            </span>
            <span className="text-gray-200 break-all">{log.message}</span>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}

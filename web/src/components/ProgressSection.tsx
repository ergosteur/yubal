import { Progress, Chip } from "@heroui/react";
import { motion, AnimatePresence } from "framer-motion";
import type { ProgressStep } from "../hooks/useSync";

interface ProgressSectionProps {
  status: ProgressStep;
  progress: number;
}

const statusConfig: Record<
  ProgressStep,
  { label: string; color: "default" | "primary" | "secondary" | "success" | "warning" | "danger" }
> = {
  idle: { label: "Idle", color: "default" },
  starting: { label: "Starting", color: "primary" },
  downloading: { label: "Downloading", color: "primary" },
  tagging: { label: "Tagging", color: "secondary" },
  complete: { label: "Complete", color: "success" },
  error: { label: "Error", color: "danger" },
};

export function ProgressSection({ status, progress }: ProgressSectionProps) {
  const config = statusConfig[status];
  const showProgress = status !== "idle";

  return (
    <AnimatePresence>
      {showProgress && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          exit={{ opacity: 0, height: 0 }}
          className="space-y-3"
        >
          <div className="flex items-center justify-between">
            <span className="text-sm text-default-500">Progress</span>
            <Chip color={config.color} variant="flat" size="sm">
              {config.label}
            </Chip>
          </div>
          <Progress
            aria-label="Sync progress"
            value={progress}
            color={config.color === "default" ? "primary" : config.color}
            showValueLabel
            className="w-full"
          />
        </motion.div>
      )}
    </AnimatePresence>
  );
}

import { useState } from "react";
import { Button } from "@heroui/react";
import { UrlInput, isValidUrl } from "./components/UrlInput";
import { ConsoleOutput } from "./components/ConsoleOutput";
import { useSync } from "./hooks/useSync";

export default function App() {
  const [url, setUrl] = useState("");
  const { status, progress, logs, startSync, cancelSync, clearLogs } =
    useSync();

  const isSyncing =
    status !== "idle" && status !== "complete" && status !== "error";
  const canSync = isValidUrl(url) && !isSyncing;
  const showSecondaryActions =
    isSyncing || status === "complete" || status === "error";

  const handleSync = () => {
    if (canSync) {
      startSync(url);
    }
  };

  const handleClear = () => {
    clearLogs();
    setUrl("");
  };

  return (
    <div className="bg-background flex min-h-screen flex-col items-center justify-center px-4 py-12">
      <main className="w-full max-w-xl space-y-8">
        {/* Header */}
        <div className="space-y-2 text-center">
          <h1 className="text-4xl font-bold tracking-tight text-white">
            yubal
          </h1>
          <p className="text-default-500">YouTube Album Downloader</p>
        </div>

        {/* Input Section */}
        <div className="space-y-3">
          <UrlInput value={url} onChange={setUrl} disabled={isSyncing} />

          <Button
            color="primary"
            size="lg"
            onPress={handleSync}
            isLoading={isSyncing}
            isDisabled={!canSync}
            className="w-full font-medium"
          >
            {isSyncing ? "Syncing..." : "Sync Album"}
          </Button>

          {showSecondaryActions && (
            <div className="flex gap-2">
              {isSyncing && (
                <Button
                  color="danger"
                  variant="flat"
                  onPress={cancelSync}
                  className="flex-1"
                >
                  Cancel
                </Button>
              )}
              {(status === "complete" || status === "error") && (
                <Button
                  color="default"
                  variant="flat"
                  onPress={handleClear}
                  className="flex-1"
                >
                  Clear
                </Button>
              )}
            </div>
          )}
        </div>

        {/* Console Output */}
        <ConsoleOutput logs={logs} status={status} progress={progress} />

        {/* Footer */}
        <p className="text-default-500 text-center text-sm">
          Powered by{" "}
          <a
            href="https://beets.io"
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary hover:underline"
          >
            beets
          </a>
        </p>
      </main>
    </div>
  );
}

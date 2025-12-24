import { useState } from "react";
import { Card, CardBody, Button } from "@heroui/react";
import { Header } from "./components/Header";
import { UrlInput, isValidUrl } from "./components/UrlInput";
import { SyncButton } from "./components/SyncButton";
import { ProgressSection } from "./components/ProgressSection";
import { ConsoleOutput } from "./components/ConsoleOutput";
import { useSync } from "./hooks/useSync";

export default function App() {
  const [url, setUrl] = useState("");
  const { status, progress, logs, startSync, cancelSync, clearLogs } =
    useSync();

  const isSyncing =
    status !== "idle" && status !== "complete" && status !== "error";
  const canSync = isValidUrl(url) && !isSyncing;

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
    <div className="bg-background min-h-screen">
      <Header />

      <main className="container mx-auto max-w-2xl px-4 py-8">
        <Card>
          <CardBody className="space-y-6">
            {/* URL Input Section */}
            <div className="space-y-4">
              <UrlInput value={url} onChange={setUrl} disabled={isSyncing} />

              <div className="flex flex-col gap-2 sm:flex-row">
                <SyncButton
                  onClick={handleSync}
                  isLoading={isSyncing}
                  isDisabled={!canSync}
                />
                {isSyncing && (
                  <Button
                    color="danger"
                    variant="flat"
                    onPress={cancelSync}
                    className="w-full sm:w-auto"
                  >
                    Cancel
                  </Button>
                )}
                {(status === "complete" || status === "error") && (
                  <Button
                    color="default"
                    variant="flat"
                    onPress={handleClear}
                    className="w-full sm:w-auto"
                  >
                    Clear
                  </Button>
                )}
              </div>
            </div>

            {/* Progress Section */}
            <ProgressSection status={status} progress={progress} />

            {/* Console Output */}
            <div className="space-y-2">
              <span className="text-default-500 text-sm">Console Output</span>
              <ConsoleOutput logs={logs} />
            </div>
          </CardBody>
        </Card>

        {/* Footer */}
        <footer className="text-default-400 mt-8 text-center text-sm">
          <p>
            Downloads YouTube Music albums and organizes them with{" "}
            <a
              href="https://beets.io"
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:underline"
            >
              beets
            </a>
          </p>
        </footer>
      </main>
    </div>
  );
}

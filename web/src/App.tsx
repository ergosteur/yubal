import { Button, NumberInput, Tooltip } from "@heroui/react";
import { Download, Hash } from "lucide-react";
import { useState } from "react";
import { ConsolePanel } from "./components/console-panel";
import { DownloadsPanel } from "./components/downloads-panel";
import { Footer } from "./components/layout/footer";
import { Header } from "./components/layout/header";
import { BlurFade } from "./components/magicui/blur-fade";
import { UrlInput } from "./components/url-input";
import { useJobs } from "./hooks/use-jobs";
import { isValidUrl } from "./lib/url";

const DEFAULT_MAX_ITEMS = 50;

export default function App() {
  const [url, setUrl] = useState("");
  const [maxItems, setMaxItems] = useState(DEFAULT_MAX_ITEMS);
  const { jobs, startJob, cancelJob, deleteJob } = useJobs();

  const canSync = isValidUrl(url);

  const handleSync = async () => {
    if (canSync) {
      await startJob(url, maxItems);
      setUrl("");
    }
  };

  const handleDelete = async (jobId: string) => {
    await deleteJob(jobId);
  };

  return (
    <div className="relative flex min-h-screen flex-col">
      <Header />

      <main className="mx-auto w-full max-w-4xl flex-1 px-4 py-8">
        {/* URL Input Section */}
        <BlurFade delay={0.05} direction="up">
          <section className="mb-6 flex gap-2">
            <div className="flex-1">
              <UrlInput value={url} onChange={setUrl} />
            </div>
            <Tooltip content="Max number of tracks to download" offset={14}>
              <NumberInput
                hideStepper
                variant="faded"
                value={maxItems}
                onValueChange={setMaxItems}
                minValue={1}
                maxValue={10000}
                radius="lg"
                fullWidth={false}
                startContent={<Hash className="text-foreground-400 h-4 w-4" />}
                className="w-24 font-mono"
              />
            </Tooltip>
            <Button
              color="primary"
              radius="lg"
              variant={canSync ? "shadow" : "solid"}
              className="shadow-primary-100/50"
              onPress={handleSync}
              isDisabled={!canSync}
              startContent={<Download className="h-4 w-4" />}
            >
              Download
            </Button>
          </section>
        </BlurFade>

        {/* Stacked Panels */}
        <BlurFade delay={0.1} direction="up">
          <section className="mb-6 flex flex-col gap-4">
            <DownloadsPanel
              jobs={jobs}
              onCancel={cancelJob}
              onDelete={handleDelete}
            />
            <ConsolePanel />
          </section>
        </BlurFade>
      </main>

      <BlurFade delay={0.15} direction="up">
        <Footer />
      </BlurFade>
    </div>
  );
}

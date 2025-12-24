export interface ProgressEvent {
  step: "starting" | "downloading" | "tagging" | "complete" | "error";
  message: string;
  progress: number | null;
  details: Record<string, unknown> | null;
}

export interface SyncResponse {
  success: boolean;
  album: {
    title: string;
    artist: string;
    year: number | null;
    track_count: number;
  } | null;
  destination: string | null;
  track_count: number;
  error: string | null;
}

export interface SSEHandlers {
  onProgress: (event: ProgressEvent) => void;
  onComplete: (result: SyncResponse) => void;
  onError: (error: Error) => void;
}

interface ParsedEvent {
  type: string;
  data: unknown;
}

interface ParseResult {
  parsed: ParsedEvent[];
  remaining: string;
}

function parseSSEBuffer(buffer: string): ParseResult {
  const parsed: ParsedEvent[] = [];
  const lines = buffer.split("\n");
  let currentEvent = { type: "message", data: "" };
  let remaining = "";

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i] ?? "";

    // Empty line marks end of event
    if (line === "") {
      if (currentEvent.data) {
        try {
          parsed.push({
            type: currentEvent.type,
            data: JSON.parse(currentEvent.data),
          });
        } catch {
          // Skip malformed JSON
        }
      }
      currentEvent = { type: "message", data: "" };
      continue;
    }

    // Comment (keepalive)
    if (line.startsWith(":")) continue;

    // Event type
    if (line.startsWith("event:")) {
      currentEvent.type = line.slice(6).trim();
      continue;
    }

    // Data
    if (line.startsWith("data:")) {
      currentEvent.data = line.slice(5).trim();
      continue;
    }

    // ID (ignored)
    if (line.startsWith("id:")) continue;

    // Incomplete line - save for next buffer
    if (i === lines.length - 1 && !buffer.endsWith("\n")) {
      remaining = line;
    }
  }

  return { parsed, remaining };
}

export function createSyncEventSource(
  url: string,
  handlers: SSEHandlers
): { abort: () => void } {
  const abortController = new AbortController();

  fetch("/api/v1/sync", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
    },
    body: JSON.stringify({ url }),
    signal: abortController.signal,
  })
    .then(async (response) => {
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      if (!response.body) {
        throw new Error("No response body");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const events = parseSSEBuffer(buffer);
        buffer = events.remaining;

        for (const event of events.parsed) {
          if (event.type === "complete") {
            handlers.onComplete(event.data as SyncResponse);
          } else {
            handlers.onProgress(event.data as ProgressEvent);
          }
        }
      }
    })
    .catch((error) => {
      if (error.name !== "AbortError") {
        handlers.onError(error);
      }
    });

  return {
    abort: () => abortController.abort(),
  };
}

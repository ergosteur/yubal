import { GitBranch } from "lucide-react";

export function Footer() {
  return (
    <footer className="mt-6 text-center">
      <p className="text-foreground-500 font-mono text-xs">
        Made by{" "}
        <a
          href="https://github.com/guillevc"
          target="_blank"
          rel="noopener noreferrer"
          className="text-primary/70 hover:text-primary hover:underline"
        >
          guillevc
        </a>
        {__COMMIT_SHA__ !== "dev" && (
          <>
            {" · "}
            <a
              href={`https://github.com/guillevc/yubal/commit/${__COMMIT_SHA__}`}
              target="_blank"
              rel="noopener noreferrer"
              className="group text-primary/70 hover:text-primary"
            >
              <GitBranch className="-mt-px inline h-4 w-4" />{" "}
              <span className="group-hover:underline">
                {__COMMIT_SHA__.slice(0, 7)}
              </span>
            </a>
          </>
        )}
        {" · Powered by "}
        <a
          href="https://github.com/yt-dlp/yt-dlp"
          target="_blank"
          rel="noopener noreferrer"
          className="text-primary/70 hover:text-primary hover:underline"
        >
          yt-dlp
        </a>
        {" & "}
        <a
          href="https://github.com/beetbox/beets"
          target="_blank"
          rel="noopener noreferrer"
          className="text-primary/70 hover:text-primary hover:underline"
        >
          beets
        </a>
      </p>
    </footer>
  );
}

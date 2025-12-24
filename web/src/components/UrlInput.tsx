import { Input } from "@heroui/react";

const YOUTUBE_MUSIC_URL_PATTERN =
  /^https?:\/\/(music\.)?youtube\.com\/(playlist\?list=|watch\?v=|browse\/VL)/;

interface UrlInputProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

export function UrlInput({ value, onChange, disabled }: UrlInputProps) {
  const isValid = value === "" || YOUTUBE_MUSIC_URL_PATTERN.test(value);

  return (
    <Input
      type="url"
      label="YouTube Music URL"
      placeholder="https://music.youtube.com/playlist?list=..."
      value={value}
      onValueChange={onChange}
      isDisabled={disabled}
      isInvalid={!isValid}
      errorMessage={!isValid ? "Enter a valid YouTube Music URL" : undefined}
      description="Paste a YouTube Music album or playlist URL"
      classNames={{
        input: "text-base",
      }}
    />
  );
}

export function isValidUrl(url: string): boolean {
  return YOUTUBE_MUSIC_URL_PATTERN.test(url);
}

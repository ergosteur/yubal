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
      placeholder="Paste YouTube Music URL..."
      value={value}
      onValueChange={onChange}
      isDisabled={disabled}
      isInvalid={!isValid}
      errorMessage={!isValid ? "Enter a valid YouTube Music URL" : undefined}
      size="lg"
      classNames={{
        input: "text-base",
        inputWrapper: "bg-default-100",
      }}
    />
  );
}

export function isValidUrl(url: string): boolean {
  return YOUTUBE_MUSIC_URL_PATTERN.test(url);
}

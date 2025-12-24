import { Button } from "@heroui/react";

interface SyncButtonProps {
  onClick: () => void;
  isLoading: boolean;
  isDisabled: boolean;
}

export function SyncButton({ onClick, isLoading, isDisabled }: SyncButtonProps) {
  return (
    <Button
      color="primary"
      size="lg"
      onPress={onClick}
      isLoading={isLoading}
      isDisabled={isDisabled}
      className="w-full sm:w-auto"
    >
      {isLoading ? "Syncing..." : "Sync Album"}
    </Button>
  );
}

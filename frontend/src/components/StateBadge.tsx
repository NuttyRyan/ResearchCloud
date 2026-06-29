import { Badge } from '@mantine/core';

const COLORS: Record<string, string> = {
  AVAILABLE: 'teal',
  COMPLETE: 'teal',
  ACTIVE: 'teal',
  DEPLOYING: 'nutanix',
  PENDING: 'yellow',
  ERROR: 'red',
};

export function StateBadge({ state }: { state: string }) {
  return (
    <Badge color={COLORS[state] ?? 'gray'} variant="light" radius="sm">
      {state}
    </Badge>
  );
}

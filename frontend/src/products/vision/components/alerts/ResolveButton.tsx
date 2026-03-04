import { Button } from '@/components/ui';

interface ResolveButtonProps {
  onResolve: () => void;
  loading?: boolean;
  className?: string;
}

export function ResolveButton({ onResolve, loading, className }: ResolveButtonProps) {
  return (
    <Button
      variant="outline"
      size="lg"
      fullWidth
      loading={loading}
      onClick={onResolve}
      className={className}
      aria-label="Resolve incident"
    >
      Mark as Resolved
    </Button>
  );
}

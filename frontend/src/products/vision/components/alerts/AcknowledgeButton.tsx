import { Button } from '@/components/ui';
import { cn } from '@/utils/cn';

interface AcknowledgeButtonProps {
  onAcknowledge: () => void;
  loading?: boolean;
  size?: 'md' | 'lg' | 'xl';
  className?: string;
}

export function AcknowledgeButton({ onAcknowledge, loading, size = 'xl', className }: AcknowledgeButtonProps) {
  return (
    <Button
      variant="primary"
      size={size}
      fullWidth
      loading={loading}
      onClick={onAcknowledge}
      className={cn('min-h-[3.5rem] text-lg font-bold uppercase tracking-wide', className)}
      aria-label="Acknowledge alert"
    >
      Acknowledge
    </Button>
  );
}

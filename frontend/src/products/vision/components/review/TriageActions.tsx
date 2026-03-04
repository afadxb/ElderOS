import { Button } from '@/components/ui';
import { Check, X } from 'lucide-react';

interface TriageActionsProps {
  onConfirm: () => void;
  onDismiss: () => void;
}

export function TriageActions({ onConfirm, onDismiss }: TriageActionsProps) {
  return (
    <div className="flex items-center gap-1">
      <Button variant="primary" size="sm" onClick={onConfirm} aria-label="Confirm event">
        <Check className="h-3.5 w-3.5 mr-1" /> Confirm
      </Button>
      <Button variant="ghost" size="sm" onClick={onDismiss} aria-label="Dismiss event">
        <X className="h-3.5 w-3.5 mr-1" /> Dismiss
      </Button>
    </div>
  );
}

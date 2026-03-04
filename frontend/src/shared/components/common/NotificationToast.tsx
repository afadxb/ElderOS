import { useEffect, useState } from 'react';
import { cn } from '@/utils/cn';
import { CheckCircle, AlertTriangle, X, XCircle, Info } from 'lucide-react';

type ToastType = 'success' | 'error' | 'warning' | 'info';

interface ToastProps {
  type: ToastType;
  message: string;
  onClose: () => void;
  duration?: number;
}

const icons = {
  success: CheckCircle,
  error: XCircle,
  warning: AlertTriangle,
  info: Info,
};

const styles = {
  success: 'bg-elder-ok-bg border-elder-ok text-green-800',
  error: 'bg-elder-critical-bg border-elder-critical text-red-800',
  warning: 'bg-elder-warning-bg border-elder-warning text-amber-800',
  info: 'bg-elder-action-bg border-elder-action text-blue-800',
};

export function NotificationToast({ type, message, onClose, duration = 4000 }: ToastProps) {
  const [visible, setVisible] = useState(true);
  const Icon = icons[type];

  useEffect(() => {
    const timer = setTimeout(() => {
      setVisible(false);
      setTimeout(onClose, 200);
    }, duration);
    return () => clearTimeout(timer);
  }, [duration, onClose]);

  return (
    <div
      className={cn(
        'fixed top-4 right-4 z-50 flex items-center gap-2 px-4 py-3 rounded-lg border shadow-lg transition-all duration-200',
        styles[type],
        visible ? 'animate-slide-up' : 'opacity-0 translate-y-2'
      )}
    >
      <Icon className="h-4 w-4 flex-shrink-0" />
      <p className="text-sm font-medium">{message}</p>
      <button onClick={onClose} className="ml-2 hover:opacity-70">
        <X className="h-3.5 w-3.5" />
      </button>
    </div>
  );
}

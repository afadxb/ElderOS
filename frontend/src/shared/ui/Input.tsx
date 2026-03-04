import { forwardRef, type InputHTMLAttributes } from 'react';
import { cn } from '@/utils/cn';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className, id, ...props }, ref) => {
    const inputId = id || label?.toLowerCase().replace(/\s+/g, '-');
    return (
      <div className="space-y-1">
        {label && (
          <label htmlFor={inputId} className="block text-sm font-medium text-elder-text-primary">
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          className={cn(
            'w-full px-3 py-2 text-sm border rounded-md bg-white text-elder-text-primary placeholder:text-elder-text-muted',
            'focus:outline-none focus:ring-2 focus:ring-elder-action focus:border-transparent',
            error ? 'border-elder-critical' : 'border-elder-border',
            className
          )}
          {...props}
        />
        {error && <p className="text-xs text-elder-critical">{error}</p>}
      </div>
    );
  }
);
Input.displayName = 'Input';

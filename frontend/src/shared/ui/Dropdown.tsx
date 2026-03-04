import { useState, useRef, useEffect, type ReactNode } from 'react';
import { cn } from '@/utils/cn';
import { ChevronDown } from 'lucide-react';

interface DropdownProps {
  trigger: ReactNode;
  children: ReactNode;
  align?: 'left' | 'right';
  className?: string;
}

export function Dropdown({ trigger, children, align = 'left', className }: DropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  return (
    <div ref={ref} className={cn('relative inline-block', className)}>
      <div onClick={() => setIsOpen(!isOpen)} className="cursor-pointer">
        {trigger}
      </div>
      {isOpen && (
        <div
          className={cn(
            'absolute z-40 mt-1 min-w-[12rem] bg-elder-surface rounded-md shadow-lg border border-elder-border py-1 animate-fade-in',
            align === 'right' ? 'right-0' : 'left-0'
          )}
        >
          {children}
        </div>
      )}
    </div>
  );
}

interface DropdownItemProps {
  children: ReactNode;
  onClick?: () => void;
  className?: string;
}

export function DropdownItem({ children, onClick, className }: DropdownItemProps) {
  return (
    <button
      onClick={onClick}
      className={cn('w-full text-left px-4 py-2 text-sm text-elder-text-primary hover:bg-elder-surface-alt', className)}
    >
      {children}
    </button>
  );
}

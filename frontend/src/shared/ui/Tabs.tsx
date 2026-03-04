import { cn } from '@/utils/cn';
import type { ReactNode } from 'react';

interface Tab {
  id: string;
  label: string;
}

interface TabsProps {
  tabs: Tab[];
  activeTab: string;
  onChange: (tabId: string) => void;
  className?: string;
}

export function Tabs({ tabs, activeTab, onChange, className }: TabsProps) {
  return (
    <div className={cn('border-b border-elder-border', className)} role="tablist">
      <nav className="flex gap-4">
        {tabs.map(tab => (
          <button
            key={tab.id}
            role="tab"
            aria-selected={activeTab === tab.id}
            onClick={() => onChange(tab.id)}
            className={cn(
              'px-1 py-2.5 text-sm font-medium border-b-2 transition-colors whitespace-nowrap',
              activeTab === tab.id
                ? 'border-elder-action text-elder-action'
                : 'border-transparent text-elder-text-secondary hover:text-elder-text-primary hover:border-gray-300'
            )}
          >
            {tab.label}
          </button>
        ))}
      </nav>
    </div>
  );
}

interface TabPanelProps {
  id: string;
  activeTab: string;
  children: ReactNode;
}

export function TabPanel({ id, activeTab, children }: TabPanelProps) {
  if (id !== activeTab) return null;
  return <div role="tabpanel">{children}</div>;
}

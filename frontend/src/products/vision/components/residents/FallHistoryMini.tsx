interface FallHistoryMiniProps {
  fallCount30Days: number;
  fallCountTotal: number;
}

export function FallHistoryMini({ fallCount30Days, fallCountTotal }: FallHistoryMiniProps) {
  const maxBars = 5;
  const bars = Math.min(fallCount30Days, maxBars);

  return (
    <div className="flex items-end gap-0.5 h-4">
      {Array.from({ length: maxBars }).map((_, i) => (
        <div
          key={i}
          className={`w-1.5 rounded-t ${i < bars ? 'bg-elder-critical' : 'bg-gray-200'}`}
          style={{ height: `${((i + 1) / maxBars) * 100}%` }}
        />
      ))}
      <span className="text-[10px] text-elder-text-muted ml-1">{fallCountTotal}</span>
    </div>
  );
}

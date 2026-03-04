import type { Resident } from '@/types';
import { Card, CardContent } from '@/components/ui';
import { riskScoreToColor, riskScoreToBg } from '@/utils/colorUtils';
import { getRiskLabel } from '@/utils/riskCalculations';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { cn } from '@/utils/cn';

interface RiskScoreCardProps {
  resident: Resident;
  onClick?: () => void;
}

const trendIcons = {
  rising: TrendingUp,
  stable: Minus,
  declining: TrendingDown,
};

const trendColors = {
  rising: 'text-elder-critical',
  stable: 'text-elder-text-secondary',
  declining: 'text-elder-ok',
};

export function RiskScoreCard({ resident, onClick }: RiskScoreCardProps) {
  const TrendIcon = trendIcons[resident.riskTrend];

  return (
    <Card hover={!!onClick} onClick={onClick}>
      <CardContent>
        <div className="flex items-center justify-between">
          <div className="min-w-0">
            <p className="text-sm font-semibold truncate">{resident.name}</p>
            <p className="text-xs text-elder-text-secondary">Room {resident.roomNumber}</p>
          </div>
          <div className="flex items-center gap-2 flex-shrink-0">
            <div className={cn('flex items-center justify-center w-10 h-10 rounded-full text-sm font-bold', riskScoreToBg(resident.riskScore), riskScoreToColor(resident.riskScore))}>
              {resident.riskScore}
            </div>
            <TrendIcon className={cn('h-4 w-4', trendColors[resident.riskTrend])} />
          </div>
        </div>
        <div className="flex items-center gap-3 mt-2 text-xs text-elder-text-secondary">
          <span>Falls (30d): {resident.fallCount30Days}</span>
          <span>{getRiskLabel(resident.riskScore)}</span>
          {resident.observeOnly && <span className="text-elder-warning">Observe only</span>}
        </div>
      </CardContent>
    </Card>
  );
}

import type { Resident } from '@/types';
import { TableRow, TableCell, Badge } from '@/components/ui';
import { riskScoreToColor } from '@/utils/colorUtils';
import { getRiskLabel } from '@/utils/riskCalculations';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { cn } from '@/utils/cn';
import { formatDate } from '@/utils/formatters';

interface ResidentRowProps {
  resident: Resident;
  onClick?: () => void;
}

const trendIcons = { rising: TrendingUp, stable: Minus, declining: TrendingDown };
const trendColors = { rising: 'text-elder-critical', stable: 'text-elder-text-secondary', declining: 'text-elder-ok' };

export function ResidentRow({ resident, onClick }: ResidentRowProps) {
  const TrendIcon = trendIcons[resident.riskTrend];

  return (
    <TableRow onClick={onClick}>
      <TableCell><span className="font-medium">{resident.name}</span></TableCell>
      <TableCell>{resident.roomNumber}</TableCell>
      <TableCell>
        <span className={cn('font-bold', riskScoreToColor(resident.riskScore))}>{resident.riskScore}</span>
      </TableCell>
      <TableCell>
        <div className="flex items-center gap-1">
          <TrendIcon className={cn('h-4 w-4', trendColors[resident.riskTrend])} />
          <span className="text-xs">{resident.riskTrend}</span>
        </div>
      </TableCell>
      <TableCell>{resident.fallCount30Days}</TableCell>
      <TableCell>{resident.lastFallDate ? formatDate(resident.lastFallDate) : '—'}</TableCell>
      <TableCell>
        {resident.observeOnly && <Badge variant="warning">Observe</Badge>}
      </TableCell>
    </TableRow>
  );
}

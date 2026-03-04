import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Table, TableHeader, TableBody, TableHead, Spinner, Card } from '@/components/ui';
import { PageHeader } from '@/components/common/PageHeader';
import { UnitSelector } from '@/components/common/UnitSelector';
import { ResidentRow } from '@/components/residents/ResidentRow';
import { RiskScoreCard } from '@/components/residents/RiskScoreCard';
import { usePagination } from '@/hooks/usePagination';
import { useIsMobile } from '@/hooks/useMediaQuery';
import { Button } from '@/components/ui';
import * as residentService from '@/services/residentService';
import type { Resident } from '@/types';

export function ResidentsPage() {
  const navigate = useNavigate();
  const isMobile = useIsMobile();
  const [residents, setResidents] = useState<Resident[]>([]);
  const [unit, setUnit] = useState('');
  const [sortBy, setSortBy] = useState<'riskScore' | 'name'>('riskScore');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      const data = await residentService.getResidents(unit || undefined);
      setResidents(data);
      setLoading(false);
    }
    load();
  }, [unit]);

  const sorted = [...residents].sort((a, b) =>
    sortBy === 'riskScore' ? b.riskScore - a.riskScore : a.name.localeCompare(b.name)
  );

  const { paginatedItems, page, totalPages, nextPage, prevPage, hasNext, hasPrev } = usePagination(sorted, 20);

  if (loading) return <div className="flex justify-center py-20"><Spinner size="lg" /></div>;

  return (
    <div className="space-y-4">
      <PageHeader
        title="Residents"
        subtitle={`${residents.length} residents monitored`}
        actions={
          <div className="flex items-center gap-2">
            <Button variant={sortBy === 'riskScore' ? 'primary' : 'outline'} size="sm" onClick={() => setSortBy('riskScore')}>By Risk</Button>
            <Button variant={sortBy === 'name' ? 'primary' : 'outline'} size="sm" onClick={() => setSortBy('name')}>By Name</Button>
            <UnitSelector value={unit} onChange={setUnit} />
          </div>
        }
      />

      {isMobile ? (
        <div className="grid grid-cols-1 gap-3">
          {paginatedItems.map(r => (
            <RiskScoreCard key={r.id} resident={r} onClick={() => navigate(`/vision/rooms/${r.roomId}`)} />
          ))}
        </div>
      ) : (
        <Card padding="none">
          <Table>
            <TableHeader>
              <tr>
                <TableHead>Name</TableHead>
                <TableHead>Room</TableHead>
                <TableHead>Risk Score</TableHead>
                <TableHead>Trend</TableHead>
                <TableHead>Falls (30d)</TableHead>
                <TableHead>Last Fall</TableHead>
                <TableHead>Status</TableHead>
              </tr>
            </TableHeader>
            <TableBody>
              {paginatedItems.map(r => (
                <ResidentRow key={r.id} resident={r} onClick={() => navigate(`/vision/rooms/${r.roomId}`)} />
              ))}
            </TableBody>
          </Table>
        </Card>
      )}

      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-elder-text-secondary">Page {page} of {totalPages}</p>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={prevPage} disabled={!hasPrev}>Previous</Button>
            <Button variant="outline" size="sm" onClick={nextPage} disabled={!hasNext}>Next</Button>
          </div>
        </div>
      )}
    </div>
  );
}

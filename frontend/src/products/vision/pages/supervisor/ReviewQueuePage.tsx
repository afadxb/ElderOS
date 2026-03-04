import { useState, useEffect } from 'react';
import { PageHeader } from '@/components/common/PageHeader';
import { ReviewQueueTable } from '@/components/review/ReviewQueueTable';
import { Spinner } from '@/components/ui';
import * as reviewService from '@/services/reviewService';
import type { AlertEvent } from '@/types';

export function ReviewQueuePage() {
  const [events, setEvents] = useState<AlertEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      const data = await reviewService.getReviewQueue();
      setEvents(data);
      setLoading(false);
    }
    load();
  }, []);

  const handleConfirm = async (eventId: string) => {
    await reviewService.triageEvent(eventId, 'confirm');
    setEvents(prev => prev.filter(e => e.id !== eventId));
  };

  const handleDismiss = async (eventId: string) => {
    await reviewService.triageEvent(eventId, 'dismiss');
    setEvents(prev => prev.filter(e => e.id !== eventId));
  };

  if (loading) return <div className="flex justify-center py-20"><Spinner size="lg" /></div>;

  return (
    <div className="space-y-4">
      <PageHeader title="Review Queue" subtitle="Medium-confidence events awaiting triage" />
      <ReviewQueueTable events={events} onConfirm={handleConfirm} onDismiss={handleDismiss} />
    </div>
  );
}

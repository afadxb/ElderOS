import { useParams, useNavigate } from 'react-router-dom';
import { useAlerts } from '@/hooks/useAlerts';
import { AlertCard } from '@/components/alerts/AlertCard';
import { Button } from '@/components/ui';
import { ArrowLeft } from 'lucide-react';

export function NurseAlertView() {
  const { eventId } = useParams<{ eventId: string }>();
  const { activeAlerts, acknowledge, resolve } = useAlerts();
  const navigate = useNavigate();

  const event = activeAlerts.find(a => a.id === eventId);

  if (!event) {
    return (
      <div className="text-center py-12">
        <p className="text-sm text-elder-text-secondary mb-4">Alert not found or already resolved.</p>
        <Button variant="outline" onClick={() => navigate('/vision/alerts')}>
          <ArrowLeft className="h-4 w-4 mr-1" /> Back to Dashboard
        </Button>
      </div>
    );
  }

  return (
    <div className="max-w-lg mx-auto">
      <AlertCard event={event} onAcknowledge={acknowledge} onResolve={resolve} />
    </div>
  );
}

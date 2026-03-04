import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui';
import { PageHeader } from '@/components/common/PageHeader';
import { Film } from 'lucide-react';

export function ClipReviewPage() {
  return (
    <div className="space-y-4">
      <PageHeader title="Clip Review" subtitle="Video clip access requests — audit logged" />
      <Card>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <Film className="h-12 w-12 text-elder-text-muted mb-3" />
            <h3 className="text-sm font-medium text-elder-text-primary mb-1">Clip review requires backend</h3>
            <p className="text-sm text-elder-text-secondary max-w-sm">
              Video clip access is controlled by role-based authorization. Every access is logged in the audit trail. This feature requires the edge appliance backend.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

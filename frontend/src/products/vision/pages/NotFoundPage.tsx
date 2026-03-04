import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui';

export function NotFoundPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex items-center justify-center bg-elder-surface-alt p-4">
      <div className="text-center">
        <p className="text-6xl font-bold text-elder-text-muted mb-2">404</p>
        <h1 className="text-xl font-semibold text-elder-text-primary mb-2">Page not found</h1>
        <p className="text-sm text-elder-text-secondary mb-6">The page you are looking for does not exist.</p>
        <Button onClick={() => navigate('/')}>Return Home</Button>
      </div>
    </div>
  );
}

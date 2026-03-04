import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as reviewService from '../services/reviewService';

export function useReviewQueue() {
  return useQuery({
    queryKey: ['review-queue'],
    queryFn: () => reviewService.getReviewQueue(),
    refetchInterval: 15_000,
  });
}

export function useTriageEvent() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ eventId, action }: { eventId: string; action: 'confirm' | 'dismiss' }) =>
      reviewService.triageEvent(eventId, action),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['review-queue'] });
    },
  });
}

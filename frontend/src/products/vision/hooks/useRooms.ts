import { useQuery } from '@tanstack/react-query';
import * as roomService from '../services/roomService';

export function useRooms(unit?: string) {
  return useQuery({
    queryKey: ['rooms', unit],
    queryFn: () => roomService.getRooms(unit),
  });
}

export function useRoom(roomId: string | undefined) {
  return useQuery({
    queryKey: ['rooms', roomId],
    queryFn: () => roomService.getRoomById(roomId!),
    enabled: !!roomId,
  });
}

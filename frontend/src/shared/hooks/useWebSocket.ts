import { useState } from 'react';

export function useWebSocket() {
  const [connected] = useState(true);
  return { connected, lastMessage: null as string | null };
}

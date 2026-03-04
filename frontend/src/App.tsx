import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '@/context/AuthContext';
import { AlertProvider } from '@/context/AlertContext';
import { AppRouter } from '@/router';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      refetchOnWindowFocus: false,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <AlertProvider>
            <AppRouter />
          </AlertProvider>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

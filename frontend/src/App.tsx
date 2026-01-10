import { RouterProvider, createRouter } from '@tanstack/react-router';
import { QueryClientProvider } from '@tanstack/react-query';
import { lazy, Suspense } from 'react';
import { routeTree } from './routeTree.gen';
import { queryClient } from './lib/query-client';
import { ThemeProvider } from './hooks/useTheme';

// Conditionally import ReactQueryDevtools only in development
const ReactQueryDevtools = import.meta.env.DEV
  ? lazy(() =>
      import('@tanstack/react-query-devtools').then((d) => ({
        default: d.ReactQueryDevtools,
      }))
    )
  : null;

// Create a new router instance
const router = createRouter({
  routeTree,
});

// Register the router instance for type safety
declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider defaultTheme="system" storageKey="focusmate-ui-theme">
        <RouterProvider router={router} />
        {ReactQueryDevtools && (
          <Suspense fallback={null}>
            <ReactQueryDevtools initialIsOpen={false} />
          </Suspense>
        )}
      </ThemeProvider>
    </QueryClientProvider>
  );
}

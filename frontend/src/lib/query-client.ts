/**
 * React Query client configuration.
 *
 * Balanced for real-time feel + performance optimization:
 * - Disabled automatic polling (WebSocket handles real-time updates)
 * - Smart refetching on user actions (mount, reconnect for fresh data)
 * - Optimized cache times for different data types
 * - Fast failure for better UX
 *
 * Strategy:
 * - Static data (profiles, settings): Long cache (5-10min)
 * - Dynamic data (notifications, messages): WebSocket + no polling
 * - Semi-dynamic (rankings, stats): Refetch on mount, no polling
 */

import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Performance: Disable automatic polling (WebSocket handles real-time)
      refetchInterval: false,       // No automatic polling - WebSocket handles updates

      // User Experience: Smart refetching for freshness
      refetchOnMount: true,         // ✅ Refetch on component mount (feels fresh)
      refetchOnWindowFocus: false,  // ❌ Don't refetch on tab switch (too aggressive)
      refetchOnReconnect: true,     // ✅ Refetch when network reconnects (good UX)

      // Caching: Balance freshness vs performance
      staleTime: 1000 * 30,         // 30 seconds - short enough to feel fresh
      gcTime: 1000 * 60 * 10,       // 10 minutes - keep in memory for fast navigation

      // Error handling: Fail fast for better UX
      retry: 1,                      // Only retry once
      retryDelay: 1000,             // 1 second between retries

      // Network: Optimize for reliability
      networkMode: 'online',        // Only run when online
    },
    mutations: {
      retry: 1,
      networkMode: 'online',
    },
  },
});

/**
 * Usage patterns:
 *
 * 1. Real-time data (notifications, messages):
 *    - Use WebSocket
 *    - Set staleTime: Infinity (data is always fresh via WebSocket)
 *    - Set refetchInterval: false
 *
 * 2. Frequently changing data (rankings, live stats):
 *    - Use default config (refetchOnMount: true)
 *    - Data refreshes when user navigates to page
 *    - No polling needed
 *
 * 3. Static data (user profile, settings):
 *    - Set staleTime: 1000 * 60 * 5 (5 minutes)
 *    - Rarely needs refresh
 *
 * 4. Critical fresh data (dashboard):
 *    - Keep default (30s staleTime)
 *    - Feels fresh without excessive requests
 */

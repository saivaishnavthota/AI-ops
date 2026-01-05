import { createApi, fetchBaseQuery, BaseQueryFn, FetchArgs, FetchBaseQueryError } from '@reduxjs/toolkit/query/react';
import type { RootState } from '../../app/store';
import { setAccessToken } from '../slices/authSlice';

const baseQuery = fetchBaseQuery({
  baseUrl: '/api/v1',
  prepareHeaders: (headers, { getState }) => {
    const token = (getState() as RootState).auth.accessToken;
    if (token) {
      headers.set('authorization', `Bearer ${token}`);
    }
    // Add cache-control headers to prevent caching
    headers.set('Cache-Control', 'no-cache, no-store, must-revalidate');
    headers.set('Pragma', 'no-cache');
    headers.set('Expires', '0');
    return headers;
  },
  fetchFn: (input, options) => {
    // Add timestamp to URL to bypass browser cache
    const url = typeof input === 'string' ? input : input.url;
    const separator = url.includes('?') ? '&' : '?';
    const cacheBuster = `_t=${Date.now()}`;
    const newUrl = `${url}${separator}${cacheBuster}`;

    if (typeof input === 'string') {
      return fetch(newUrl, {
        ...options,
        cache: 'no-store', // Disable browser cache
      });
    } else {
      return fetch(new Request(newUrl, input), {
        ...options,
        cache: 'no-store',
      });
    }
  },
});

// Custom base query with token refresh
const baseQueryWithReauth: BaseQueryFn<string | FetchArgs, unknown, FetchBaseQueryError> = async (
  args,
  api,
  extraOptions
) => {
  let result = await baseQuery(args, api, extraOptions);

  if (result.error && result.error.status === 401) {
    // Try to refresh the token
    const refreshToken = (api.getState() as RootState).auth.refreshToken;

    if (refreshToken) {
      const refreshResult = await baseQuery(
        {
          url: '/auth/refresh',
          method: 'POST',
          body: { refresh_token: refreshToken },
        },
        api,
        extraOptions
      );

      if (refreshResult.data && !refreshResult.error) {
        // Store the new token
        const data = refreshResult.data as { access_token: string; refresh_token?: string };
        api.dispatch(setAccessToken(data.access_token));
        
        // Update refresh token if provided
        if (data.refresh_token) {
          localStorage.setItem('refreshToken', data.refresh_token);
        }

        // Retry the original query with new token
        result = await baseQuery(args, api, extraOptions);
      } else {
        // Refresh failed, logout
        api.dispatch({ type: 'auth/logout' });
      }
    } else {
      api.dispatch({ type: 'auth/logout' });
    }
  }

  return result;
};

export const baseApi = createApi({
  reducerPath: 'api',
  baseQuery: baseQueryWithReauth,
  tagTypes: ['User', 'Incident', 'Alert', 'Team', 'Organization', 'Playbook'],
  endpoints: () => ({}),
});

import { baseApi } from './baseApi';

export interface Notification {
    id: string;
    title: string;
    message: string;
    type: 'info' | 'warning' | 'error' | 'success' | 'alert' | 'incident' | 'system';
    priority: 'low' | 'medium' | 'high' | 'urgent';
    is_read: boolean;
    read_at?: string;
    action_url?: string;
    action_label?: string;
    related_entity_type?: string;
    related_entity_id?: string;
    created_at: string;
    updated_at: string;
}

export interface NotificationListResponse {
    items: Notification[];
    total: number;
    page: number;
    page_size: number;
    unread_count: number;
}

export interface NotificationStats {
    total: number;
    unread: number;
    by_type: Record<string, number>;
    by_priority: Record<string, number>;
}

export const notificationsApi = baseApi.injectEndpoints({
    endpoints: (builder) => ({
        getNotifications: builder.query<NotificationListResponse, {
            page?: number;
            page_size?: number;
            unread_only?: boolean;
            type?: string;
            priority?: string;
        }>({
            query: (params = {}) => ({
                url: '/notifications',
                params: {
                    page: 1,
                    page_size: 20,
                    ...params,
                },
            }),
            providesTags: ['Notification'],
        }),

        getNotificationStats: builder.query<NotificationStats, void>({
            query: () => '/notifications/stats',
            providesTags: ['Notification'],
        }),

        getNotification: builder.query<Notification, string>({
            query: (id) => `/notifications/${id}`,
            providesTags: (result, error, id) => [{ type: 'Notification', id }],
        }),

        markNotificationRead: builder.mutation<Notification, string>({
            query: (id) => ({
                url: `/notifications/${id}/read`,
                method: 'POST',
            }),
            invalidatesTags: ['Notification'],
        }),

        markMultipleRead: builder.mutation<{ marked_read: number }, string[]>({
            query: (notification_ids) => ({
                url: '/notifications/mark-read',
                method: 'POST',
                body: { notification_ids },
            }),
            invalidatesTags: ['Notification'],
        }),

        markAllRead: builder.mutation<{ marked_read: number }, void>({
            query: () => ({
                url: '/notifications/mark-all-read',
                method: 'POST',
            }),
            invalidatesTags: ['Notification'],
        }),

        deleteNotification: builder.mutation<void, string>({
            query: (id) => ({
                url: `/notifications/${id}`,
                method: 'DELETE',
            }),
            invalidatesTags: ['Notification'],
        }),
    }),
});

export const {
    useGetNotificationsQuery,
    useGetNotificationStatsQuery,
    useGetNotificationQuery,
    useMarkNotificationReadMutation,
    useMarkMultipleReadMutation,
    useMarkAllReadMutation,
    useDeleteNotificationMutation,
} = notificationsApi;
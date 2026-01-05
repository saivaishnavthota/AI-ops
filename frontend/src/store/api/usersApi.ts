import { baseApi } from './baseApi';

export interface User {
  id: string;
  organization_id: string;
  email: string;
  first_name: string | null;
  last_name: string | null;
  full_name: string;
  role: 'super_admin' | 'admin' | 'operator' | 'viewer';
  phone: string | null;
  job_title: string | null;
  avatar_url: string | null;
  is_active: boolean;
  is_verified: boolean;
  mfa_enabled: boolean;
  last_login: string | null;
  created_at: string;
  updated_at: string;
}

interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

interface ListUsersParams {
  page?: number;
  page_size?: number;
  search?: string;
  role?: string;
  is_active?: boolean;
}

interface CreateUserRequest {
  email: string;
  password?: string;
  first_name: string;
  last_name: string;
  role?: string;
  phone?: string;
  job_title?: string;
}

interface UpdateUserRequest {
  email?: string;
  first_name?: string;
  last_name?: string;
  phone?: string;
  job_title?: string;
  role?: string;
  is_active?: boolean;
}

export const usersApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    listUsers: builder.query<PaginatedResponse<User>, ListUsersParams>({
      query: (params) => ({
        url: '/users',
        params,
      }),
      providesTags: (result) =>
        result
          ? [
              ...result.items.map(({ id }) => ({ type: 'User' as const, id })),
              { type: 'User', id: 'LIST' },
            ]
          : [{ type: 'User', id: 'LIST' }],
    }),

    getUser: builder.query<User, string>({
      query: (id) => `/users/${id}`,
      providesTags: (result, error, id) => [{ type: 'User', id }],
    }),

    createUser: builder.mutation<User, CreateUserRequest>({
      query: (data) => ({
        url: '/users',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: [{ type: 'User', id: 'LIST' }],
    }),

    updateUser: builder.mutation<User, { id: string; data: UpdateUserRequest }>({
      query: ({ id, data }) => ({
        url: `/users/${id}`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'User', id },
        { type: 'User', id: 'LIST' },
      ],
    }),

    deleteUser: builder.mutation<{ message: string }, string>({
      query: (id) => ({
        url: `/users/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: (result, error, id) => [
        { type: 'User', id },
        { type: 'User', id: 'LIST' },
      ],
    }),

    activateUser: builder.mutation<User, string>({
      query: (id) => ({
        url: `/users/${id}/activate`,
        method: 'POST',
      }),
      invalidatesTags: (result, error, id) => [
        { type: 'User', id },
        { type: 'User', id: 'LIST' },
      ],
    }),

    deactivateUser: builder.mutation<User, string>({
      query: (id) => ({
        url: `/users/${id}/deactivate`,
        method: 'POST',
      }),
      invalidatesTags: (result, error, id) => [
        { type: 'User', id },
        { type: 'User', id: 'LIST' },
      ],
    }),

    changeUserRole: builder.mutation<User, { id: string; role: string }>({
      query: ({ id, role }) => ({
        url: `/users/${id}/change-role`,
        method: 'POST',
        params: { role },
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'User', id },
        { type: 'User', id: 'LIST' },
      ],
    }),
  }),
});

export const {
  useListUsersQuery,
  useGetUserQuery,
  useCreateUserMutation,
  useUpdateUserMutation,
  useDeleteUserMutation,
  useActivateUserMutation,
  useDeactivateUserMutation,
  useChangeUserRoleMutation,
} = usersApi;

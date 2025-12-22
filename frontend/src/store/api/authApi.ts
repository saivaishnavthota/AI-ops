import { baseApi } from './baseApi';
import type { User, LoginResponse, MessageResponse } from '../../types/models.types';

interface LoginRequest {
  email: string;
  password: string;
  remember_me?: boolean;
}

interface RegisterRequest {
  organization_name: string;
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

interface PasswordResetRequest {
  email: string;
}

interface PasswordResetConfirm {
  token: string;
  new_password: string;
}

interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

export const authApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    login: builder.mutation<LoginResponse, LoginRequest>({
      query: (credentials) => ({
        url: '/auth/login',
        method: 'POST',
        body: credentials,
      }),
    }),

    register: builder.mutation<LoginResponse, RegisterRequest>({
      query: (data) => ({
        url: '/auth/register',
        method: 'POST',
        body: data,
      }),
    }),

    logout: builder.mutation<MessageResponse, void>({
      query: () => ({
        url: '/auth/logout',
        method: 'POST',
      }),
    }),

    getMe: builder.query<User, void>({
      query: () => '/auth/me',
      providesTags: ['User'],
    }),

    updateProfile: builder.mutation<User, Partial<User>>({
      query: (data) => ({
        url: '/auth/me',
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: ['User'],
    }),

    forgotPassword: builder.mutation<MessageResponse, PasswordResetRequest>({
      query: (data) => ({
        url: '/auth/forgot-password',
        method: 'POST',
        body: data,
      }),
    }),

    resetPassword: builder.mutation<MessageResponse, PasswordResetConfirm>({
      query: (data) => ({
        url: '/auth/reset-password',
        method: 'POST',
        body: data,
      }),
    }),

    changePassword: builder.mutation<MessageResponse, ChangePasswordRequest>({
      query: (data) => ({
        url: '/auth/change-password',
        method: 'POST',
        body: data,
      }),
    }),
  }),
});

export const {
  useLoginMutation,
  useRegisterMutation,
  useLogoutMutation,
  useGetMeQuery,
  useUpdateProfileMutation,
  useForgotPasswordMutation,
  useResetPasswordMutation,
  useChangePasswordMutation,
} = authApi;

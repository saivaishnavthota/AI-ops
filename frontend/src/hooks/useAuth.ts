import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { useCallback } from 'react';

import type { RootState } from '../app/store';
import { logout as logoutAction, setCredentials } from '../store/slices/authSlice';
import type { User, LoginResponse } from '../types/models.types';

export const useAuth = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { user, accessToken, isAuthenticated, isLoading } = useSelector(
    (state: RootState) => state.auth
  );

  const login = useCallback(
    (user: User, tokens: LoginResponse) => {
      dispatch(
        setCredentials({
          user,
          accessToken: tokens.access_token,
          refreshToken: tokens.refresh_token,
        })
      );
      navigate('/');
    },
    [dispatch, navigate]
  );

  const logout = useCallback(() => {
    dispatch(logoutAction());
    navigate('/login');
  }, [dispatch, navigate]);

  const hasPermission = useCallback(
    (permission: string): boolean => {
      if (!user) return false;
      if (user.role === 'admin' || user.role === 'super_admin') return true;
      return user.permissions?.includes(permission) ?? false;
    },
    [user]
  );

  const hasRole = useCallback(
    (roles: string[]): boolean => {
      if (!user) return false;
      return roles.includes(user.role);
    },
    [user]
  );

  return {
    user,
    accessToken,
    isAuthenticated,
    isLoading,
    login,
    logout,
    hasPermission,
    hasRole,
    isAdmin: user?.role === 'admin' || user?.role === 'super_admin',
  };
};

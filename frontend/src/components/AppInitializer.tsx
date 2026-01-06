import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Spin } from 'antd';

import type { RootState, AppDispatch } from '../app/store';
import { authApi } from '../store/api/authApi';
import { setCredentials, setLoading } from '../store/slices/authSlice';

interface AppInitializerProps {
    children: React.ReactNode;
}

const AppInitializer: React.FC<AppInitializerProps> = ({ children }) => {
    const dispatch = useDispatch<AppDispatch>();
    const { isAuthenticated, isLoading } = useSelector((state: RootState) => state.auth);

    useEffect(() => {
        const initializeApp = async () => {
            const accessToken = localStorage.getItem('accessToken');
            const refreshToken = localStorage.getItem('refreshToken');

            if (accessToken && refreshToken && !isAuthenticated) {
                dispatch(setLoading(true));

                try {
                    // Fetch user data with existing token
                    const userResponse = await dispatch(
                        authApi.endpoints.getMe.initiate()
                    ).unwrap();

                    // Update Redux store with user and tokens
                    dispatch(setCredentials({
                        user: userResponse,
                        accessToken,
                        refreshToken,
                    }));
                } catch (error) {
                    // Token is invalid, clear storage
                    localStorage.removeItem('accessToken');
                    localStorage.removeItem('refreshToken');
                    localStorage.removeItem('user');
                } finally {
                    dispatch(setLoading(false));
                }
            }
        };

        initializeApp();
    }, [dispatch, isAuthenticated]);

    if (isLoading) {
        return (
            <div style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                height: '100vh'
            }}>
                <Spin size="large" />
            </div>
        );
    }

    return <>{children}</>;
};

export default AppInitializer;
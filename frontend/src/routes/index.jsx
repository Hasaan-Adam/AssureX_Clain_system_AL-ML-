import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from '../components/common/ProtectedRoute';
import RoleRoute from '../components/common/RoleRoute';

import LandingPage from '../pages/LandingPage';
import LoginPage from '../pages/LoginPage';
import RegisterPage from '../pages/RegisterPage';
import DashboardPage from '../pages/DashboardPage';
import ProductsPage from '../pages/ProductsPage';
import WarrantiesPage from '../pages/WarrantiesPage';
import ClaimsPage from '../pages/ClaimsPage';
import NewClaimPage from '../pages/NewClaimPage';
import ClaimDetailPage from '../pages/ClaimDetailPage';
import ReviewQueuePage from '../pages/ReviewQueuePage';
import AdminDashboardPage from '../pages/AdminDashboardPage';
import AnalyticsPage from '../pages/AnalyticsPage';
import SettingsPage from '../pages/SettingsPage';
import ProfilePage from '../pages/ProfilePage';
import UsersPage from '../pages/UsersPage';
import { AuditLogsPage } from '../pages/AuditLogsPage';
import { PoliciesPage } from '../pages/PoliciesPage';
import NotFoundPage from '../pages/NotFoundPage';
import ReportsPage from '../pages/ReportsPage';

export const AppRoutes = () => {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/products" element={<ProductsPage />} />

      {/* Protected Customer & Common Routes */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/warranties"
        element={
          <ProtectedRoute>
            <WarrantiesPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/claims"
        element={
          <ProtectedRoute>
            <ClaimsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/claims/new"
        element={
          <ProtectedRoute>
            <NewClaimPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/claims/:id"
        element={
          <ProtectedRoute>
            <ClaimDetailPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/claims/by-number/:claimNumber"
        element={
          <ProtectedRoute>
            <ClaimDetailPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/profile"
        element={
          <ProtectedRoute>
            <ProfilePage />
          </ProtectedRoute>
        }
      />

      {/* Reviewer / Staff Routes */}
      <Route
        path="/reviews"
        element={
          <RoleRoute allowedRoles={['reviewer', 'staff', 'service_staff', 'admin']}>
            <ReviewQueuePage />
          </RoleRoute>
        }
      />
      <Route
        path="/analytics"
        element={
          <RoleRoute allowedRoles={['reviewer', 'staff', 'service_staff', 'admin']}>
            <AnalyticsPage />
          </RoleRoute>
        }
      />
      <Route
        path="/reports"
        element={
          <RoleRoute allowedRoles={['reviewer', 'staff', 'service_staff', 'admin']}>
            <ReportsPage />
          </RoleRoute>
        }
      />

      {/* Admin Operations Routes */}
      <Route
        path="/admin"
        element={
          <RoleRoute allowedRoles={['admin']}>
            <AdminDashboardPage />
          </RoleRoute>
        }
      />
      <Route
        path="/admin/audit-logs"
        element={
          <RoleRoute allowedRoles={['admin']}>
            <AuditLogsPage />
          </RoleRoute>
        }
      />
      <Route
        path="/admin/policies"
        element={
          <RoleRoute allowedRoles={['admin']}>
            <PoliciesPage />
          </RoleRoute>
        }
      />
      <Route
        path="/users"
        element={
          <RoleRoute allowedRoles={['admin']}>
            <UsersPage />
          </RoleRoute>
        }
      />
      <Route
        path="/settings"
        element={
          <RoleRoute allowedRoles={['admin']}>
            <SettingsPage />
          </RoleRoute>
        }
      />

      {/* 404 Fallback */}
      <Route path="/404" element={<NotFoundPage />} />
      <Route path="*" element={<Navigate to="/404" replace />} />
    </Routes>
  );
};

export default AppRoutes;
import { Center, Loader } from '@mantine/core';
import { Navigate, Route, Routes } from 'react-router-dom';
import { useAuth } from './auth/AuthContext';
import { AppLayout } from './components/AppLayout';
import { ConnectionProvider } from './state/ConnectionContext';
import { ConnectionsPage } from './pages/ConnectionsPage';
import { DashboardPage } from './pages/DashboardPage';
import { FilesPage } from './pages/FilesPage';
import { LoginPage } from './pages/LoginPage';
import { ObjectsPage } from './pages/ObjectsPage';
import { ProjectsPage } from './pages/ProjectsPage';

export default function App() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <Center mih="100vh">
        <Loader color="nutanix" />
      </Center>
    );
  }

  if (!user) {
    return (
      <Routes>
        <Route path="*" element={<LoginPage />} />
      </Routes>
    );
  }

  return (
    <ConnectionProvider>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/connections" element={<ConnectionsPage />} />
          <Route path="/projects" element={<ProjectsPage />} />
          <Route path="/files" element={<FilesPage />} />
          <Route path="/objects" element={<ObjectsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </ConnectionProvider>
  );
}

import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import { useAuth } from '../auth/AuthContext';

interface ConnectionContextValue {
  activeId: number | null;
  setActiveId: (id: number | null) => void;
}

const ConnectionContext = createContext<ConnectionContextValue | undefined>(
  undefined,
);

const STORAGE_KEY = 'rc_active_connection';

export function ConnectionProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth();
  const [activeId, setActiveIdState] = useState<number | null>(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? Number(stored) : null;
  });

  const { data: connections } = useQuery({
    queryKey: ['connections'],
    queryFn: api.listConnections,
    enabled: !!user,
  });

  const setActiveId = (id: number | null) => {
    setActiveIdState(id);
    if (id === null) localStorage.removeItem(STORAGE_KEY);
    else localStorage.setItem(STORAGE_KEY, String(id));
  };

  // Auto-select the first connection if none chosen or the chosen one vanished.
  useEffect(() => {
    if (!connections) return;
    const exists = connections.some((c) => c.id === activeId);
    if (!exists) {
      setActiveId(connections.length > 0 ? connections[0].id : null);
    }
  }, [connections, activeId]);

  const value = useMemo(() => ({ activeId, setActiveId }), [activeId]);
  return (
    <ConnectionContext.Provider value={value}>
      {children}
    </ConnectionContext.Provider>
  );
}

export function useActiveConnection(): ConnectionContextValue {
  const ctx = useContext(ConnectionContext);
  if (!ctx)
    throw new Error('useActiveConnection must be used within ConnectionProvider');
  return ctx;
}

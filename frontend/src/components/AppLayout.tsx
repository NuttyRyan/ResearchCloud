import {
  ActionIcon,
  AppShell,
  Avatar,
  Badge,
  Burger,
  Group,
  Menu,
  NavLink,
  Select,
  Text,
  Title,
  Tooltip,
} from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import {
  IconBox,
  IconCloud,
  IconFolders,
  IconLayoutDashboard,
  IconLogout,
  IconPlugConnected,
  IconServer2,
} from '@tabler/icons-react';
import { useQuery } from '@tanstack/react-query';
import { NavLink as RouterNavLink, Outlet, useLocation } from 'react-router-dom';
import { api } from '../api/client';
import { useAuth } from '../auth/AuthContext';
import { useActiveConnection } from '../state/ConnectionContext';

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', icon: IconLayoutDashboard, end: true },
  { to: '/connections', label: 'Prism Central', icon: IconPlugConnected },
  { to: '/projects', label: 'Projects', icon: IconFolders },
  { to: '/files', label: 'Files', icon: IconServer2 },
  { to: '/objects', label: 'Objects', icon: IconBox },
];

export function AppLayout() {
  const [opened, { toggle }] = useDisclosure();
  const { user, logout } = useAuth();
  const { activeId, setActiveId } = useActiveConnection();
  const location = useLocation();

  const { data: connections } = useQuery({
    queryKey: ['connections'],
    queryFn: api.listConnections,
  });

  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: api.health,
  });

  return (
    <AppShell
      header={{ height: 60 }}
      navbar={{ width: 250, breakpoint: 'sm', collapsed: { mobile: !opened } }}
      padding="lg"
    >
      <AppShell.Header>
        <Group h="100%" px="md" justify="space-between">
          <Group gap="xs">
            <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" />
            <IconCloud size={28} color="var(--mantine-color-nutanix-5)" />
            <Title order={3} c="nutanix.7">
              ResearchCloud
            </Title>
            {health?.mode === 'mock' && (
              <Badge color="yellow" variant="light" radius="sm" title="Using mock Nutanix provider">
                MOCK MODE
              </Badge>
            )}
          </Group>
          <Group>
            <Select
              size="xs"
              placeholder="Select Prism Central"
              w={220}
              data={(connections ?? []).map((c) => ({
                value: String(c.id),
                label: `${c.name} (${c.host})`,
              }))}
              value={activeId ? String(activeId) : null}
              onChange={(v) => setActiveId(v ? Number(v) : null)}
              leftSection={<IconPlugConnected size={14} />}
              aria-label="Active Prism Central connection"
            />
            <Menu position="bottom-end" withArrow>
              <Menu.Target>
                <Tooltip label={user?.username ?? ''}>
                  <ActionIcon variant="light" radius="xl" size="lg" aria-label="Account">
                    <Avatar color="nutanix" radius="xl" size={28}>
                      {user?.username?.[0]?.toUpperCase() ?? '?'}
                    </Avatar>
                  </ActionIcon>
                </Tooltip>
              </Menu.Target>
              <Menu.Dropdown>
                <Menu.Label>{user?.username}</Menu.Label>
                <Menu.Item
                  leftSection={<IconLogout size={14} />}
                  onClick={logout}
                >
                  Sign out
                </Menu.Item>
              </Menu.Dropdown>
            </Menu>
          </Group>
        </Group>
      </AppShell.Header>

      <AppShell.Navbar p="md">
        {NAV_ITEMS.map((item) => {
          const active =
            item.end
              ? location.pathname === item.to
              : location.pathname.startsWith(item.to);
          return (
            <NavLink
              key={item.to}
              component={RouterNavLink}
              to={item.to}
              label={item.label}
              leftSection={<item.icon size={18} />}
              active={active}
              variant="filled"
              mb={4}
            />
          );
        })}
        <Text size="xs" c="dimmed" mt="auto" pt="md">
          v0.1.0 - Phase 1
        </Text>
      </AppShell.Navbar>

      <AppShell.Main>
        <Outlet />
      </AppShell.Main>
    </AppShell>
  );
}

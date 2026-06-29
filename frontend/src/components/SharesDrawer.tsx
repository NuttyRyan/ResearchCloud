import {
  ActionIcon,
  Button,
  Divider,
  Drawer,
  Group,
  NumberInput,
  Paper,
  Select,
  Stack,
  Table,
  Text,
  TextInput,
  Title,
} from '@mantine/core';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import { IconPlus, IconTrash } from '@tabler/icons-react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { api, ApiError } from '../api/client';
import type { FileServer, ShareAccess, SharePermission } from '../api/types';
import { StateBadge } from './StateBadge';

const ACCESS_OPTIONS: ShareAccess[] = ['READ_WRITE', 'READ_ONLY', 'NO_ACCESS'];

export function SharesDrawer({
  connectionId,
  fileServer,
  onClose,
}: {
  connectionId: number;
  fileServer: FileServer | null;
  onClose: () => void;
}) {
  const queryClient = useQueryClient();
  const opened = fileServer !== null;
  const fsExtId = fileServer?.ext_id ?? '';

  const [permissions, setPermissions] = useState<SharePermission[]>([]);
  const [principal, setPrincipal] = useState('');
  const [access, setAccess] = useState<ShareAccess>('READ_WRITE');

  const { data: shares } = useQuery({
    queryKey: ['shares', connectionId, fsExtId],
    queryFn: () => api.listShares(connectionId, fsExtId),
    enabled: opened,
  });

  const form = useForm({
    initialValues: { name: '', protocol: 'SMB' as 'SMB' | 'NFS', size_gib: 100 },
    validate: { name: (v) => (v ? null : 'Required') },
  });

  const createMut = useMutation({
    mutationFn: (values: { name: string; protocol: 'SMB' | 'NFS'; size_gib: number }) =>
      api.createShare(connectionId, fsExtId, { ...values, permissions }),
    onSuccess: (share) => {
      queryClient.invalidateQueries({ queryKey: ['shares', connectionId, fsExtId] });
      notifications.show({ color: 'teal', message: `Share "${share.name}" created` });
      form.reset();
      setPermissions([]);
    },
    onError: (e) =>
      notifications.show({
        color: 'red',
        message: e instanceof ApiError ? e.message : 'Failed to create share',
      }),
  });

  const addPermission = () => {
    if (!principal.trim()) return;
    setPermissions((p) => [...p, { principal: principal.trim(), access }]);
    setPrincipal('');
    setAccess('READ_WRITE');
  };

  return (
    <Drawer
      opened={opened}
      onClose={onClose}
      position="right"
      size="lg"
      title={<Title order={4}>Shares - {fileServer?.name}</Title>}
    >
      <Stack>
        <Paper withBorder radius="md" p="md">
          <Table verticalSpacing="sm">
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Name</Table.Th>
                <Table.Th>Protocol</Table.Th>
                <Table.Th>Size (GiB)</Table.Th>
                <Table.Th>Permissions</Table.Th>
                <Table.Th>State</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {shares?.map((s) => (
                <Table.Tr key={s.ext_id}>
                  <Table.Td>
                    <Text fw={600}>{s.name}</Text>
                  </Table.Td>
                  <Table.Td>{s.protocol}</Table.Td>
                  <Table.Td>{s.size_gib.toLocaleString()}</Table.Td>
                  <Table.Td>
                    {s.permissions.length === 0 ? (
                      <Text c="dimmed">-</Text>
                    ) : (
                      s.permissions
                        .map((p) => `${p.principal}: ${p.access}`)
                        .join(', ')
                    )}
                  </Table.Td>
                  <Table.Td>
                    <StateBadge state={s.state} />
                  </Table.Td>
                </Table.Tr>
              ))}
              {(shares?.length ?? 0) === 0 && (
                <Table.Tr>
                  <Table.Td colSpan={5}>
                    <Text c="dimmed" ta="center" py="sm">
                      No shares yet.
                    </Text>
                  </Table.Td>
                </Table.Tr>
              )}
            </Table.Tbody>
          </Table>
        </Paper>

        <Divider label="Create share" labelPosition="center" />

        <form onSubmit={form.onSubmit((v) => createMut.mutate(v))}>
          <Stack>
            <TextInput label="Name" placeholder="datasets" required {...form.getInputProps('name')} />
            <Group grow>
              <Select
                label="Protocol"
                data={['SMB', 'NFS']}
                {...form.getInputProps('protocol')}
              />
              <NumberInput label="Size (GiB)" min={1} {...form.getInputProps('size_gib')} />
            </Group>

            <div>
              <Text size="sm" fw={500} mb={4}>
                Permissions
              </Text>
              {permissions.map((p, i) => (
                <Group key={`${p.principal}-${i}`} gap="xs" mb={4}>
                  <Text size="sm" style={{ flex: 1 }}>
                    {p.principal}
                  </Text>
                  <Text size="sm" c="dimmed">
                    {p.access}
                  </Text>
                  <ActionIcon
                    variant="subtle"
                    color="red"
                    onClick={() => setPermissions((arr) => arr.filter((_, j) => j !== i))}
                    aria-label={`Remove ${p.principal}`}
                  >
                    <IconTrash size={14} />
                  </ActionIcon>
                </Group>
              ))}
              <Group gap="xs" align="flex-end">
                <TextInput
                  placeholder="AD group / user"
                  value={principal}
                  onChange={(e) => setPrincipal(e.currentTarget.value)}
                  style={{ flex: 1 }}
                />
                <Select
                  data={ACCESS_OPTIONS}
                  value={access}
                  onChange={(v) => setAccess((v as ShareAccess) ?? 'READ_WRITE')}
                  w={150}
                />
                <ActionIcon variant="light" onClick={addPermission} aria-label="Add permission">
                  <IconPlus size={16} />
                </ActionIcon>
              </Group>
            </div>

            <Button type="submit" loading={createMut.isPending}>
              Create share
            </Button>
          </Stack>
        </form>
      </Stack>
    </Drawer>
  );
}

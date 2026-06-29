import {
  ActionIcon,
  Button,
  Checkbox,
  Group,
  Modal,
  NumberInput,
  Paper,
  PasswordInput,
  Stack,
  Table,
  Text,
  TextInput,
  Title,
  Tooltip,
} from '@mantine/core';
import { useForm } from '@mantine/form';
import { useDisclosure } from '@mantine/hooks';
import { notifications } from '@mantine/notifications';
import { IconPlugConnected, IconPlus, IconTestPipe, IconTrash } from '@tabler/icons-react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api, ApiError } from '../api/client';
import { useActiveConnection } from '../state/ConnectionContext';

export function ConnectionsPage() {
  const queryClient = useQueryClient();
  const [opened, { open, close }] = useDisclosure(false);
  const { activeId, setActiveId } = useActiveConnection();

  const { data: connections, isLoading } = useQuery({
    queryKey: ['connections'],
    queryFn: api.listConnections,
  });

  const form = useForm({
    initialValues: {
      name: '',
      host: '',
      port: 9440,
      username: 'admin',
      secret: '',
      verify_ssl: false,
    },
    validate: {
      name: (v) => (v ? null : 'Required'),
      host: (v) => (v ? null : 'Required'),
      username: (v) => (v ? null : 'Required'),
      secret: (v) => (v ? null : 'Required'),
    },
  });

  const createMut = useMutation({
    mutationFn: api.createConnection,
    onSuccess: (created) => {
      queryClient.invalidateQueries({ queryKey: ['connections'] });
      setActiveId(created.id);
      notifications.show({ color: 'teal', message: `Connection "${created.name}" added` });
      form.reset();
      close();
    },
    onError: (e) =>
      notifications.show({
        color: 'red',
        message: e instanceof ApiError ? e.message : 'Failed to add connection',
      }),
  });

  const deleteMut = useMutation({
    mutationFn: api.deleteConnection,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['connections'] });
      notifications.show({ color: 'gray', message: 'Connection removed' });
    },
  });

  const testMut = useMutation({
    mutationFn: api.testConnection,
    onSuccess: (result) => {
      notifications.show({
        color: result.ok ? 'teal' : 'red',
        title: result.ok ? 'Connection successful' : 'Connection failed',
        message: result.ok
          ? `Prism Central ${result.prism_central_version} - ${result.cluster_count} cluster(s) [${result.mode}]`
          : result.message,
      });
    },
  });

  return (
    <Stack>
      <Group justify="space-between">
        <div>
          <Title order={2}>Prism Central</Title>
          <Text c="dimmed">Manage Nutanix Prism Central connections and API credentials.</Text>
        </div>
        <Button leftSection={<IconPlus size={16} />} onClick={open}>
          Add connection
        </Button>
      </Group>

      <Paper withBorder radius="md" p="md">
        <Table verticalSpacing="sm" highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Name</Table.Th>
              <Table.Th>Host</Table.Th>
              <Table.Th>Port</Table.Th>
              <Table.Th>Username</Table.Th>
              <Table.Th>SSL verify</Table.Th>
              <Table.Th ta="right">Actions</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {connections?.map((c) => (
              <Table.Tr key={c.id} bg={c.id === activeId ? 'nutanix.0' : undefined}>
                <Table.Td>
                  <Group gap="xs">
                    <IconPlugConnected size={16} />
                    <Text fw={600}>{c.name}</Text>
                  </Group>
                </Table.Td>
                <Table.Td>{c.host}</Table.Td>
                <Table.Td>{c.port}</Table.Td>
                <Table.Td>{c.username}</Table.Td>
                <Table.Td>{c.verify_ssl ? 'Yes' : 'No'}</Table.Td>
                <Table.Td>
                  <Group gap="xs" justify="flex-end">
                    <Tooltip label="Test connection">
                      <ActionIcon
                        variant="light"
                        color="nutanix"
                        loading={testMut.isPending && testMut.variables === c.id}
                        onClick={() => testMut.mutate(c.id)}
                        aria-label={`Test ${c.name}`}
                      >
                        <IconTestPipe size={16} />
                      </ActionIcon>
                    </Tooltip>
                    <Tooltip label="Delete">
                      <ActionIcon
                        variant="light"
                        color="red"
                        loading={deleteMut.isPending && deleteMut.variables === c.id}
                        onClick={() => deleteMut.mutate(c.id)}
                        aria-label={`Delete ${c.name}`}
                      >
                        <IconTrash size={16} />
                      </ActionIcon>
                    </Tooltip>
                  </Group>
                </Table.Td>
              </Table.Tr>
            ))}
            {!isLoading && (connections?.length ?? 0) === 0 && (
              <Table.Tr>
                <Table.Td colSpan={6}>
                  <Text c="dimmed" ta="center" py="md">
                    No connections yet. Add your first Prism Central connection.
                  </Text>
                </Table.Td>
              </Table.Tr>
            )}
          </Table.Tbody>
        </Table>
      </Paper>

      <Modal opened={opened} onClose={close} title="Add Prism Central connection" centered>
        <form onSubmit={form.onSubmit((v) => createMut.mutate(v))}>
          <Stack>
            <TextInput label="Name" placeholder="pc-prod" required {...form.getInputProps('name')} />
            <TextInput
              label="Host / IP"
              placeholder="10.10.0.5"
              required
              {...form.getInputProps('host')}
            />
            <NumberInput label="Port" min={1} max={65535} {...form.getInputProps('port')} />
            <TextInput label="Username" required {...form.getInputProps('username')} />
            <PasswordInput
              label="Password / API key"
              description="Stored encrypted at rest"
              required
              {...form.getInputProps('secret')}
            />
            <Checkbox label="Verify SSL certificate" {...form.getInputProps('verify_ssl', { type: 'checkbox' })} />
            <Group justify="flex-end" mt="sm">
              <Button variant="default" onClick={close}>
                Cancel
              </Button>
              <Button type="submit" loading={createMut.isPending}>
                Add connection
              </Button>
            </Group>
          </Stack>
        </form>
      </Modal>
    </Stack>
  );
}

import {
  Button,
  Group,
  Modal,
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
import { useDisclosure } from '@mantine/hooks';
import { notifications } from '@mantine/notifications';
import { IconServerBolt } from '@tabler/icons-react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api, ApiError } from '../api/client';
import { NoConnection } from '../components/NoConnection';
import { StateBadge } from '../components/StateBadge';
import { useActiveConnection } from '../state/ConnectionContext';

export function FilesPage() {
  const { activeId } = useActiveConnection();
  const queryClient = useQueryClient();
  const [opened, { open, close }] = useDisclosure(false);

  const { data: servers, isLoading } = useQuery({
    queryKey: ['files', activeId],
    queryFn: () => api.listFileServers(activeId!),
    enabled: !!activeId,
  });

  const { data: clusters } = useQuery({
    queryKey: ['clusters', activeId],
    queryFn: () => api.listClusters(activeId!),
    enabled: !!activeId,
  });

  const form = useForm({
    initialValues: { name: '', cluster_ext_id: '', size_gib: 1024 },
    validate: {
      name: (v) => (v ? null : 'Required'),
      cluster_ext_id: (v) => (v ? null : 'Select a cluster'),
    },
  });

  const createMut = useMutation({
    mutationFn: (values: { name: string; cluster_ext_id: string; size_gib: number }) =>
      api.createFileServer(activeId!, values),
    onSuccess: (fs) => {
      queryClient.invalidateQueries({ queryKey: ['files', activeId] });
      notifications.show({ color: 'teal', message: `Deploying file server "${fs.name}"` });
      form.reset();
      close();
    },
    onError: (e) =>
      notifications.show({
        color: 'red',
        message: e instanceof ApiError ? e.message : 'Failed to deploy file server',
      }),
  });

  if (!activeId) return <NoConnection />;

  return (
    <Stack>
      <Group justify="space-between">
        <div>
          <Title order={2}>Nutanix Files</Title>
          <Text c="dimmed">Deploy and manage Nutanix file servers.</Text>
        </div>
        <Button leftSection={<IconServerBolt size={16} />} onClick={open}>
          Deploy Files
        </Button>
      </Group>

      <Paper withBorder radius="md" p="md">
        <Table verticalSpacing="sm" highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Name</Table.Th>
              <Table.Th>Cluster</Table.Th>
              <Table.Th>Size (GiB)</Table.Th>
              <Table.Th>Version</Table.Th>
              <Table.Th>State</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {servers?.map((s) => (
              <Table.Tr key={s.ext_id}>
                <Table.Td>
                  <Text fw={600}>{s.name}</Text>
                </Table.Td>
                <Table.Td>{s.cluster_name}</Table.Td>
                <Table.Td>{s.size_gib.toLocaleString()}</Table.Td>
                <Table.Td>{s.version}</Table.Td>
                <Table.Td>
                  <StateBadge state={s.state} />
                </Table.Td>
              </Table.Tr>
            ))}
            {!isLoading && (servers?.length ?? 0) === 0 && (
              <Table.Tr>
                <Table.Td colSpan={5}>
                  <Text c="dimmed" ta="center" py="md">
                    No file servers yet.
                  </Text>
                </Table.Td>
              </Table.Tr>
            )}
          </Table.Tbody>
        </Table>
      </Paper>

      <Modal opened={opened} onClose={close} title="Deploy Nutanix Files" centered>
        <form onSubmit={form.onSubmit((v) => createMut.mutate(v))}>
          <Stack>
            <TextInput label="Name" placeholder="research-files" required {...form.getInputProps('name')} />
            <Select
              label="Cluster"
              placeholder="Select cluster"
              required
              data={(clusters ?? []).map((c) => ({ value: c.ext_id, label: `${c.name} (${c.hypervisor})` }))}
              {...form.getInputProps('cluster_ext_id')}
            />
            <NumberInput
              label="Size (GiB)"
              min={1024}
              step={1024}
              {...form.getInputProps('size_gib')}
            />
            <Group justify="flex-end" mt="sm">
              <Button variant="default" onClick={close}>
                Cancel
              </Button>
              <Button type="submit" loading={createMut.isPending}>
                Deploy
              </Button>
            </Group>
          </Stack>
        </form>
      </Modal>
    </Stack>
  );
}

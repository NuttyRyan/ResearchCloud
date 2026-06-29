import {
  Button,
  Code,
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
import { IconBox, IconBucket } from '@tabler/icons-react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { api, ApiError } from '../api/client';
import { BucketsDrawer } from '../components/BucketsDrawer';
import { NoConnection } from '../components/NoConnection';
import { StateBadge } from '../components/StateBadge';
import type { ObjectStore } from '../api/types';
import { useActiveConnection } from '../state/ConnectionContext';

export function ObjectsPage() {
  const { activeId } = useActiveConnection();
  const queryClient = useQueryClient();
  const [opened, { open, close }] = useDisclosure(false);
  const [bucketsFor, setBucketsFor] = useState<ObjectStore | null>(null);

  const { data: stores, isLoading } = useQuery({
    queryKey: ['objects', activeId],
    queryFn: () => api.listObjectStores(activeId!),
    enabled: !!activeId,
  });

  const { data: clusters } = useQuery({
    queryKey: ['clusters', activeId],
    queryFn: () => api.listClusters(activeId!),
    enabled: !!activeId,
  });

  const form = useForm({
    initialValues: { name: '', cluster_ext_id: '', capacity_gib: 2048 },
    validate: {
      name: (v) => (v ? null : 'Required'),
      cluster_ext_id: (v) => (v ? null : 'Select a cluster'),
    },
  });

  const createMut = useMutation({
    mutationFn: (values: { name: string; cluster_ext_id: string; capacity_gib: number }) =>
      api.createObjectStore(activeId!, values),
    onSuccess: (os) => {
      queryClient.invalidateQueries({ queryKey: ['objects', activeId] });
      notifications.show({ color: 'teal', message: `Deploying object store "${os.name}"` });
      form.reset();
      close();
    },
    onError: (e) =>
      notifications.show({
        color: 'red',
        message: e instanceof ApiError ? e.message : 'Failed to deploy object store',
      }),
  });

  if (!activeId) return <NoConnection />;

  return (
    <Stack>
      <Group justify="space-between">
        <div>
          <Title order={2}>Nutanix Objects</Title>
          <Text c="dimmed">Deploy and manage object storage clusters.</Text>
        </div>
        <Button leftSection={<IconBox size={16} />} onClick={open}>
          Deploy Objects
        </Button>
      </Group>

      <Paper withBorder radius="md" p="md">
        <Table verticalSpacing="sm" highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Name</Table.Th>
              <Table.Th>Cluster</Table.Th>
              <Table.Th>Capacity (GiB)</Table.Th>
              <Table.Th>Endpoint</Table.Th>
              <Table.Th>State</Table.Th>
              <Table.Th ta="right">Actions</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {stores?.map((s) => (
              <Table.Tr key={s.ext_id}>
                <Table.Td>
                  <Text fw={600}>{s.name}</Text>
                </Table.Td>
                <Table.Td>{s.cluster_name}</Table.Td>
                <Table.Td>{s.capacity_gib.toLocaleString()}</Table.Td>
                <Table.Td>
                  <Code>{s.endpoint}</Code>
                </Table.Td>
                <Table.Td>
                  <StateBadge state={s.state} />
                </Table.Td>
                <Table.Td>
                  <Group justify="flex-end">
                    <Button
                      size="xs"
                      variant="light"
                      leftSection={<IconBucket size={14} />}
                      onClick={() => setBucketsFor(s)}
                    >
                      Buckets
                    </Button>
                  </Group>
                </Table.Td>
              </Table.Tr>
            ))}
            {!isLoading && (stores?.length ?? 0) === 0 && (
              <Table.Tr>
                <Table.Td colSpan={6}>
                  <Text c="dimmed" ta="center" py="md">
                    No object stores yet.
                  </Text>
                </Table.Td>
              </Table.Tr>
            )}
          </Table.Tbody>
        </Table>
      </Paper>

      <Modal opened={opened} onClose={close} title="Deploy Nutanix Objects" centered>
        <form onSubmit={form.onSubmit((v) => createMut.mutate(v))}>
          <Stack>
            <TextInput label="Name" placeholder="research-objects" required {...form.getInputProps('name')} />
            <Select
              label="Cluster"
              placeholder="Select cluster"
              required
              data={(clusters ?? []).map((c) => ({ value: c.ext_id, label: `${c.name} (${c.hypervisor})` }))}
              {...form.getInputProps('cluster_ext_id')}
            />
            <NumberInput
              label="Capacity (GiB)"
              min={1024}
              step={1024}
              {...form.getInputProps('capacity_gib')}
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

      {activeId && (
        <BucketsDrawer
          connectionId={activeId}
          objectStore={bucketsFor}
          onClose={() => setBucketsFor(null)}
        />
      )}
    </Stack>
  );
}

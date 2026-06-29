import {
  Button,
  Checkbox,
  Divider,
  Drawer,
  NumberInput,
  Paper,
  Stack,
  Table,
  Text,
  TextInput,
  Title,
} from '@mantine/core';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api, ApiError } from '../api/client';
import type { ObjectStore } from '../api/types';
import { StateBadge } from './StateBadge';

export function BucketsDrawer({
  connectionId,
  objectStore,
  onClose,
}: {
  connectionId: number;
  objectStore: ObjectStore | null;
  onClose: () => void;
}) {
  const queryClient = useQueryClient();
  const opened = objectStore !== null;
  const osExtId = objectStore?.ext_id ?? '';

  const { data: buckets } = useQuery({
    queryKey: ['buckets', connectionId, osExtId],
    queryFn: () => api.listBuckets(connectionId, osExtId),
    enabled: opened,
  });

  const form = useForm({
    initialValues: { name: '', versioning: false, size_gib: 100 },
    validate: { name: (v) => (v ? null : 'Required') },
  });

  const createMut = useMutation({
    mutationFn: (values: { name: string; versioning: boolean; size_gib: number }) =>
      api.createBucket(connectionId, osExtId, values),
    onSuccess: (bucket) => {
      queryClient.invalidateQueries({ queryKey: ['buckets', connectionId, osExtId] });
      notifications.show({ color: 'teal', message: `Bucket "${bucket.name}" created` });
      form.reset();
    },
    onError: (e) =>
      notifications.show({
        color: 'red',
        message: e instanceof ApiError ? e.message : 'Failed to create bucket',
      }),
  });

  return (
    <Drawer
      opened={opened}
      onClose={onClose}
      position="right"
      size="lg"
      title={<Title order={4}>Buckets - {objectStore?.name}</Title>}
    >
      <Stack>
        <Paper withBorder radius="md" p="md">
          <Table verticalSpacing="sm">
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Name</Table.Th>
                <Table.Th>Versioning</Table.Th>
                <Table.Th>Quota (GiB)</Table.Th>
                <Table.Th>State</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {buckets?.map((b) => (
                <Table.Tr key={b.ext_id}>
                  <Table.Td>
                    <Text fw={600}>{b.name}</Text>
                  </Table.Td>
                  <Table.Td>{b.versioning ? 'Enabled' : 'Disabled'}</Table.Td>
                  <Table.Td>{b.size_gib.toLocaleString()}</Table.Td>
                  <Table.Td>
                    <StateBadge state={b.state} />
                  </Table.Td>
                </Table.Tr>
              ))}
              {(buckets?.length ?? 0) === 0 && (
                <Table.Tr>
                  <Table.Td colSpan={4}>
                    <Text c="dimmed" ta="center" py="sm">
                      No buckets yet.
                    </Text>
                  </Table.Td>
                </Table.Tr>
              )}
            </Table.Tbody>
          </Table>
        </Paper>

        <Divider label="Create bucket" labelPosition="center" />

        <form onSubmit={form.onSubmit((v) => createMut.mutate(v))}>
          <Stack>
            <TextInput label="Name" placeholder="raw-data" required {...form.getInputProps('name')} />
            <NumberInput label="Quota (GiB)" min={1} {...form.getInputProps('size_gib')} />
            <Checkbox
              label="Enable versioning"
              {...form.getInputProps('versioning', { type: 'checkbox' })}
            />
            <Button type="submit" loading={createMut.isPending}>
              Create bucket
            </Button>
          </Stack>
        </form>
      </Stack>
    </Drawer>
  );
}

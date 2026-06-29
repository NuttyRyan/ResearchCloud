import {
  Button,
  Group,
  Modal,
  Paper,
  Stack,
  Table,
  Text,
  Textarea,
  TextInput,
  Title,
} from '@mantine/core';
import { useForm } from '@mantine/form';
import { useDisclosure } from '@mantine/hooks';
import { notifications } from '@mantine/notifications';
import { IconPlus } from '@tabler/icons-react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api, ApiError } from '../api/client';
import { NoConnection } from '../components/NoConnection';
import { StateBadge } from '../components/StateBadge';
import { useActiveConnection } from '../state/ConnectionContext';

export function ProjectsPage() {
  const { activeId } = useActiveConnection();
  const queryClient = useQueryClient();
  const [opened, { open, close }] = useDisclosure(false);

  const { data: projects, isLoading } = useQuery({
    queryKey: ['projects', activeId],
    queryFn: () => api.listProjects(activeId!),
    enabled: !!activeId,
  });

  const form = useForm({
    initialValues: { name: '', description: '' },
    validate: { name: (v) => (v ? null : 'Required') },
  });

  const createMut = useMutation({
    mutationFn: (values: { name: string; description: string }) =>
      api.createProject(activeId!, values),
    onSuccess: (project) => {
      queryClient.invalidateQueries({ queryKey: ['projects', activeId] });
      notifications.show({ color: 'teal', message: `Project "${project.name}" created` });
      form.reset();
      close();
    },
    onError: (e) =>
      notifications.show({
        color: 'red',
        message: e instanceof ApiError ? e.message : 'Failed to create project',
      }),
  });

  if (!activeId) return <NoConnection />;

  return (
    <Stack>
      <Group justify="space-between">
        <div>
          <Title order={2}>Projects</Title>
          <Text c="dimmed">Create and manage Nutanix projects.</Text>
        </div>
        <Button leftSection={<IconPlus size={16} />} onClick={open}>
          Create project
        </Button>
      </Group>

      <Paper withBorder radius="md" p="md">
        <Table verticalSpacing="sm" highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Name</Table.Th>
              <Table.Th>Description</Table.Th>
              <Table.Th>VMs</Table.Th>
              <Table.Th>State</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {projects?.map((p) => (
              <Table.Tr key={p.ext_id}>
                <Table.Td>
                  <Text fw={600}>{p.name}</Text>
                </Table.Td>
                <Table.Td>{p.description || <Text c="dimmed">-</Text>}</Table.Td>
                <Table.Td>{p.vm_count}</Table.Td>
                <Table.Td>
                  <StateBadge state={p.state} />
                </Table.Td>
              </Table.Tr>
            ))}
            {!isLoading && (projects?.length ?? 0) === 0 && (
              <Table.Tr>
                <Table.Td colSpan={4}>
                  <Text c="dimmed" ta="center" py="md">
                    No projects yet.
                  </Text>
                </Table.Td>
              </Table.Tr>
            )}
          </Table.Tbody>
        </Table>
      </Paper>

      <Modal opened={opened} onClose={close} title="Create project" centered>
        <form onSubmit={form.onSubmit((v) => createMut.mutate(v))}>
          <Stack>
            <TextInput label="Name" placeholder="genomics" required {...form.getInputProps('name')} />
            <Textarea
              label="Description"
              placeholder="Research project for the genomics team"
              {...form.getInputProps('description')}
            />
            <Group justify="flex-end" mt="sm">
              <Button variant="default" onClick={close}>
                Cancel
              </Button>
              <Button type="submit" loading={createMut.isPending}>
                Create
              </Button>
            </Group>
          </Stack>
        </form>
      </Modal>
    </Stack>
  );
}

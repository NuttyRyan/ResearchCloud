import {
  ActionIcon,
  Badge,
  Button,
  Code,
  CopyButton,
  Drawer,
  Group,
  Modal,
  Paper,
  ScrollArea,
  Select,
  Stack,
  Table,
  Text,
  Textarea,
  TextInput,
  Title,
  Tooltip,
} from '@mantine/core';
import { useForm } from '@mantine/form';
import { useDisclosure } from '@mantine/hooks';
import { notifications } from '@mantine/notifications';
import {
  IconClipboardCheck,
  IconCopy,
  IconEye,
  IconPlus,
  IconTrash,
} from '@tabler/icons-react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { api, ApiError } from '../api/client';
import type { Runbook } from '../api/types';

const OS_OPTIONS = ['Ubuntu 22.04', 'Rocky Linux 9', 'Windows Server 2022', 'CentOS 7'];

export function RunbooksPage() {
  const queryClient = useQueryClient();
  const [opened, { open, close }] = useDisclosure(false);
  const [viewing, setViewing] = useState<Runbook | null>(null);

  const { data: runbooks, isLoading } = useQuery({
    queryKey: ['runbooks'],
    queryFn: api.listRunbooks,
  });

  const form = useForm({
    initialValues: { name: '', description: '', os: 'Ubuntu 22.04', script: '' },
    validate: {
      name: (v) => (v ? null : 'Required'),
      script: (v) => (v ? null : 'Required'),
    },
  });

  const createMut = useMutation({
    mutationFn: (values: typeof form.values) => api.createRunbook(values),
    onSuccess: (rb) => {
      queryClient.invalidateQueries({ queryKey: ['runbooks'] });
      notifications.show({ color: 'teal', message: `Runbook "${rb.name}" created` });
      form.reset();
      close();
    },
    onError: (e) =>
      notifications.show({
        color: 'red',
        message: e instanceof ApiError ? e.message : 'Failed to create runbook',
      }),
  });

  const deleteMut = useMutation({
    mutationFn: api.deleteRunbook,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['runbooks'] });
      notifications.show({ color: 'gray', message: 'Runbook deleted' });
    },
  });

  return (
    <Stack>
      <Group justify="space-between">
        <div>
          <Title order={2}>Runbooks</Title>
          <Text c="dimmed">
            Repeatable, selectable automation scripts - generated from blueprints or authored
            directly.
          </Text>
        </div>
        <Button leftSection={<IconPlus size={16} />} onClick={open}>
          Create runbook
        </Button>
      </Group>

      <Paper withBorder radius="md" p="md">
        <Table verticalSpacing="sm" highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Name</Table.Th>
              <Table.Th>OS</Table.Th>
              <Table.Th>Source</Table.Th>
              <Table.Th ta="right">Actions</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {runbooks?.map((r) => (
              <Table.Tr key={r.id}>
                <Table.Td>
                  <Text fw={600}>{r.name}</Text>
                  {r.description && (
                    <Text size="xs" c="dimmed">
                      {r.description}
                    </Text>
                  )}
                </Table.Td>
                <Table.Td>{r.os}</Table.Td>
                <Table.Td>
                  {r.source_blueprint_id ? (
                    <Badge variant="light" color="nutanix" radius="sm">
                      blueprint
                    </Badge>
                  ) : (
                    <Badge variant="light" color="gray" radius="sm">
                      authored
                    </Badge>
                  )}
                </Table.Td>
                <Table.Td>
                  <Group gap="xs" justify="flex-end">
                    <Tooltip label="View script">
                      <ActionIcon variant="light" onClick={() => setViewing(r)} aria-label={`View ${r.name}`}>
                        <IconEye size={16} />
                      </ActionIcon>
                    </Tooltip>
                    <Tooltip label="Delete">
                      <ActionIcon
                        variant="light"
                        color="red"
                        loading={deleteMut.isPending && deleteMut.variables === r.id}
                        onClick={() => deleteMut.mutate(r.id)}
                        aria-label={`Delete ${r.name}`}
                      >
                        <IconTrash size={16} />
                      </ActionIcon>
                    </Tooltip>
                  </Group>
                </Table.Td>
              </Table.Tr>
            ))}
            {!isLoading && (runbooks?.length ?? 0) === 0 && (
              <Table.Tr>
                <Table.Td colSpan={4}>
                  <Text c="dimmed" ta="center" py="md">
                    No runbooks yet. Create one here or from a blueprint.
                  </Text>
                </Table.Td>
              </Table.Tr>
            )}
          </Table.Tbody>
        </Table>
      </Paper>

      <Modal opened={opened} onClose={close} title="Create runbook" size="lg" centered>
        <form onSubmit={form.onSubmit((v) => createMut.mutate(v))}>
          <Stack>
            <TextInput label="Name" placeholder="patch-baseline" required {...form.getInputProps('name')} />
            <TextInput label="Description" {...form.getInputProps('description')} />
            <Select label="Operating system" data={OS_OPTIONS} {...form.getInputProps('os')} />
            <Textarea
              label="Script"
              placeholder="#!/usr/bin/env bash&#10;apt-get update -y"
              autosize
              minRows={6}
              required
              {...form.getInputProps('script')}
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

      <Drawer
        opened={viewing !== null}
        onClose={() => setViewing(null)}
        position="right"
        size="lg"
        title={<Title order={4}>{viewing?.name ?? 'Runbook'}</Title>}
      >
        {viewing && (
          <Stack>
            <Text c="dimmed" size="sm">
              {viewing.os}
              {viewing.description ? ` - ${viewing.description}` : ''}
            </Text>
            <Group justify="flex-end">
              <CopyButton value={viewing.script}>
                {({ copied, copy }) => (
                  <Button
                    size="xs"
                    variant="light"
                    color={copied ? 'teal' : 'nutanix'}
                    leftSection={copied ? <IconClipboardCheck size={14} /> : <IconCopy size={14} />}
                    onClick={copy}
                  >
                    {copied ? 'Copied' : 'Copy'}
                  </Button>
                )}
              </CopyButton>
            </Group>
            <ScrollArea h={500} type="auto">
              <Code block style={{ whiteSpace: 'pre' }}>
                {viewing.script}
              </Code>
            </ScrollArea>
          </Stack>
        )}
      </Drawer>
    </Stack>
  );
}

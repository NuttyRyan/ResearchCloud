import {
  ActionIcon,
  Button,
  Code,
  CopyButton,
  Divider,
  Drawer,
  Group,
  Modal,
  NumberInput,
  Paper,
  ScrollArea,
  Select,
  Stack,
  Table,
  Tabs,
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
import { useEffect, useState } from 'react';
import { api, ApiError } from '../api/client';
import type { AppSpec } from '../api/types';

const OS_OPTIONS = ['Ubuntu 22.04', 'Rocky Linux 9', 'Windows Server 2022', 'CentOS 7'];

function CopyBlock({ code, label }: { code: string; label: string }) {
  return (
    <Stack gap="xs">
      <Group justify="space-between">
        <Text size="sm" fw={600}>
          {label}
        </Text>
        <CopyButton value={code}>
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
      <ScrollArea h={360} type="auto">
        <Code block style={{ whiteSpace: 'pre' }}>
          {code}
        </Code>
      </ScrollArea>
    </Stack>
  );
}

export function BlueprintsPage() {
  const queryClient = useQueryClient();
  const [opened, { open, close }] = useDisclosure(false);
  const [detailId, setDetailId] = useState<number | null>(null);
  const [apps, setApps] = useState<AppSpec[]>([]);
  const [runbookName, setRunbookName] = useState('');

  const { data: blueprints, isLoading } = useQuery({
    queryKey: ['blueprints'],
    queryFn: api.listBlueprints,
  });

  const { data: detail } = useQuery({
    queryKey: ['blueprint', detailId],
    queryFn: () => api.getBlueprint(detailId!),
    enabled: detailId !== null,
  });

  // Pre-fill a sensible runbook name when a blueprint's detail loads.
  useEffect(() => {
    if (detail) setRunbookName(`${detail.name}-setup`);
  }, [detail]);

  const form = useForm({
    initialValues: {
      name: '',
      description: '',
      os: 'Ubuntu 22.04',
      num_vcpus: 2,
      memory_gib: 8,
    },
    validate: { name: (v) => (v ? null : 'Required') },
  });

  const createMut = useMutation({
    mutationFn: (values: typeof form.values) =>
      api.createBlueprint({ ...values, apps }),
    onSuccess: (bp) => {
      queryClient.invalidateQueries({ queryKey: ['blueprints'] });
      notifications.show({ color: 'teal', message: `Blueprint "${bp.name}" created` });
      form.reset();
      setApps([]);
      close();
      setDetailId(bp.id);
    },
    onError: (e) =>
      notifications.show({
        color: 'red',
        message: e instanceof ApiError ? e.message : 'Failed to create blueprint',
      }),
  });

  const deleteMut = useMutation({
    mutationFn: api.deleteBlueprint,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['blueprints'] });
      notifications.show({ color: 'gray', message: 'Blueprint deleted' });
    },
  });

  const runbookMut = useMutation({
    mutationFn: ({ id, name }: { id: number; name: string }) =>
      api.createRunbookFromBlueprint(id, { name, description: '' }),
    onSuccess: (rb) => {
      queryClient.invalidateQueries({ queryKey: ['runbooks'] });
      notifications.show({ color: 'teal', message: `Runbook "${rb.name}" created` });
      setRunbookName('');
    },
    onError: (e) =>
      notifications.show({
        color: 'red',
        message: e instanceof ApiError ? e.message : 'Failed to create runbook',
      }),
  });

  const addApp = () =>
    setApps((a) => [...a, { name: '', method: 'URL', url: '', script: '' }]);
  const updateApp = (i: number, patch: Partial<AppSpec>) =>
    setApps((a) => a.map((app, j) => (j === i ? { ...app, ...patch } : app)));
  const removeApp = (i: number) => setApps((a) => a.filter((_, j) => j !== i));

  return (
    <Stack>
      <Group justify="space-between">
        <div>
          <Title order={2}>Blueprints</Title>
          <Text c="dimmed">
            Build Self-Service blueprints - pick an OS and applications, and generate an
            install script and Calm DSL.
          </Text>
        </div>
        <Button leftSection={<IconPlus size={16} />} onClick={open}>
          Build blueprint
        </Button>
      </Group>

      <Paper withBorder radius="md" p="md">
        <Table verticalSpacing="sm" highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Name</Table.Th>
              <Table.Th>OS</Table.Th>
              <Table.Th>Size</Table.Th>
              <Table.Th>Apps</Table.Th>
              <Table.Th ta="right">Actions</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {blueprints?.map((b) => (
              <Table.Tr key={b.id}>
                <Table.Td>
                  <Text fw={600}>{b.name}</Text>
                  {b.description && (
                    <Text size="xs" c="dimmed">
                      {b.description}
                    </Text>
                  )}
                </Table.Td>
                <Table.Td>{b.os}</Table.Td>
                <Table.Td>
                  {b.num_vcpus} vCPU / {b.memory_gib} GiB
                </Table.Td>
                <Table.Td>{b.apps.length}</Table.Td>
                <Table.Td>
                  <Group gap="xs" justify="flex-end">
                    <Tooltip label="View generated script & DSL">
                      <ActionIcon variant="light" onClick={() => setDetailId(b.id)} aria-label={`View ${b.name}`}>
                        <IconEye size={16} />
                      </ActionIcon>
                    </Tooltip>
                    <Tooltip label="Delete">
                      <ActionIcon
                        variant="light"
                        color="red"
                        loading={deleteMut.isPending && deleteMut.variables === b.id}
                        onClick={() => deleteMut.mutate(b.id)}
                        aria-label={`Delete ${b.name}`}
                      >
                        <IconTrash size={16} />
                      </ActionIcon>
                    </Tooltip>
                  </Group>
                </Table.Td>
              </Table.Tr>
            ))}
            {!isLoading && (blueprints?.length ?? 0) === 0 && (
              <Table.Tr>
                <Table.Td colSpan={5}>
                  <Text c="dimmed" ta="center" py="md">
                    No blueprints yet. Build your first one.
                  </Text>
                </Table.Td>
              </Table.Tr>
            )}
          </Table.Tbody>
        </Table>
      </Paper>

      <Modal opened={opened} onClose={close} title="Build blueprint" size="lg" centered>
        <form onSubmit={form.onSubmit((v) => createMut.mutate(v))}>
          <Stack>
            <TextInput label="Name" placeholder="data-science-workstation" required {...form.getInputProps('name')} />
            <TextInput label="Description" {...form.getInputProps('description')} />
            <Group grow>
              <Select label="Operating system" data={OS_OPTIONS} {...form.getInputProps('os')} />
              <NumberInput label="vCPUs" min={1} max={128} {...form.getInputProps('num_vcpus')} />
              <NumberInput label="Memory (GiB)" min={1} max={1024} {...form.getInputProps('memory_gib')} />
            </Group>

            <Divider label="Applications" labelPosition="center" />
            {apps.map((app, i) => (
              <Paper key={i} withBorder radius="sm" p="sm">
                <Stack gap="xs">
                  <Group gap="xs" align="flex-end">
                    <TextInput
                      label="App name"
                      placeholder="docker"
                      value={app.name}
                      onChange={(e) => updateApp(i, { name: e.currentTarget.value })}
                      style={{ flex: 1 }}
                    />
                    <Select
                      label="Install via"
                      w={150}
                      data={[
                        { value: 'URL', label: 'URL (download & run)' },
                        { value: 'INLINE', label: 'Inline script' },
                      ]}
                      value={app.method}
                      onChange={(v) => updateApp(i, { method: (v as AppSpec['method']) ?? 'URL' })}
                    />
                    <ActionIcon
                      variant="light"
                      color="red"
                      onClick={() => removeApp(i)}
                      aria-label={`Remove app ${i + 1}`}
                      mb={4}
                    >
                      <IconTrash size={16} />
                    </ActionIcon>
                  </Group>
                  {app.method === 'URL' ? (
                    <TextInput
                      label="Installer URL"
                      placeholder="https://get.docker.com"
                      value={app.url}
                      onChange={(e) => updateApp(i, { url: e.currentTarget.value })}
                    />
                  ) : (
                    <Textarea
                      label="Inline script"
                      placeholder="apt-get install -y nginx"
                      autosize
                      minRows={2}
                      value={app.script}
                      onChange={(e) => updateApp(i, { script: e.currentTarget.value })}
                    />
                  )}
                </Stack>
              </Paper>
            ))}
            <Button variant="light" leftSection={<IconPlus size={14} />} onClick={addApp}>
              Add application
            </Button>

            <Group justify="flex-end" mt="sm">
              <Button variant="default" onClick={close}>
                Cancel
              </Button>
              <Button type="submit" loading={createMut.isPending}>
                Build
              </Button>
            </Group>
          </Stack>
        </form>
      </Modal>

      <Drawer
        opened={detailId !== null}
        onClose={() => setDetailId(null)}
        position="right"
        size="xl"
        title={<Title order={4}>{detail?.name ?? 'Blueprint'}</Title>}
      >
        {detail && (
          <Stack>
            <Text c="dimmed" size="sm">
              {detail.os} - {detail.num_vcpus} vCPU / {detail.memory_gib} GiB -{' '}
              {detail.apps.length} app(s) - platform {detail.platform}
            </Text>
            <Tabs defaultValue="script">
              <Tabs.List>
                <Tabs.Tab value="script">Install script</Tabs.Tab>
                <Tabs.Tab value="dsl">Calm DSL</Tabs.Tab>
              </Tabs.List>
              <Tabs.Panel value="script" pt="sm">
                <CopyBlock
                  code={detail.install_script}
                  label={detail.platform === 'windows' ? 'PowerShell' : 'Bash'}
                />
              </Tabs.Panel>
              <Tabs.Panel value="dsl" pt="sm">
                <CopyBlock code={detail.calm_dsl} label="Calm DSL (Python)" />
              </Tabs.Panel>
            </Tabs>

            <Divider label="Create runbook from this blueprint" labelPosition="center" />
            <Group align="flex-end">
              <TextInput
                label="Runbook name"
                placeholder={`${detail.name}-setup`}
                value={runbookName}
                onChange={(e) => setRunbookName(e.currentTarget.value)}
                style={{ flex: 1 }}
              />
              <Button
                loading={runbookMut.isPending}
                disabled={!runbookName.trim()}
                onClick={() => runbookMut.mutate({ id: detail.id, name: runbookName.trim() })}
              >
                Create runbook
              </Button>
            </Group>
          </Stack>
        )}
      </Drawer>
    </Stack>
  );
}

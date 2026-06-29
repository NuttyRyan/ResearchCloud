import {
  ActionIcon,
  Badge,
  Button,
  Group,
  Modal,
  Select,
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
import {
  IconPlayerPlay,
  IconPlayerStop,
  IconPlus,
  IconRefresh,
  IconTrash,
} from '@tabler/icons-react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { api, ApiError } from '../api/client';
import { NoConnection } from '../components/NoConnection';
import type { VmPowerActionType } from '../api/types';
import { useActiveConnection } from '../state/ConnectionContext';

const PRESETS: Record<string, { num_vcpus: number; memory_gib: number; label: string }> = {
  small: { num_vcpus: 2, memory_gib: 4, label: 'Small - 2 vCPU / 4 GiB' },
  medium: { num_vcpus: 4, memory_gib: 16, label: 'Medium - 4 vCPU / 16 GiB' },
  large: { num_vcpus: 8, memory_gib: 32, label: 'Large - 8 vCPU / 32 GiB' },
  gpu: { num_vcpus: 16, memory_gib: 64, label: 'GPU - 16 vCPU / 64 GiB' },
};

const OS_OPTIONS = ['Ubuntu 22.04', 'Rocky Linux 9', 'Windows Server 2022', 'CentOS 7'];

export function VmsPage() {
  const { activeId } = useActiveConnection();
  const queryClient = useQueryClient();
  const [opened, { open, close }] = useDisclosure(false);
  const [projectFilter, setProjectFilter] = useState<string | null>(null);

  const vmsKey = ['vms', activeId, projectFilter];
  const { data: vms, isLoading } = useQuery({
    queryKey: vmsKey,
    queryFn: () => api.listVms(activeId!, projectFilter ?? undefined),
    enabled: !!activeId,
  });

  const { data: clusters } = useQuery({
    queryKey: ['clusters', activeId],
    queryFn: () => api.listClusters(activeId!),
    enabled: !!activeId,
  });
  const { data: projects } = useQuery({
    queryKey: ['projects', activeId],
    queryFn: () => api.listProjects(activeId!),
    enabled: !!activeId,
  });

  const form = useForm({
    initialValues: {
      name: '',
      project_ext_id: '',
      cluster_ext_id: '',
      size: 'medium',
      os: 'Ubuntu 22.04',
    },
    validate: {
      name: (v) => (v ? null : 'Required'),
      project_ext_id: (v) => (v ? null : 'Select a project'),
      cluster_ext_id: (v) => (v ? null : 'Select a cluster'),
    },
  });

  const invalidate = () =>
    queryClient.invalidateQueries({ queryKey: ['vms', activeId] });

  const createMut = useMutation({
    mutationFn: (values: typeof form.values) => {
      const preset = PRESETS[values.size];
      return api.createVm(activeId!, {
        name: values.name,
        project_ext_id: values.project_ext_id,
        cluster_ext_id: values.cluster_ext_id,
        num_vcpus: preset.num_vcpus,
        memory_gib: preset.memory_gib,
        os: values.os,
      });
    },
    onSuccess: (vm) => {
      invalidate();
      notifications.show({ color: 'teal', message: `VM "${vm.name}" created` });
      form.reset();
      close();
    },
    onError: (e) =>
      notifications.show({
        color: 'red',
        message: e instanceof ApiError ? e.message : 'Failed to create VM',
      }),
  });

  const powerMut = useMutation({
    mutationFn: ({ extId, action }: { extId: string; action: VmPowerActionType }) =>
      api.setVmPower(activeId!, extId, action),
    onSuccess: (vm) => {
      invalidate();
      notifications.show({ color: 'teal', message: `${vm.name} is now ${vm.power_state}` });
    },
    onError: (e) =>
      notifications.show({
        color: 'red',
        message: e instanceof ApiError ? e.message : 'Power action failed',
      }),
  });

  const deleteMut = useMutation({
    mutationFn: (extId: string) => api.deleteVm(activeId!, extId),
    onSuccess: () => {
      invalidate();
      notifications.show({ color: 'gray', message: 'VM deleted' });
    },
  });

  if (!activeId) return <NoConnection />;

  return (
    <Stack>
      <Group justify="space-between">
        <div>
          <Title order={2}>Virtual Machines</Title>
          <Text c="dimmed">Self-service VM management across your projects.</Text>
        </div>
        <Group>
          <Select
            placeholder="All projects"
            clearable
            w={220}
            data={(projects ?? []).map((p) => ({ value: p.ext_id, label: p.name }))}
            value={projectFilter}
            onChange={setProjectFilter}
            aria-label="Filter by project"
          />
          <Button leftSection={<IconPlus size={16} />} onClick={open}>
            Create VM
          </Button>
        </Group>
      </Group>

      <Table.ScrollContainer minWidth={760}>
        <Table verticalSpacing="sm" highlightOnHover withTableBorder>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Name</Table.Th>
              <Table.Th>Project</Table.Th>
              <Table.Th>Cluster</Table.Th>
              <Table.Th>Size</Table.Th>
              <Table.Th>OS</Table.Th>
              <Table.Th>IP</Table.Th>
              <Table.Th>Power</Table.Th>
              <Table.Th ta="right">Actions</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {vms?.map((vm) => {
              const busy = powerMut.isPending && powerMut.variables?.extId === vm.ext_id;
              return (
                <Table.Tr key={vm.ext_id}>
                  <Table.Td>
                    <Text fw={600}>{vm.name}</Text>
                  </Table.Td>
                  <Table.Td>{vm.project_name}</Table.Td>
                  <Table.Td>{vm.cluster_name}</Table.Td>
                  <Table.Td>
                    {vm.num_vcpus} vCPU / {vm.memory_gib} GiB
                  </Table.Td>
                  <Table.Td>{vm.os}</Table.Td>
                  <Table.Td>{vm.ip_address ?? <Text c="dimmed">-</Text>}</Table.Td>
                  <Table.Td>
                    <Badge
                      color={vm.power_state === 'ON' ? 'teal' : 'gray'}
                      variant="light"
                      radius="sm"
                    >
                      {vm.power_state}
                    </Badge>
                  </Table.Td>
                  <Table.Td>
                    <Group gap="xs" justify="flex-end">
                      {vm.power_state === 'OFF' ? (
                        <Tooltip label="Power on">
                          <ActionIcon
                            variant="light"
                            color="teal"
                            loading={busy}
                            onClick={() =>
                              powerMut.mutate({ extId: vm.ext_id, action: 'ON' })
                            }
                            aria-label={`Power on ${vm.name}`}
                          >
                            <IconPlayerPlay size={16} />
                          </ActionIcon>
                        </Tooltip>
                      ) : (
                        <Tooltip label="Power off">
                          <ActionIcon
                            variant="light"
                            color="orange"
                            loading={busy}
                            onClick={() =>
                              powerMut.mutate({ extId: vm.ext_id, action: 'OFF' })
                            }
                            aria-label={`Power off ${vm.name}`}
                          >
                            <IconPlayerStop size={16} />
                          </ActionIcon>
                        </Tooltip>
                      )}
                      <Tooltip label="Restart">
                        <ActionIcon
                          variant="light"
                          color="nutanix"
                          loading={busy}
                          onClick={() =>
                            powerMut.mutate({ extId: vm.ext_id, action: 'RESTART' })
                          }
                          aria-label={`Restart ${vm.name}`}
                        >
                          <IconRefresh size={16} />
                        </ActionIcon>
                      </Tooltip>
                      <Tooltip label="Delete">
                        <ActionIcon
                          variant="light"
                          color="red"
                          loading={deleteMut.isPending && deleteMut.variables === vm.ext_id}
                          onClick={() => deleteMut.mutate(vm.ext_id)}
                          aria-label={`Delete ${vm.name}`}
                        >
                          <IconTrash size={16} />
                        </ActionIcon>
                      </Tooltip>
                    </Group>
                  </Table.Td>
                </Table.Tr>
              );
            })}
            {!isLoading && (vms?.length ?? 0) === 0 && (
              <Table.Tr>
                <Table.Td colSpan={8}>
                  <Text c="dimmed" ta="center" py="md">
                    No VMs yet.
                  </Text>
                </Table.Td>
              </Table.Tr>
            )}
          </Table.Tbody>
        </Table>
      </Table.ScrollContainer>

      <Modal opened={opened} onClose={close} title="Create virtual machine" centered>
        <form onSubmit={form.onSubmit((v) => createMut.mutate(v))}>
          <Stack>
            <TextInput label="Name" placeholder="analysis-01" required {...form.getInputProps('name')} />
            <Select
              label="Project"
              placeholder="Select project"
              required
              data={(projects ?? []).map((p) => ({ value: p.ext_id, label: p.name }))}
              {...form.getInputProps('project_ext_id')}
            />
            <Select
              label="Cluster"
              placeholder="Select cluster"
              required
              data={(clusters ?? []).map((c) => ({ value: c.ext_id, label: `${c.name} (${c.hypervisor})` }))}
              {...form.getInputProps('cluster_ext_id')}
            />
            <Select
              label="Size"
              data={Object.entries(PRESETS).map(([value, p]) => ({ value, label: p.label }))}
              {...form.getInputProps('size')}
            />
            <Select label="Operating system" data={OS_OPTIONS} {...form.getInputProps('os')} />
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

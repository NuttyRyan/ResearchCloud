import {
  Badge,
  Card,
  Grid,
  Group,
  List,
  Paper,
  Progress,
  SimpleGrid,
  Stack,
  Text,
  ThemeIcon,
  Title,
} from '@mantine/core';
import {
  IconBox,
  IconBuildingBank,
  IconCircleCheck,
  IconCircleDashed,
  IconDeviceDesktop,
  IconFolders,
  IconReportMoney,
  IconServer2,
} from '@tabler/icons-react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import type { ResourceUsage } from '../api/types';
import { NoConnection } from '../components/NoConnection';
import { useActiveConnection } from '../state/ConnectionContext';

function UsageBar({ label, usage }: { label: string; usage: ResourceUsage }) {
  const pct = usage.limit > 0 ? Math.min(100, (usage.used / usage.limit) * 100) : 0;
  const color = pct >= 90 ? 'red' : pct >= 75 ? 'orange' : 'nutanix';
  return (
    <div>
      <Group justify="space-between" mb={2}>
        <Text size="xs" c="dimmed">
          {label}
        </Text>
        <Text size="xs">
          {usage.used.toLocaleString()} / {usage.limit.toLocaleString()} {usage.unit} (
          {Math.round(pct)}%)
        </Text>
      </Group>
      <Progress value={pct} color={color} radius="sm" />
    </div>
  );
}

function StatCard({
  label,
  value,
  icon: Icon,
}: {
  label: string;
  value: number | string;
  icon: typeof IconFolders;
}) {
  return (
    <Card withBorder radius="md" padding="lg">
      <Group justify="space-between">
        <Stack gap={0}>
          <Text c="dimmed" size="sm" fw={600} tt="uppercase">
            {label}
          </Text>
          <Text fw={700} fz={32}>
            {value}
          </Text>
        </Stack>
        <ThemeIcon size={48} radius="md" variant="light" color="nutanix">
          <Icon size={26} />
        </ThemeIcon>
      </Group>
    </Card>
  );
}

const DELIVERED = [
  'Prism Central connection management',
  'Projects (create & manage)',
  'Deploy Nutanix Files & Objects',
  'File shares (with permissions) & object buckets',
  'VM management: create, power on/off/restart, delete',
  'Self-Service blueprint builder & runbooks (Calm DSL)',
];

const ROADMAP = [
  'VNC console for project VMs',
  'Active Directory user & group management',
  'Flow microsegmentation management',
  'Admin & end-user (self-service) access modes',
  'Smart scheduling & idle auto-stop for VMs',
  'Cost management & governance (NCM Cost Governance)',
];

export function DashboardPage() {
  const { activeId } = useActiveConnection();

  const clusters = useQuery({
    queryKey: ['clusters', activeId],
    queryFn: () => api.listClusters(activeId!),
    enabled: !!activeId,
  });
  const projects = useQuery({
    queryKey: ['projects', activeId],
    queryFn: () => api.listProjects(activeId!),
    enabled: !!activeId,
  });
  const files = useQuery({
    queryKey: ['files', activeId],
    queryFn: () => api.listFileServers(activeId!),
    enabled: !!activeId,
  });
  const objects = useQuery({
    queryKey: ['objects', activeId],
    queryFn: () => api.listObjectStores(activeId!),
    enabled: !!activeId,
  });
  const vms = useQuery({
    queryKey: ['vms', activeId, null],
    queryFn: () => api.listVms(activeId!),
    enabled: !!activeId,
  });
  const utilization = useQuery({
    queryKey: ['project-utilization', activeId],
    queryFn: () => api.getProjectUtilization(activeId!),
    enabled: !!activeId,
  });
  const cost = useQuery({
    queryKey: ['cost-summary', activeId],
    queryFn: () => api.getCostSummary(activeId!),
    enabled: !!activeId,
  });

  return (
    <Stack>
      <div>
        <Title order={2}>Dashboard</Title>
        <Text c="dimmed">
          Overview of your Nutanix services managed through ResearchCloud.
        </Text>
      </div>

      {!activeId ? (
        <NoConnection />
      ) : (
        <>
          <SimpleGrid cols={{ base: 1, sm: 2, lg: 5 }}>
            <StatCard label="Clusters" value={clusters.data?.length ?? '-'} icon={IconBuildingBank} />
            <StatCard label="Projects" value={projects.data?.length ?? '-'} icon={IconFolders} />
            <StatCard label="VMs" value={vms.data?.length ?? '-'} icon={IconDeviceDesktop} />
            <StatCard label="File servers" value={files.data?.length ?? '-'} icon={IconServer2} />
            <StatCard label="Object stores" value={objects.data?.length ?? '-'} icon={IconBox} />
          </SimpleGrid>

          <Grid>
            <Grid.Col span={{ base: 12, md: 8 }}>
              <Paper withBorder radius="md" p="lg" h="100%">
                <Title order={4} mb="md">
                  Project quota utilisation
                </Title>
                <Stack gap="lg">
                  {utilization.data?.map((p) => (
                    <div key={p.project_ext_id}>
                      <Text fw={600} mb={6}>
                        {p.project_name}
                      </Text>
                      <Stack gap={8}>
                        <UsageBar label="vCPU" usage={p.vcpus} />
                        <UsageBar label="Memory" usage={p.memory_gib} />
                        <UsageBar label="Storage" usage={p.storage_gib} />
                      </Stack>
                    </div>
                  ))}
                  {utilization.isLoading && <Text c="dimmed">Loading utilisation...</Text>}
                  {!utilization.isLoading && (utilization.data?.length ?? 0) === 0 && (
                    <Text c="dimmed">No projects to report on.</Text>
                  )}
                </Stack>
              </Paper>
            </Grid.Col>
            <Grid.Col span={{ base: 12, md: 4 }}>
              <Card withBorder radius="md" padding="lg" h="100%">
                <Group justify="space-between" mb="xs">
                  <Group gap="xs">
                    <ThemeIcon size={32} radius="md" variant="light" color="nutanix">
                      <IconReportMoney size={18} />
                    </ThemeIcon>
                    <Text fw={700}>Cost usage</Text>
                  </Group>
                  <Badge color="gray" variant="light" radius="sm">
                    Coming soon
                  </Badge>
                </Group>
                <Text c="dimmed" size="sm" mb="md">
                  Source: {cost.data?.source ?? 'NCM Cost Governance'}
                </Text>
                <Stack gap="xs">
                  <Group justify="space-between">
                    <Text size="sm" c="dimmed">
                      Month to date
                    </Text>
                    <Text fw={600}>
                      {cost.data?.month_to_date != null
                        ? `${cost.data.currency} ${cost.data.month_to_date.toLocaleString()}`
                        : '—'}
                    </Text>
                  </Group>
                  <Group justify="space-between">
                    <Text size="sm" c="dimmed">
                      Forecast
                    </Text>
                    <Text fw={600}>
                      {cost.data?.forecast != null
                        ? `${cost.data.currency} ${cost.data.forecast.toLocaleString()}`
                        : '—'}
                    </Text>
                  </Group>
                </Stack>
                <Text size="xs" c="dimmed" mt="md">
                  {cost.data?.note ??
                    'Cost data will be sourced from NCM Cost Governance (Phase 7).'}
                </Text>
              </Card>
            </Grid.Col>
          </Grid>
        </>
      )}

      <SimpleGrid cols={{ base: 1, md: 2 }}>
        <Paper withBorder radius="md" p="lg">
          <Title order={4} mb="sm">
            Available now
          </Title>
          <List
            spacing="xs"
            icon={
              <ThemeIcon color="teal" size={20} radius="xl">
                <IconCircleCheck size={14} />
              </ThemeIcon>
            }
          >
            {DELIVERED.map((item) => (
              <List.Item key={item}>{item}</List.Item>
            ))}
          </List>
        </Paper>
        <Paper withBorder radius="md" p="lg">
          <Title order={4} mb="sm">
            Roadmap
          </Title>
          <List
            spacing="xs"
            icon={
              <ThemeIcon color="gray" size={20} radius="xl">
                <IconCircleDashed size={14} />
              </ThemeIcon>
            }
          >
            {ROADMAP.map((item) => (
              <List.Item key={item}>{item}</List.Item>
            ))}
          </List>
        </Paper>
      </SimpleGrid>
    </Stack>
  );
}

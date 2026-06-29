import {
  Card,
  Group,
  List,
  Paper,
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
  IconServer2,
} from '@tabler/icons-react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import { NoConnection } from '../components/NoConnection';
import { useActiveConnection } from '../state/ConnectionContext';

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
];

const ROADMAP = [
  'Self-Service blueprint builder & runbooks (Calm DSL)',
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
        <SimpleGrid cols={{ base: 1, sm: 2, lg: 5 }}>
          <StatCard label="Clusters" value={clusters.data?.length ?? '-'} icon={IconBuildingBank} />
          <StatCard label="Projects" value={projects.data?.length ?? '-'} icon={IconFolders} />
          <StatCard label="VMs" value={vms.data?.length ?? '-'} icon={IconDeviceDesktop} />
          <StatCard label="File servers" value={files.data?.length ?? '-'} icon={IconServer2} />
          <StatCard label="Object stores" value={objects.data?.length ?? '-'} icon={IconBox} />
        </SimpleGrid>
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

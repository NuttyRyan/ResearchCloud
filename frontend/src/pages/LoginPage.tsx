import {
  Alert,
  Button,
  Center,
  Group,
  Paper,
  PasswordInput,
  Stack,
  Text,
  TextInput,
  Title,
} from '@mantine/core';
import { useForm } from '@mantine/form';
import { IconCloud } from '@tabler/icons-react';
import { useState } from 'react';
import { ApiError } from '../api/client';
import { useAuth } from '../auth/AuthContext';

export function LoginPage() {
  const { login } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const form = useForm({
    initialValues: { username: 'admin', password: 'admin' },
  });

  const onSubmit = form.onSubmit(async (values) => {
    setError(null);
    setLoading(true);
    try {
      await login(values.username, values.password);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  });

  return (
    <Center mih="100vh" bg="charcoal.0">
      <Paper shadow="md" radius="lg" p="xl" w={400} withBorder>
        <Stack>
          <Group gap="xs" justify="center">
            <IconCloud size={36} color="var(--mantine-color-nutanix-5)" />
            <Title order={2} c="nutanix.7">
              ResearchCloud
            </Title>
          </Group>
          <Text c="dimmed" ta="center" size="sm">
            Sign in to manage your Nutanix services
          </Text>
          {error && (
            <Alert color="red" variant="light">
              {error}
            </Alert>
          )}
          <form onSubmit={onSubmit}>
            <Stack>
              <TextInput
                label="Username"
                required
                {...form.getInputProps('username')}
              />
              <PasswordInput
                label="Password"
                required
                {...form.getInputProps('password')}
              />
              <Button type="submit" loading={loading} fullWidth mt="sm">
                Sign in
              </Button>
            </Stack>
          </form>
        </Stack>
      </Paper>
    </Center>
  );
}

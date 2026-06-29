import { Alert, Anchor } from '@mantine/core';
import { IconInfoCircle } from '@tabler/icons-react';
import { Link } from 'react-router-dom';

export function NoConnection() {
  return (
    <Alert
      icon={<IconInfoCircle />}
      color="nutanix"
      variant="light"
      title="No Prism Central selected"
    >
      Add and select a Prism Central connection on the{' '}
      <Anchor component={Link} to="/connections">
        Prism Central
      </Anchor>{' '}
      page to manage resources.
    </Alert>
  );
}

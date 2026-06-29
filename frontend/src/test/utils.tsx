import { MantineProvider } from '@mantine/core';
import { render, type RenderOptions } from '@testing-library/react';
import type { ReactElement, ReactNode } from 'react';
import { theme } from '../theme';

function Wrapper({ children }: { children: ReactNode }) {
  return (
    <MantineProvider theme={theme} defaultColorScheme="light">
      {children}
    </MantineProvider>
  );
}

export function renderWithProviders(
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>,
) {
  return render(ui, { wrapper: Wrapper, ...options });
}

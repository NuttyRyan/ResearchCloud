import { screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { renderWithProviders } from '../test/utils';
import { StateBadge } from './StateBadge';

describe('StateBadge', () => {
  it('renders the provided state label', () => {
    renderWithProviders(<StateBadge state="DEPLOYING" />);
    expect(screen.getByText('DEPLOYING')).toBeInTheDocument();
  });

  it('renders unknown states without crashing', () => {
    renderWithProviders(<StateBadge state="WEIRD" />);
    expect(screen.getByText('WEIRD')).toBeInTheDocument();
  });
});

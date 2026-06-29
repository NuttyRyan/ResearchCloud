import { createTheme, type MantineColorsTuple } from '@mantine/core';

// Nutanix-inspired purple palette built around the brand color #7855fa.
const nutanixPurple: MantineColorsTuple = [
  '#f2effe',
  '#e0d8fc',
  '#bfaef7',
  '#9c81f3',
  '#7f5cef',
  '#7855fa',
  '#6a45e8',
  '#5836c4',
  '#472ca0',
  '#36217d',
];

// Charcoal grays used for surfaces and text, matching Nutanix's neutral tones.
const charcoal: MantineColorsTuple = [
  '#f4f5f7',
  '#e7e9ee',
  '#cbcfd9',
  '#aab1c2',
  '#8d97ad',
  '#79839c',
  '#5f6a83',
  '#454f68',
  '#333a4d',
  '#22283a',
];

export const theme = createTheme({
  primaryColor: 'nutanix',
  primaryShade: 5,
  colors: {
    nutanix: nutanixPurple,
    charcoal,
  },
  fontFamily:
    'Nunito, "Nutanix Soft", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  headings: {
    fontFamily:
      'Nunito, "Nutanix Soft", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    fontWeight: '700',
  },
  defaultRadius: 'md',
});

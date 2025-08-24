import { render, screen } from '@testing-library/react';
import App from './App';

test('renders without crashing', () => {
  render(<App />);
  // This test will fail if there are any syntax errors in the component tree
  expect(screen.getByRole('main')).toBeInTheDocument();
});

test('contains main navigation elements', () => {
  render(<App />);
  // Test for main app structure
  const mainElement = screen.getByRole('main');
  expect(mainElement).toBeInTheDocument();
});
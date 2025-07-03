// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';

// Mock chart components to avoid HTMLCanvasElement.getContext error
jest.mock('react-chartjs-2', () => ({
  Pie: () => 'PieChart',
  Bar: () => 'BarChart',
  Scatter: () => 'ScatterChart',
  Line: () => 'LineChart'
}));

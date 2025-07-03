import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import PortfolioOptimization from '../PortfolioOptimization';
import { portfolioService } from '../../services/portfolioService';

// Mock portfolioService methods
jest.mock('../../services/portfolioService', () => ({
  portfolioService: {
    optimizePortfolio: jest.fn(),
    getEfficientFrontier: jest.fn(),
    getCorrelationMatrix: jest.fn()
  }
}));

describe('PortfolioOptimization integration', () => {
  beforeEach(() => {
    // Mock optimizePortfolio to resolve with dummy data
    (portfolioService.optimizePortfolio as jest.Mock).mockResolvedValue({
      weights: { AAPL: 0.5, GOOGL: 0.5 },
      expected_return: 0.1,
      volatility: 0.2,
      sharpe_ratio: 1.5,
      expected_dividend_yield: 0.03
    });
    // Mock getEfficientFrontier to resolve with dummy points
    (portfolioService.getEfficientFrontier as jest.Mock).mockResolvedValue({
      frontier_points: [
        { volatility: 0.1, expected_return: 0.05 },
        { volatility: 0.2, expected_return: 0.1 }
      ]
    });

    // Mock getCorrelationMatrix to resolve with identity matrix
    (portfolioService.getCorrelationMatrix as jest.Mock).mockResolvedValue({
      tickers: ['AAPL', 'GOOGL'],
      matrix: [ [1, 0.5], [0.5, 1] ],
      order: ['AAPL', 'GOOGL']
    });
  });

  it('runs optimization and displays tabs with placeholders', async () => {
    render(<PortfolioOptimization />);

    // Click Run EPO Analysis button
    const optimizeButton = screen.getByRole('button', { name: /run epo analysis/i });
    userEvent.click(optimizeButton);

    // Wait for Tabs to appear
    await waitFor(() => {
      expect(screen.getByRole('tab', { name: /overview/i })).toBeInTheDocument();
    });

    // Verify Correlation matrix displays
    userEvent.click(screen.getByRole('tab', { name: /correlation/i }));
    await waitFor(() => {
      expect(screen.getAllByText(/aapl/i).length).toBeGreaterThan(0);
    });
  });
}); 
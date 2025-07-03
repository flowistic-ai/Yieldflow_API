import { TAB_LABELS } from '../PortfolioOptimization.constants';

describe('PortfolioOptimization tabs', () => {
  it('exports the correct tab labels', () => {
    expect(TAB_LABELS).toEqual([
      'Overview',
      'Efficient Frontier',
      'Correlation'
    ]);
  });
}); 
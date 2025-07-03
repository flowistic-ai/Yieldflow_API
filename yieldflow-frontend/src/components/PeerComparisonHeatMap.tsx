import React from 'react';
import { Box, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Typography } from '@mui/material';

interface PeersObject {
  [symbol: string]: number;
}

interface MetricData {
  target: number;
  peers: PeersObject;
  percentile_rank: number;
}

interface PeerComparisonData {
  dividend_yield: MetricData;
  payout_ratio: MetricData;
  dividend_growth_5y: MetricData;
}

interface SectorBenchmarks {
  avg_yield?: number;
  avg_payout?: number;
  avg_growth?: number;
}

interface Props {
  ticker: string;
  data: PeerComparisonData;
  sectorBenchmarks?: SectorBenchmarks;
}

const metricLabels: Record<keyof PeerComparisonData, string> = {
  dividend_yield: 'Dividend Yield %',
  payout_ratio: 'Payout Ratio %',
  dividend_growth_5y: '5Y Dividend Growth %',
};

const PeerComparisonHeatMap: React.FC<Props> = ({ ticker, data, sectorBenchmarks }) => {
  // collect list of tickers
  const tickersSet = new Set<string>();
  Object.values(data).forEach(metric => {
    tickersSet.add(ticker);
    Object.keys(metric.peers).forEach(sym => tickersSet.add(sym));
  });
  if (sectorBenchmarks) {
    tickersSet.add('Industry');
  }
  const tickers = Array.from(tickersSet);

  // Build matrix
  type MetricKey = keyof PeerComparisonData;
  const metricKeys: MetricKey[] = ['dividend_yield', 'payout_ratio', 'dividend_growth_5y'];

  // Gather values
  const values: Record<MetricKey, Record<string, number | undefined>> = {
    dividend_yield: {},
    payout_ratio: {},
    dividend_growth_5y: {},
  } as any;

  metricKeys.forEach(key => {
    // target
    values[key][ticker] = data[key].target;
    // peers
    Object.entries(data[key].peers).forEach(([sym, val]) => {
      values[key][sym] = val;
    });
    // industry average if present
    if (sectorBenchmarks) {
      if (key === 'dividend_yield') values[key]['Industry'] = sectorBenchmarks.avg_yield;
      if (key === 'payout_ratio') values[key]['Industry'] = sectorBenchmarks.avg_payout;
      if (key === 'dividend_growth_5y') values[key]['Industry'] = sectorBenchmarks.avg_growth;
    }
  });

  // For each metric compute min & max for color scaling
  const ranges: Record<MetricKey, { min: number; max: number }> = {} as any;
  metricKeys.forEach(k => {
    const vals = Object.values(values[k]).filter(v => v !== undefined) as number[];
    ranges[k] = { min: Math.min(...vals), max: Math.max(...vals) };
  });

  const getCellColor = (metric: MetricKey, val?: number) => {
    if (val === undefined) return undefined;
    const { min, max } = ranges[metric];
    // normalize 0-1
    const norm = max === min ? 0.5 : (val - min) / (max - min);
    // diverging palette: below industry average red -> green
    const hue = 120 * norm; // 0=red, 120=green
    const lightness = 90 - 40 * norm; // 90% to 50%
    return `hsl(${hue},70%,${lightness}%)`;
  };

  return (
    <Box>
      <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
        <Table stickyHeader size="small">
          <TableHead>
            <TableRow>
              <TableCell><strong>Metric</strong></TableCell>
              {tickers.map(sym => (
                <TableCell key={sym} align="center"><strong>{sym}</strong></TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {metricKeys.map(metric => (
              <TableRow key={metric}>
                <TableCell><Typography variant="body2">{metricLabels[metric]}</Typography></TableCell>
                {tickers.map(sym => {
                  const val = values[metric][sym];
                  return (
                    <TableCell key={sym} align="center" sx={{ backgroundColor: getCellColor(metric, val) }}>
                      {val !== undefined ? val.toFixed(2) : '—'}
                    </TableCell>
                  );
                })}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default PeerComparisonHeatMap; 
import React, { useState, useMemo } from 'react';
import {
  Box,
  Paper,
  Typography,
  Tooltip,
  Card,
  CardContent,
  Chip,
  Stack,
  useTheme,
  Alert,
} from '@mui/material';
import {
  CheckCircle,
  Cancel,
  Warning,
  TrendingUp,
  AccountBalance,
  MonetizationOn,
  Security,
  EventRepeat,
  VerifiedUser,
} from '@mui/icons-material';

interface MetricDetail {
  name: string;
  value: string | number;
  benchmark?: number;
  status: 'good' | 'warning' | 'poor' | 'neutral';
  description: string;
}

export interface SnowflakeCategory {
  id: string;
  name: string;
  score: number; // 0-6 scale
  color: string;
  icon: React.ReactNode;
  metrics: MetricDetail[];
  description: string;
}

interface DividendQualitySnowflakeProps {
  analysis: any;
  ticker: string;
  companyInfo?: any;
}

const DividendQualitySnowflake: React.FC<DividendQualitySnowflakeProps> = ({ 
  analysis, 
  ticker, 
  companyInfo 
}) => {
  const theme = useTheme();
  const [hoveredCategory, setHoveredCategory] = useState<string | null>(null);

  // Transform dividend analysis data to snowflake categories
  const transformToDividendCategories = (analysisData: any): SnowflakeCategory[] => {
    if (!analysisData?.dividend_quality_score) {
      return [];
    }

    const dqScore = analysisData.dividend_quality_score;
    const quality = analysisData.quality_analysis;
    const coverage = analysisData.coverage_analysis;
    const stability = analysisData.financial_stability_analysis;
    const growth = analysisData.growth_analytics;

    const safeNum = (val: any, defaultVal = 0) => (typeof val === 'number' && isFinite(val) ? val : defaultVal);
    const formatPercent = (val: any) => `${(safeNum(val) * 100).toFixed(1)}%`;
    const formatRatio = (val: any) => `${safeNum(val).toFixed(2)}x`;
    const scaleScore = (score: any) => (safeNum(score, 0) / 100) * 6; // Convert 0-100 to 0-6 scale

    // Access components properly - they might be nested
    const components = dqScore.components || dqScore;

    return [
      {
        id: 'consistency',
        name: 'Consistency',
        score: scaleScore(components.consistency_score || components.consistency || 0),
        color: '#059669',
        icon: <EventRepeat />,
        description: 'Years of maintained/increased dividends (25% weight)',
        metrics: [
          { 
            name: 'Years of Growth', 
            value: safeNum(growth?.consecutive_increases || 0), 
            status: safeNum(growth?.consecutive_increases || 0) >= 10 ? 'good' : 
                   safeNum(growth?.consecutive_increases || 0) >= 5 ? 'warning' : 'poor',
            description: 'Consecutive years of dividend increases' 
          },
          { 
            name: 'Years Analyzed', 
            value: safeNum(analysisData.analysis_period?.years_analyzed || 0), 
            status: safeNum(analysisData.analysis_period?.years_analyzed || 0) >= 15 ? 'good' : 
                   safeNum(analysisData.analysis_period?.years_analyzed || 0) >= 10 ? 'warning' : 'poor',
            description: 'Years of dividend data analyzed' 
          },
          { 
            name: 'Consistency Score', 
            value: `${safeNum(components.consistency_score || components.consistency || 0)}/100`, 
            status: safeNum(components.consistency_score || components.consistency || 0) >= 70 ? 'good' : 
                   safeNum(components.consistency_score || components.consistency || 0) >= 50 ? 'warning' : 'poor',
            description: 'Based on dividend track record' 
          },
        ],
      },
      {
        id: 'growth',
        name: 'Growth',
        score: scaleScore(components.growth_score || components.growth || 0),
        color: '#3B82F6',
        icon: <TrendingUp />,
        description: 'CAGR analysis with 5-15% optimal target (25% weight)',
        metrics: [
          { 
            name: '5-Year CAGR', 
            value: formatPercent(growth?.cagr_analysis?.['5y_cagr'] / 100 || 0), 
            status: Math.abs(safeNum(growth?.cagr_analysis?.['5y_cagr'] || 0)) >= 5 && 
                   Math.abs(safeNum(growth?.cagr_analysis?.['5y_cagr'] || 0)) <= 15 ? 'good' : 
                   Math.abs(safeNum(growth?.cagr_analysis?.['5y_cagr'] || 0)) > 0 ? 'warning' : 'poor',
            description: '5-year compound annual growth rate' 
          },
          { 
            name: '10-Year CAGR', 
            value: formatPercent(growth?.cagr_analysis?.['10y_cagr'] / 100 || 0), 
            status: Math.abs(safeNum(growth?.cagr_analysis?.['10y_cagr'] || 0)) >= 5 && 
                   Math.abs(safeNum(growth?.cagr_analysis?.['10y_cagr'] || 0)) <= 15 ? 'good' : 
                   Math.abs(safeNum(growth?.cagr_analysis?.['10y_cagr'] || 0)) > 0 ? 'warning' : 'poor',
            description: '10-year compound annual growth rate' 
          },
          { 
            name: 'Growth Score', 
            value: `${safeNum(components.growth_score || components.growth || 0)}/100`, 
            status: safeNum(components.growth_score || components.growth || 0) >= 70 ? 'good' : 
                   safeNum(components.growth_score || components.growth || 0) >= 50 ? 'warning' : 'poor',
            description: 'Based on historical growth rates' 
          },
        ],
      },
      {
        id: 'coverage',
        name: 'Coverage',
        score: scaleScore(components.coverage_score || components.coverage || 0),
        color: '#F97316',
        icon: <VerifiedUser />,
        description: 'EPS & Free Cash Flow coverage ratios (25% weight)',
        metrics: [
          { 
            name: 'FCF Coverage', 
            value: formatRatio(coverage?.coverage_ratios?.fcf_coverage || 0), 
            status: safeNum(coverage?.coverage_ratios?.fcf_coverage || 0) >= 2.0 ? 'good' : 
                   safeNum(coverage?.coverage_ratios?.fcf_coverage || 0) >= 1.5 ? 'warning' : 'poor',
            description: 'Free cash flow coverage ratio' 
          },
          { 
            name: 'EPS Coverage', 
            value: formatRatio(coverage?.coverage_ratios?.eps_coverage || 0), 
            status: safeNum(coverage?.coverage_ratios?.eps_coverage || 0) >= 2.0 ? 'good' : 
                   safeNum(coverage?.coverage_ratios?.eps_coverage || 0) >= 1.5 ? 'warning' : 'poor',
            description: 'Earnings per share coverage ratio' 
          },
          { 
            name: 'Coverage Score', 
            value: `${safeNum(components.coverage_score || components.coverage || 0)}/100`, 
            status: safeNum(components.coverage_score || components.coverage || 0) >= 70 ? 'good' : 
                   safeNum(components.coverage_score || components.coverage || 0) >= 50 ? 'warning' : 'poor',
            description: 'Overall coverage assessment' 
          },
        ],
      },
      {
        id: 'yield_quality',
        name: 'Yield Quality',
        score: scaleScore(components.yield_quality_score || components.yield_quality || 0),
        color: '#8B5CF6',
        icon: <MonetizationOn />,
        description: 'Stability vs volatility assessment (15% weight)',
        metrics: [
          { 
            name: 'Current Yield', 
            value: formatPercent(analysisData.current_metrics?.current_yield_pct || 0), 
            status: safeNum(analysisData.current_metrics?.current_yield_pct || 0) >= 0.02 && 
                   safeNum(analysisData.current_metrics?.current_yield_pct || 0) <= 0.06 ? 'good' :
                   safeNum(analysisData.current_metrics?.current_yield_pct || 0) > 0 ? 'warning' : 'poor',
            description: 'Current annual dividend yield' 
          },
          { 
            name: 'Yield Percentile', 
            value: `${safeNum(analysisData.performance_analytics?.yield_percentile_ranking || 0).toFixed(0)}%`, 
            status: safeNum(analysisData.performance_analytics?.yield_percentile_ranking || 0) >= 70 ? 'good' : 
                   safeNum(analysisData.performance_analytics?.yield_percentile_ranking || 0) >= 50 ? 'warning' : 'poor',
            description: 'Historical yield ranking' 
          },
          { 
            name: 'Yield Quality Score', 
            value: `${safeNum(components.yield_quality_score || components.yield_quality || 0)}/100`, 
            status: safeNum(components.yield_quality_score || components.yield_quality || 0) >= 70 ? 'good' : 
                   safeNum(components.yield_quality_score || components.yield_quality || 0) >= 50 ? 'warning' : 'poor',
            description: 'Based on yield sustainability' 
          },
        ],
      },
      {
        id: 'financial_strength',
        name: 'Financial Strength',
        score: scaleScore(components.financial_strength_score || components.financial_strength || 0),
        color: '#DB2777',
        icon: <AccountBalance />,
        description: 'ROE and balance sheet metrics (10% weight)',
        metrics: [
          { 
            name: 'Sustainability Score', 
            value: `${safeNum(analysisData.sustainability_analysis?.sustainability_score || 0)}/100`, 
            status: safeNum(analysisData.sustainability_analysis?.sustainability_score || 0) >= 70 ? 'good' : 
                   safeNum(analysisData.sustainability_analysis?.sustainability_score || 0) >= 50 ? 'warning' : 'poor',
            description: 'Overall dividend sustainability' 
          },
          { 
            name: 'Risk Score', 
            value: `${safeNum(analysisData.risk_assessment?.risk_score || 0)}/100`, 
            status: safeNum(analysisData.risk_assessment?.risk_score || 0) <= 40 ? 'good' : 
                   safeNum(analysisData.risk_assessment?.risk_score || 0) <= 60 ? 'warning' : 'poor',
            description: 'Lower is better - dividend risk assessment' 
          },
          { 
            name: 'Financial Score', 
            value: `${safeNum(components.financial_strength_score || components.financial_strength || 0)}/100`, 
            status: safeNum(components.financial_strength_score || components.financial_strength || 0) >= 70 ? 'good' : 
                   safeNum(components.financial_strength_score || components.financial_strength || 0) >= 50 ? 'warning' : 'poor',
            description: 'Overall financial health assessment' 
          },
        ],
      },
    ];
  };

  const categories = transformToDividendCategories(analysis);
  const overallScore = analysis?.dividend_quality_score?.quality_score || 0;
  const qualityGrade = analysis?.dividend_quality_score?.grade || 'F';
  const qualityRating = analysis?.dividend_quality_score?.rating || 'No Rating';
  const companyName = companyInfo?.shortName || ticker;

  // Calculate snowflake points for visualization
  const calculateSnowflakePoints = (cats: SnowflakeCategory[]) => {
    const center = { x: 200, y: 175 };
    const radius = 130;
    return cats.map((cat, i) => {
      const angle = (i * 2 * Math.PI) / cats.length - Math.PI / 2;
      const scoreRadius = (cat.score / 6) * radius;
      return {
        x: center.x + scoreRadius * Math.cos(angle),
        y: center.y + scoreRadius * Math.sin(angle),
        angle: angle,
        category: cat
      };
    });
  };

  const points = calculateSnowflakePoints(categories);

  const getTextAnchor = (angle: number) => {
    // Determine text-anchor based on angle to flow text away from the center
    const degrees = angle * (180 / Math.PI);
    if (degrees > -45 && degrees <= 45) return 'start'; // Right
    if (degrees > 45 && degrees <= 135) return 'middle'; // Bottom
    if (degrees > 135 || degrees <= -135) return 'end'; // Left
    return 'middle'; // Top
  };

  const createSnowflakePath = (points: any[]) => {
    if (points.length === 0) return '';
    return points.map((p, i) => (i === 0 ? 'M' : 'L') + `${p.x},${p.y}`).join(' ') + ' Z';
  };
  
  const pathData = createSnowflakePath(points);

  const getStatusIcon = (status: 'good' | 'warning' | 'poor' | 'neutral') => {
    switch (status) {
      case 'good':
        return <CheckCircle sx={{ fontSize: 16, color: theme.palette.success.main }} />;
      case 'warning':
        return <Warning sx={{ fontSize: 16, color: theme.palette.warning.main }} />;
      case 'poor':
        return <Cancel sx={{ fontSize: 16, color: theme.palette.error.main }} />;
      case 'neutral':
        return <Security sx={{ fontSize: 16, color: theme.palette.text.secondary }} />;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 70) return theme.palette.success.main;
    if (score >= 50) return theme.palette.warning.main;
    return theme.palette.error.main;
  };

  const getGradeColor = (grade: string) => {
    if (grade === 'A+' || grade === 'A') return 'success';
    if (grade === 'B') return 'warning';
    return 'error';
  };

  if (!categories || categories.length === 0) {
    return (
      <Alert severity="info" sx={{ m: 3 }}>
        No dividend quality data available for visualization.
      </Alert>
    );
  }

  return (
    <Paper sx={{ p: 3, borderRadius: 2, bgcolor: 'transparent', boxShadow: 'none' }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h5" sx={{ fontWeight: 700, mb: 1 }}>
          Dividend Quality Snowflake Analysis
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {ticker} • {companyName} • Visual breakdown of dividend quality components
        </Typography>
      </Box>
      
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', lg: '1fr 1fr' }, gap: 4 }}>
        {/* Snowflake Visualization */}
        <Box>
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
            <svg 
              width="100%" 
              height="320" 
              viewBox="0 0 400 350"
              aria-labelledby="snowflake-title"
            >
              <defs>
                <filter id="dropshadow" height="130%">
                  <feDropShadow 
                    dx="2" 
                    dy="4" 
                    stdDeviation="3" 
                    floodColor="rgba(0,0,0,0.2)"
                  />
                </filter>
              </defs>
              <title id="snowflake-title">{`${ticker || '...'} Dividend Quality Snowflake Analysis`}</title>
              
              {/* Grid lines and axis labels */}
              {points.map((p, i) => {
                const labelRadius = 165;
                let yOffset = 0;
                if (categories[i].id === 'yield_quality') {
                  yOffset = 10; // Add extra margin for the bottom label
                }

                return (
                  <g key={`axis-${i}`}>
                    <line x1={200} y1={175} x2={p.x} y2={p.y} stroke="#E0E0E0" strokeWidth="1" />
                    <text
                      x={200 + labelRadius * Math.cos(p.angle)}
                      y={175 + labelRadius * Math.sin(p.angle) + yOffset}
                      textAnchor={getTextAnchor(p.angle)}
                      dominantBaseline="central"
                      fill="#616161"
                      fontSize="14"
                      fontWeight="500"
                    >
                      {categories[i].name.split(' ').map((word, index) => (
                        <tspan key={index} x={200 + labelRadius * Math.cos(p.angle)} dy={index > 0 ? '1.2em' : 0}>
                          {word}
                        </tspan>
                      ))}
                    </text>
                  </g>
                )
              })}
              
              {/* Snowflake shape */}
              <path
                d={pathData}
                fill="rgba(16, 185, 129, 0.4)"
                stroke="#10B981"
                strokeWidth="2"
                style={{ transition: 'd 0.3s ease-in-out' }}
                filter="url(#dropshadow)"
              />
              
              {/* Category points */}
              {points.map((point, index) => (
                <g key={index}>
                  <circle
                    cx={point.x}
                    cy={point.y}
                    r="8"
                    fill={point.category.color}
                    stroke="white"
                    strokeWidth="2"
                    style={{ cursor: 'pointer' }}
                    onMouseEnter={() => setHoveredCategory(point.category.id)}
                    onMouseLeave={() => setHoveredCategory(null)}
                  />
                  
                  {/* Category labels */}
                  <text
                    x={point.x}
                    y={point.y + 20}
                    textAnchor="middle"
                    fontSize="10"
                    fontWeight="600"
                    fill={point.category.color}
                  >
                    {point.category.score.toFixed(1)}/6
                  </text>
                </g>
              ))}
              
              {/* Center point */}
              <circle cx="200" cy="175" r="4" fill="#374151" />
            </svg>
          </Box>
        </Box>

        {/* Category Details */}
        <Box>
          <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
            Component Breakdown
          </Typography>
          <Stack spacing={2}>
            {categories.map((category) => (
              <Card 
                key={category.id}
                sx={{ 
                  border: hoveredCategory === category.id ? `2px solid ${category.color}` : '1px solid #E5E7EB',
                  transition: 'all 0.2s ease',
                  cursor: 'pointer',
                }}
                onMouseEnter={() => setHoveredCategory(category.id)}
                onMouseLeave={() => setHoveredCategory(null)}
              >
                <CardContent sx={{ p: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Box sx={{ color: category.color }}>
                        {category.icon}
                      </Box>
                      <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                        {category.name}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="h6" sx={{ fontWeight: 700, color: category.color }}>
                        {category.score.toFixed(1)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        /6
                      </Typography>
                    </Box>
                  </Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2, fontSize: '0.75rem' }}>
                    {category.description}
                  </Typography>
                  <Stack spacing={1}>
                    {category.metrics.slice(0, 3).map((metric, index) => (
                      <Box key={index} sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {getStatusIcon(metric.status)}
                          <Typography variant="body2" sx={{ fontSize: '0.75rem' }}>
                            {metric.name}
                          </Typography>
                        </Box>
                        <Typography variant="body2" sx={{ fontWeight: 600, fontSize: '0.75rem' }}>
                          {metric.value}
                        </Typography>
                      </Box>
                    ))}
                  </Stack>
                </CardContent>
              </Card>
            ))}
          </Stack>
        </Box>
      </Box>

      {/* Overall Score Summary */}
      <Box sx={{ mt: 4, p: 3, bgcolor: 'action.hover', borderRadius: 2 }}>
        <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
          Dividend Quality Summary
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 3, flexWrap: 'wrap' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="h3" sx={{ fontWeight: 700, color: getScoreColor(overallScore) }}>
              {overallScore.toFixed(1)}
            </Typography>
            <Typography variant="h6" color="text.secondary">
              / 100
            </Typography>
          </Box>
          <Chip
            label={qualityGrade}
            color={getGradeColor(qualityGrade)}
            sx={{
              fontWeight: 600,
              fontSize: '0.9rem',
            }}
          />
          <Chip
            label={qualityRating}
            sx={{
              bgcolor: getScoreColor(overallScore),
              color: 'white',
              fontWeight: 600,
              fontSize: '0.9rem',
            }}
          />
          <Typography variant="body1" color="text.secondary" sx={{ flex: 1, minWidth: 200 }}>
            Methodology: Consistency (25%), Growth (25%), Coverage (25%), Yield Quality (15%), Financial Strength (10%)
          </Typography>
        </Box>
      </Box>
    </Paper>
  );
};

export default DividendQualitySnowflake; 
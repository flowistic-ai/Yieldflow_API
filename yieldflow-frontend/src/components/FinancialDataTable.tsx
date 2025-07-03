import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Box,
  Typography,
  useTheme,
  TableSortLabel,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  MoreVert as MoreVertIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Remove as FlatIcon,
} from '@mui/icons-material';
import StatusIndicator, { StatusType } from './StatusIndicator';

export interface ColumnConfig {
  key: string;
  label: string;
  type?: 'text' | 'number' | 'currency' | 'percentage' | 'status';
  align?: 'left' | 'center' | 'right';
  sortable?: boolean;
  width?: string | number;
  precision?: number;
  prefix?: string;
  suffix?: string;
  statusType?: StatusType;
  showTrend?: boolean;
}

export interface RowData {
  [key: string]: any;
  id?: string | number;
}

export interface FinancialDataTableProps {
  columns: ColumnConfig[];
  data: RowData[];
  variant?: 'dense' | 'normal' | 'comfortable';
  showActions?: boolean;
  onRowClick?: (row: RowData) => void;
  onSort?: (column: string, direction: 'asc' | 'desc') => void;
  sortColumn?: string;
  sortDirection?: 'asc' | 'desc';
  maxHeight?: number | string;
  stickyHeader?: boolean;
  loading?: boolean;
  emptyMessage?: string;
}

const FinancialDataTable: React.FC<FinancialDataTableProps> = ({
  columns,
  data,
  variant = 'dense',
  showActions = false,
  onRowClick,
  onSort,
  sortColumn,
  sortDirection,
  maxHeight = 400,
  stickyHeader = true,
  loading = false,
  emptyMessage = 'No data available',
}) => {
  const theme = useTheme();

  // Get cell padding based on variant
  const getCellPadding = () => {
    switch (variant) {
      case 'dense':
        return '4px 8px';
      case 'comfortable':
        return '12px 16px';
      default:
        return '8px 12px';
    }
  };

  // Format cell value based on column type
  const formatCellValue = (value: any, column: ColumnConfig) => {
    if (value === null || value === undefined || value === '') {
      return '-';
    }

    const { type, precision = 2, prefix = '', suffix = '' } = column;

    switch (type) {
      case 'currency':
        return `${prefix}$${Number(value).toLocaleString(undefined, {
          minimumFractionDigits: precision,
          maximumFractionDigits: precision,
        })}${suffix}`;
      case 'percentage':
        return `${prefix}${(Number(value) * 100).toFixed(precision)}%${suffix}`;
      case 'number':
        return `${prefix}${Number(value).toLocaleString(undefined, {
          minimumFractionDigits: precision,
          maximumFractionDigits: precision,
        })}${suffix}`;
      default:
        return `${prefix}${value}${suffix}`;
    }
  };

  // Get status type for financial values
  const getFinancialStatusType = (value: number, column: ColumnConfig): StatusType => {
    if (column.statusType) return column.statusType;
    
    if (value > 0) return 'positive';
    if (value < 0) return 'negative';
    return 'neutral';
  };

  // Render cell content
  const renderCellContent = (value: any, column: ColumnConfig) => {
    if (column.type === 'status' || (column.showTrend && typeof value === 'number')) {
      return (
        <StatusIndicator
          value={value}
          type={getFinancialStatusType(value, column)}
          variant="text"
          size="small"
          showTrend={column.showTrend}
          format={column.type === 'currency' ? 'currency' : column.type === 'percentage' ? 'percentage' : 'number'}
          precision={column.precision}
          prefix={column.prefix}
          suffix={column.suffix}
        />
      );
    }

    return (
      <Typography
        variant="body2"
        sx={{
          fontFamily: column.type === 'text' ? 'inherit' : theme.typography.fontFamilyMonospace,
          fontWeight: column.type === 'text' ? 400 : 500,
          fontSize: variant === 'dense' ? '0.6875rem' : '0.75rem',
          color: theme.palette.text.primary,
        }}
      >
        {formatCellValue(value, column)}
      </Typography>
    );
  };

  // Handle sort
  const handleSort = (column: ColumnConfig) => {
    if (!onSort || !column.sortable) return;

    const isCurrentColumn = sortColumn === column.key;
    const newDirection = isCurrentColumn && sortDirection === 'asc' ? 'desc' : 'asc';
    onSort(column.key, newDirection);
  };

  return (
    <TableContainer
      component={Paper}
      sx={{
        maxHeight,
        border: `1px solid ${theme.palette.divider}`,
        borderRadius: 1,
        '& .MuiTable-root': {
          borderCollapse: 'separate',
          borderSpacing: 0,
        },
      }}
    >
      <Table stickyHeader={stickyHeader} size={variant === 'dense' ? 'small' : 'medium'}>
        <TableHead>
          <TableRow>
            {columns.map((column) => (
              <TableCell
                key={column.key}
                align={column.align || 'left'}
                sx={{
                  backgroundColor: theme.palette.grey[50],
                  borderBottom: `2px solid ${theme.palette.divider}`,
                  padding: getCellPadding(),
                  fontWeight: 700,
                  fontSize: '0.6875rem',
                  letterSpacing: '0.025em',
                  textTransform: 'uppercase',
                  color: theme.palette.text.secondary,
                  width: column.width,
                  position: 'sticky',
                  top: 0,
                  zIndex: 100,
                }}
              >
                {column.sortable ? (
                  <TableSortLabel
                    active={sortColumn === column.key}
                    direction={sortColumn === column.key ? sortDirection : 'asc'}
                    onClick={() => handleSort(column)}
                    sx={{
                      '& .MuiTableSortLabel-icon': {
                        fontSize: '0.875rem',
                      },
                    }}
                  >
                    {column.label}
                  </TableSortLabel>
                ) : (
                  column.label
                )}
              </TableCell>
            ))}
            {showActions && (
              <TableCell
                align="center"
                sx={{
                  backgroundColor: theme.palette.grey[50],
                  borderBottom: `2px solid ${theme.palette.divider}`,
                  padding: getCellPadding(),
                  width: 48,
                  position: 'sticky',
                  top: 0,
                  zIndex: 100,
                }}
              >
                Actions
              </TableCell>
            )}
          </TableRow>
        </TableHead>
        <TableBody>
          {loading ? (
            <TableRow>
              <TableCell
                colSpan={columns.length + (showActions ? 1 : 0)}
                align="center"
                sx={{ padding: '2rem' }}
              >
                <Typography variant="body2" color="text.secondary">
                  Loading...
                </Typography>
              </TableCell>
            </TableRow>
          ) : data.length === 0 ? (
            <TableRow>
              <TableCell
                colSpan={columns.length + (showActions ? 1 : 0)}
                align="center"
                sx={{ padding: '2rem' }}
              >
                <Typography variant="body2" color="text.secondary">
                  {emptyMessage}
                </Typography>
              </TableCell>
            </TableRow>
          ) : (
            data.map((row, index) => (
              <TableRow
                key={row.id || index}
                hover
                sx={{
                  cursor: onRowClick ? 'pointer' : 'default',
                  '&:hover': {
                    backgroundColor: theme.palette.action.hover,
                  },
                  '&:nth-of-type(even)': {
                    backgroundColor: theme.palette.action.hover,
                  },
                }}
                onClick={() => onRowClick?.(row)}
              >
                {columns.map((column) => (
                  <TableCell
                    key={column.key}
                    align={column.align || 'left'}
                    sx={{
                      padding: getCellPadding(),
                      borderBottom: `1px solid ${theme.palette.divider}`,
                    }}
                  >
                    {renderCellContent(row[column.key], column)}
                  </TableCell>
                ))}
                {showActions && (
                  <TableCell
                    align="center"
                    sx={{
                      padding: getCellPadding(),
                      borderBottom: `1px solid ${theme.palette.divider}`,
                    }}
                  >
                    <Tooltip title="More actions">
                      <IconButton size="small" sx={{ color: theme.palette.text.secondary }}>
                        <MoreVertIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                )}
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default FinancialDataTable; 
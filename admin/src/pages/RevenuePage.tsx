import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { 
  TrendingUp, 
  DollarSign, 
  CreditCard, 
  Users, 
  Download,
  Filter,
  Calendar,
  RefreshCw
} from 'lucide-react';
import { apiService } from '@/services/api';
import LoadingSpinner from '@/components/LoadingSpinner';
import { formatCurrency } from '@/utils/formatters';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];

interface RevenueData {
  id: number;
  order_id: number;
  amount: number;
  commission: number;
  platform_fee: number;
  seller_revenue: number;
  payment_method: string;
  created_at: string;
}

interface RevenueSummary {
  summary: {
    total_revenue: number;
    total_commission: number;
    total_platform_fees: number;
    total_seller_revenue: number;
    total_transactions: number;
  };
  payment_breakdown: Array<{
    method: string;
    count: number;
    total_amount: number;
  }>;
  daily_revenue: Array<{
    date: string;
    revenue: number;
  }>;
}

interface RevenueResponse {
  data: RevenueData[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

const RevenuePage: React.FC = () => {
  const [filters, setFilters] = useState({
    dateFrom: '',
    dateTo: '',
    paymentMethod: '',
    page: 1,
    limit: 10
  });

  const [summaryFilters, setSummaryFilters] = useState({
    dateFrom: '',
    dateTo: ''
  });

  // Fetch revenue data
  const { data: revenueData, isLoading: revenueLoading, refetch: refetchRevenue } = useQuery<RevenueResponse>({
    queryKey: ['revenue', filters],
    queryFn: () => apiService.getRevenue(filters),
    placeholderData: (previousData) => previousData,
  });

  // Fetch revenue summary
  const { data: summaryData, isLoading: summaryLoading, refetch: refetchSummary } = useQuery<RevenueSummary>({
    queryKey: ['revenue-summary', summaryFilters],
    queryFn: () => apiService.getRevenueSummary(summaryFilters),
    placeholderData: (previousData) => previousData,
  });

  const handleFilterChange = (key: string, value: string | number) => {
    setFilters(prev => ({ ...prev, [key]: value, page: 1 }));
  };

  const handleSummaryFilterChange = (key: string, value: string) => {
    setSummaryFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleExport = async (format: 'csv' | 'json') => {
    try {
      const exportData = await apiService.exportRevenue({
        dateFrom: filters.dateFrom,
        dateTo: filters.dateTo,
        format
      });
      
      // Create and download file
      const blob = new Blob([exportData.data], { type: exportData.content_type });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = exportData.filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  if (summaryLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Revenue Management</h1>
          <p className="text-gray-600 dark:text-gray-400">Track and analyze platform revenue</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => handleExport('csv')}
            className="btn btn-secondary"
          >
            <Download size={16} />
            Export CSV
          </button>
          <button
            onClick={() => handleExport('json')}
            className="btn btn-secondary"
          >
            <Download size={16} />
            Export JSON
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      {summaryData && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="card">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
                <DollarSign className="h-6 w-6 text-blue-600 dark:text-blue-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Revenue</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {formatCurrency(summaryData.summary.total_revenue)}
                </p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
                <TrendingUp className="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Platform Commission</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {formatCurrency(summaryData.summary.total_commission)}
                </p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
                <CreditCard className="h-6 w-6 text-yellow-600 dark:text-yellow-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Platform Fees</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {formatCurrency(summaryData.summary.total_platform_fees)}
                </p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
                <Users className="h-6 w-6 text-purple-600 dark:text-purple-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Transactions</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {summaryData.summary.total_transactions}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Daily Revenue Chart */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Daily Revenue (Last 7 Days)</h3>
            <div className="flex gap-2">
              <input
                type="date"
                value={summaryFilters.dateFrom}
                onChange={(e) => handleSummaryFilterChange('dateFrom', e.target.value)}
                className="input input-sm"
              />
              <input
                type="date"
                value={summaryFilters.dateTo}
                onChange={(e) => handleSummaryFilterChange('dateTo', e.target.value)}
                className="input input-sm"
              />
              <button
                onClick={() => refetchSummary()}
                className="btn btn-sm btn-secondary"
              >
                <RefreshCw size={14} />
              </button>
            </div>
          </div>
          <div className="card-content">
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={summaryData?.daily_revenue || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    tickFormatter={(value) => new Date(value).toLocaleDateString()}
                  />
                  <YAxis />
                  <Tooltip 
                    labelFormatter={(value) => new Date(value).toLocaleDateString()}
                    formatter={(value: number) => [formatCurrency(value), 'Revenue']}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="revenue" 
                    stroke="#3b82f6" 
                    strokeWidth={2}
                    dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Payment Method Breakdown */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Payment Method Breakdown</h3>
          </div>
          <div className="card-content">
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={summaryData?.payment_breakdown || []}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ method, total_amount }) => `${method}: ${formatCurrency(total_amount)}`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="total_amount"
                  >
                    {summaryData?.payment_breakdown.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: number) => [formatCurrency(value), 'Amount']} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>

      {/* Revenue Data Table */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Revenue Transactions</h3>
          <div className="flex gap-2 items-center">
            <input
              type="date"
              value={filters.dateFrom}
              onChange={(e) => handleFilterChange('dateFrom', e.target.value)}
              className="input input-sm"
              placeholder="From Date"
            />
            <input
              type="date"
              value={filters.dateTo}
              onChange={(e) => handleFilterChange('dateTo', e.target.value)}
              className="input input-sm"
              placeholder="To Date"
            />
            <select
              value={filters.paymentMethod}
              onChange={(e) => handleFilterChange('paymentMethod', e.target.value)}
              className="select select-sm"
            >
              <option value="">All Payment Methods</option>
              <option value="paygate">PayGate</option>
              <option value="payfast">PayFast</option>
              <option value="snapscan">SnapScan</option>
              <option value="zapper">Zapper</option>
              <option value="eft">EFT</option>
              <option value="cash_on_delivery">Cash on Delivery</option>
            </select>
            <button
              onClick={() => refetchRevenue()}
              className="btn btn-sm btn-secondary"
            >
              <RefreshCw size={14} />
            </button>
          </div>
        </div>
        <div className="card-content">
          {revenueLoading ? (
            <div className="flex items-center justify-center h-32">
              <LoadingSpinner />
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="table table-auto w-full">
                  <thead>
                    <tr>
                      <th>Order ID</th>
                      <th>Amount</th>
                      <th>Commission</th>
                      <th>Platform Fee</th>
                      <th>Seller Revenue</th>
                      <th>Payment Method</th>
                      <th>Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {revenueData?.data.map((revenue) => (
                      <tr key={revenue.id}>
                        <td>#{revenue.order_id}</td>
                        <td className="font-medium">{formatCurrency(revenue.amount)}</td>
                        <td>{formatCurrency(revenue.commission)}</td>
                        <td>{formatCurrency(revenue.platform_fee)}</td>
                        <td>{formatCurrency(revenue.seller_revenue)}</td>
                        <td>
                          <span className="badge badge-secondary">
                            {revenue.payment_method.replace('_', ' ')}
                          </span>
                        </td>
                        <td>{new Date(revenue.created_at).toLocaleDateString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {revenueData && revenueData.total_pages > 1 && (
                <div className="flex justify-between items-center mt-4">
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Showing {((filters.page - 1) * filters.limit) + 1} to{' '}
                    {Math.min(filters.page * filters.limit, revenueData.total)} of{' '}
                    {revenueData.total} results
                  </p>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleFilterChange('page', filters.page - 1)}
                      disabled={filters.page === 1}
                      className="btn btn-sm btn-secondary disabled:opacity-50"
                    >
                      Previous
                    </button>
                    <span className="flex items-center px-3 text-sm">
                      Page {filters.page} of {revenueData.total_pages}
                    </span>
                    <button
                      onClick={() => handleFilterChange('page', filters.page + 1)}
                      disabled={filters.page === revenueData.total_pages}
                      className="btn btn-sm btn-secondary disabled:opacity-50"
                    >
                      Next
                    </button>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default RevenuePage;

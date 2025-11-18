import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  Search, 
  Filter, 
  Eye, 
  Edit3, 
  Download,
  Calendar,
  User,
  Package,
  CreditCard,
  MapPin,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  ShoppingCart
} from 'lucide-react';
import { apiService } from '@/services/api';
import { Order, OrderFilters } from '@/types';
import LoadingSpinner from '@/components/LoadingSpinner';
import { toast } from 'react-hot-toast';

// Helper function to normalize image URLs for the admin panel
// Converts full URLs with IPs to relative paths that work with Vite proxy
const normalizeImageUrl = (imageUrl: string): string => {
  if (!imageUrl) return '';
  
  // If it's already a relative path, return as is
  if (imageUrl.startsWith('/images/')) {
    return imageUrl;
  }
  
  // If it's a full URL with any IP address, extract the path
  if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) {
    // Check if it's a profile image
    const profileMatch = imageUrl.match(/\/images\/profile\/(.+)$/);
    if (profileMatch) {
      return `/images/profile/${profileMatch[1]}`;
    }
    
    // Extract the path part after /images/
    const match = imageUrl.match(/\/images\/(.+)$/);
    if (match) {
      return `/images/${match[1]}`;
    }
    // If no /images/ in URL, try to extract filename
    const filename = imageUrl.split('/').pop();
    if (filename) {
      return `/images/${filename}`;
    }
  }
  
  // If it's just a filename, prepend /images/
  if (!imageUrl.startsWith('/')) {
    return `/images/${imageUrl}`;
  }
  
  return imageUrl;
};

const OrdersPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [limit] = useState(10);
  const [filters, setFilters] = useState<OrderFilters>({});
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [showFilters, setShowFilters] = useState(false);

  // Fetch orders
  const { data: ordersData, isLoading, error } = useQuery({
    queryKey: ['orders', page, limit, filters],
    queryFn: () => apiService.getOrders(filters, page, limit),
    placeholderData: (previousData) => previousData,
  });

  // Update order status mutation
  const updateStatusMutation = useMutation({
    mutationFn: (data: { orderId: number; status: string }) =>
      apiService.updateOrderStatus(data.orderId, data.status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orders'] });
      toast.success('Order status updated successfully');
    },
    onError: (error: any) => {
      console.error('Error updating order status:', error);
      toast.error('Failed to update order status');
    },
  });

  const handleStatusUpdate = (orderId: number, newStatus: string) => {
    updateStatusMutation.mutate({ orderId, status: newStatus });
  };

  const handleFilterChange = (key: keyof OrderFilters, value: string) => {
    setFilters(prev => ({
      ...prev,
      [key]: value || undefined
    }));
    setPage(1);
  };

  const handleSearch = () => {
    setFilters(prev => ({
      ...prev,
      search: searchTerm || undefined
    }));
    setPage(1);
  };

  const clearFilters = () => {
    setFilters({});
    setSearchTerm('');
    setPage(1);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'confirmed': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'shipped': return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'delivered': return 'bg-green-100 text-green-800 border-green-200';
      case 'cancelled': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getPaymentMethodIcon = (method: string) => {
    switch (method.toLowerCase()) {
      case 'paygate':
      case 'payfast':
        return <CreditCard className="w-4 h-4" />;
      case 'snapscan':
      case 'zapper':
        return <Package className="w-4 h-4" />;
      case 'eft':
        return <CreditCard className="w-4 h-4" />;
      case 'cash_on_delivery':
        return <ShoppingCart className="w-4 h-4" />;
      default:
        return <CreditCard className="w-4 h-4" />;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-ZA', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-ZA', {
      style: 'currency',
      currency: 'ZAR'
    }).format(amount);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="mx-auto h-12 w-12 text-red-500" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">Error loading orders</h3>
        <p className="mt-1 text-sm text-gray-500">Please try again later.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Orders</h1>
          <p className="text-gray-600">Manage and track student marketplace orders</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <Filter className="w-4 h-4 mr-2" />
            Filters
          </button>
          <button
            onClick={() => {/* TODO: Export orders */}}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <Download className="w-4 h-4 mr-2" />
            Export
          </button>
        </div>
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="bg-white p-6 rounded-lg shadow border">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
              <div className="relative">
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Search orders..."
                  className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <Search className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <select
                value={filters.status || ''}
                onChange={(e) => handleFilterChange('status', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="confirmed">Confirmed</option>
                <option value="shipped">Shipped</option>
                <option value="delivered">Delivered</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Date From</label>
              <input
                type="date"
                value={filters.date_from || ''}
                onChange={(e) => handleFilterChange('date_from', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Date To</label>
              <input
                type="date"
                value={filters.date_to || ''}
                onChange={(e) => handleFilterChange('date_to', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          <div className="flex justify-end space-x-3 mt-4">
            <button
              onClick={clearFilters}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200"
            >
              Clear
            </button>
            <button
              onClick={handleSearch}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700"
            >
              Apply Filters
            </button>
          </div>
        </div>
      )}

      {/* Orders Table */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-medium text-gray-900">
              Orders ({ordersData?.total || 0})
            </h3>
            <div className="text-sm text-gray-500">
              Page {page} of {ordersData?.total_pages || 1}
            </div>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Order ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Customer
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Items
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Total
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Payment
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {ordersData?.data.map((order) => (
                <tr key={order.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">#{order.id}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10">
                        {order.buyer.profile_img ? (
                          <img
                            className="h-10 w-10 rounded-full"
                            src={normalizeImageUrl(order.buyer.profile_img)}
                            alt=""
                            onError={(e) => {
                              const target = e.target as HTMLImageElement;
                              target.style.display = 'none';
                              // Show fallback user icon
                              const parent = target.parentElement;
                              if (parent) {
                                parent.innerHTML = '<div class="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center"><svg class="h-5 w-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg></div>';
                              }
                            }}
                          />
                        ) : (
                          <div className="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                            <User className="h-5 w-5 text-gray-500" />
                          </div>
                        )}
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">
                          {order.buyer.name} {order.buyer.surname}
                        </div>
                        <div className="text-sm text-gray-500">{order.buyer.email}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{order.items.length} items</div>
                    <div className="text-sm text-gray-500">
                      {order.items.slice(0, 2).map(item => item.product.title).join(', ')}
                      {order.items.length > 2 && '...'}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      {formatCurrency(order.total_amount)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      {getPaymentMethodIcon(order.payment_method)}
                      <span className="ml-2 text-sm text-gray-900 capitalize">
                        {order.payment_method.replace('_', ' ')}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <select
                      value={order.status}
                      onChange={(e) => handleStatusUpdate(order.id, e.target.value)}
                      className={`text-sm px-2 py-1 rounded-full border ${getStatusColor(order.status)}`}
                    >
                      <option value="pending">Pending</option>
                      <option value="confirmed">Confirmed</option>
                      <option value="shipped">Shipped</option>
                      <option value="delivered">Delivered</option>
                      <option value="cancelled">Cancelled</option>
                    </select>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{formatDate(order.created_at)}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      onClick={() => setSelectedOrder(order)}
                      className="text-blue-600 hover:text-blue-900 mr-3"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => {/* TODO: Edit order */}}
                      className="text-gray-600 hover:text-gray-900"
                    >
                      <Edit3 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {ordersData && ordersData.total_pages > 1 && (
          <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
            <div className="flex-1 flex justify-between sm:hidden">
              <button
                onClick={() => setPage(page - 1)}
                disabled={page === 1}
                className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
              >
                Previous
              </button>
              <button
                onClick={() => setPage(page + 1)}
                disabled={page === ordersData.total_pages}
                className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
              >
                Next
              </button>
            </div>
            <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-gray-700">
                  Showing{' '}
                  <span className="font-medium">{(page - 1) * limit + 1}</span>
                  {' '}to{' '}
                  <span className="font-medium">
                    {Math.min(page * limit, ordersData.total)}
                  </span>
                  {' '}of{' '}
                  <span className="font-medium">{ordersData.total}</span>
                  {' '}results
                </p>
              </div>
              <div>
                <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                  <button
                    onClick={() => setPage(page - 1)}
                    disabled={page === 1}
                    className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                  >
                    Previous
                  </button>
                  {Array.from({ length: ordersData.total_pages }, (_, i) => i + 1).map((pageNum) => (
                    <button
                      key={pageNum}
                      onClick={() => setPage(pageNum)}
                      className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                        pageNum === page
                          ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                          : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                      }`}
                    >
                      {pageNum}
                    </button>
                  ))}
                  <button
                    onClick={() => setPage(page + 1)}
                    disabled={page === ordersData.total_pages}
                    className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                  >
                    Next
                  </button>
                </nav>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Order Details Modal */}
      {selectedOrder && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium text-gray-900">
                  Order #{selectedOrder.id} Details
                </h3>
                <button
                  onClick={() => setSelectedOrder(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XCircle className="w-6 h-6" />
                </button>
              </div>

              <div className="space-y-6">
                {/* Customer Information */}
                <div>
                  <h4 className="text-md font-medium text-gray-900 mb-3">Customer Information</h4>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm text-gray-500">Name</p>
                        <p className="text-sm font-medium">{selectedOrder.buyer.name} {selectedOrder.buyer.surname}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Email</p>
                        <p className="text-sm font-medium">{selectedOrder.buyer.email}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Phone</p>
                        <p className="text-sm font-medium">{selectedOrder.buyer.phone || 'N/A'}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Username</p>
                        <p className="text-sm font-medium">{selectedOrder.buyer.username}</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Order Items */}
                <div>
                  <h4 className="text-md font-medium text-gray-900 mb-3">Order Items</h4>
                  <div className="space-y-3">
                    {selectedOrder.items.map((item) => (
                      <div key={item.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <div className="w-12 h-12 bg-gray-200 rounded-lg flex items-center justify-center">
                            {item.product.images && item.product.images.length > 0 ? (
                              <img
                                src={normalizeImageUrl(item.product.images[0])}
                                alt={item.product.title}
                                className="w-12 h-12 rounded-lg object-cover"
                                onError={(e) => {
                                  const target = e.target as HTMLImageElement;
                                  target.style.display = 'none';
                                }}
                              />
                            ) : (
                              <Package className="w-6 h-6 text-gray-400" />
                            )}
                          </div>
                          <div>
                            <p className="text-sm font-medium">{item.product.title}</p>
                            <p className="text-sm text-gray-500">Qty: {item.quantity}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-medium">{formatCurrency(item.price)}</p>
                          <p className="text-sm text-gray-500">Total: {formatCurrency(item.price * item.quantity)}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Order Summary */}
                <div>
                  <h4 className="text-md font-medium text-gray-900 mb-3">Order Summary</h4>
                  <div className="bg-gray-50 p-4 rounded-lg space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-500">Payment Method:</span>
                      <span className="text-sm font-medium capitalize">{selectedOrder.payment_method.replace('_', ' ')}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-500">Status:</span>
                      <span className={`text-sm px-2 py-1 rounded-full border ${getStatusColor(selectedOrder.status)}`}>
                        {selectedOrder.status}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-500">Order Date:</span>
                      <span className="text-sm font-medium">{formatDate(selectedOrder.created_at)}</span>
                    </div>
                    <div className="flex justify-between border-t pt-2">
                      <span className="text-sm font-medium">Total Amount:</span>
                      <span className="text-lg font-bold text-gray-900">{formatCurrency(selectedOrder.total_amount)}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex justify-end space-x-3 mt-6">
                <button
                  onClick={() => setSelectedOrder(null)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200"
                >
                  Close
                </button>
                <button
                  onClick={() => {/* TODO: Print order */}}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700"
                >
                  Print Order
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default OrdersPage;

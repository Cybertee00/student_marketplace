import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  Package, 
  AlertTriangle, 
  TrendingUp, 
  TrendingDown, 
  Edit, 
  Plus, 
  Minus, 
  Eye,
  RefreshCw,
  Filter
} from 'lucide-react';
import { apiService } from '@/services/api';
import { Product, InventorySummary, InventoryLog, StockUpdateRequest } from '@/types';
import { toast } from 'react-hot-toast';
import LoadingSpinner from '@/components/LoadingSpinner';

interface StockUpdateModalProps {
  product: Product;
  operation: 'update' | 'add' | 'remove';
  onClose: () => void;
  onSuccess: () => void;
}

const StockUpdateModal: React.FC<StockUpdateModalProps> = ({ 
  product, 
  operation, 
  onClose, 
  onSuccess 
}) => {
  const [quantity, setQuantity] = useState('');
  const [reason, setReason] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const queryClient = useQueryClient();

  const getOperationInfo = () => {
    switch (operation) {
      case 'update':
        return { title: 'Update Stock', action: 'Update', icon: Edit };
      case 'add':
        return { title: 'Add Stock', action: 'Add', icon: Plus };
      case 'remove':
        return { title: 'Remove Stock', action: 'Remove', icon: Minus };
    }
  };

  const { title, action, icon: Icon } = getOperationInfo();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!quantity || parseInt(quantity) <= 0) {
      toast.error('Please enter a valid quantity');
      return;
    }

    setIsSubmitting(true);
    try {
      const data: StockUpdateRequest = {
        stock_quantity: parseInt(quantity),
        reason: reason || undefined
      };

      let response;
      switch (operation) {
        case 'update':
          response = await apiService.updateProductStock(product.id, data);
          break;
        case 'add':
          response = await apiService.addProductStock(product.id, data);
          break;
        case 'remove':
          response = await apiService.removeProductStock(product.id, data);
          break;
      }

      if (response.success) {
        toast.success(`Stock ${action.toLowerCase()}ed successfully`);
        queryClient.invalidateQueries({ queryKey: ['products'] });
        queryClient.invalidateQueries({ queryKey: ['inventory'] });
        onSuccess();
        onClose();
      } else {
        toast.error(response.message || 'Failed to update stock');
      }
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to update stock');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <div className="flex items-center gap-2 mb-4">
          <Icon className="w-5 h-5 text-blue-600" />
          <h2 className="text-xl font-semibold">{title}</h2>
        </div>

        <div className="mb-4">
          <p className="text-sm text-gray-600 mb-2">Product: {product.title}</p>
          <p className="text-sm text-gray-600">Current Stock: {product.inventory?.stock_quantity || 0}</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Quantity to {action.toLowerCase()}
            </label>
            <input
              type="number"
              min="1"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder={`Enter quantity to ${action.toLowerCase()}`}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Reason (optional)
            </label>
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., Restock, Damaged items, etc."
              rows={3}
            />
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {isSubmitting ? 'Updating...' : action}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

interface InventoryLogsModalProps {
  product: Product;
  onClose: () => void;
}

const InventoryLogsModal: React.FC<InventoryLogsModalProps> = ({ product, onClose }) => {
  const { data: logs, isLoading } = useQuery({
    queryKey: ['inventory-logs', product.id],
    queryFn: () => apiService.getProductInventoryLogs(product.id, 100, 0),
    enabled: !!product.id
  });

  const formatChangeType = (type: string) => {
    return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const getChangeColor = (quantity: number) => {
    return quantity > 0 ? 'text-green-600' : 'text-red-600';
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[80vh] overflow-hidden flex flex-col">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Inventory History - {product.title}</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>

        <div className="flex-1 overflow-y-auto">
          {isLoading ? (
            <LoadingSpinner />
          ) : logs && logs.length > 0 ? (
            <div className="space-y-3">
              {logs.map((log) => (
                <div key={log.id} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium">{formatChangeType(log.change_type)}</span>
                    <span className={`font-semibold ${getChangeColor(log.quantity_changed)}`}>
                      {log.quantity_changed > 0 ? '+' : ''}{log.quantity_changed}
                    </span>
                  </div>
                  <div className="text-sm text-gray-600 space-y-1">
                    <p>Previous: {log.previous_stock} → New: {log.new_stock}</p>
                    {log.reason && <p>Reason: {log.reason}</p>}
                    <p>Date: {new Date(log.created_at).toLocaleString()}</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">No inventory history found</p>
          )}
        </div>
      </div>
    </div>
  );
};

const InventoryPage: React.FC = () => {
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [modalType, setModalType] = useState<'stock' | 'logs' | null>(null);
  const [stockOperation, setStockOperation] = useState<'update' | 'add' | 'remove'>('update');
  const [filter, setFilter] = useState<'all' | 'low-stock' | 'out-of-stock'>('all');

  const queryClient = useQueryClient();

  // Fetch products with inventory data (admin products only)
  const { data: productsData, isLoading: productsLoading } = useQuery({
    queryKey: ['products', { inventory: true, admin_only: true }],
    queryFn: () => apiService.getProducts({ created_via: 'admin_web' }, 1, 1000),
  });

  // Fetch low stock products
  const { data: lowStockData } = useQuery({
    queryKey: ['low-stock-products'],
    queryFn: () => apiService.getLowStockProducts(100),
  });

  // Fetch out of stock products
  const { data: outOfStockData } = useQuery({
    queryKey: ['out-of-stock-products'],
    queryFn: () => apiService.getOutOfStockProducts(100),
  });

  // Log inventory data to verify it only shows admin products
  useEffect(() => {
    if (productsData) {
      console.log('Inventory products data received:');
      console.log('Total products:', productsData?.data?.length);
      if (productsData?.data) {
        console.log('Products created_via:', productsData.data.map((p: any) => ({ 
          id: p.id, 
          title: p.title, 
          created_via: p.created_via 
        })));
      }
    }
  }, [productsData]);

  const getFilteredProducts = () => {
    if (!productsData?.data) return [];
    
    switch (filter) {
      case 'low-stock':
        return productsData.data.filter(p => 
          p.inventory && p.inventory.stock_quantity <= p.inventory.low_stock_threshold && p.inventory.stock_quantity > 0
        );
      case 'out-of-stock':
        return productsData.data.filter(p => 
          p.inventory && p.inventory.is_out_of_stock
        );
      default:
        return productsData.data;
    }
  };

  const openStockModal = (product: Product, operation: 'update' | 'add' | 'remove') => {
    setSelectedProduct(product);
    setStockOperation(operation);
    setModalType('stock');
  };

  const openLogsModal = (product: Product) => {
    setSelectedProduct(product);
    setModalType('logs');
  };

  const closeModal = () => {
    setSelectedProduct(null);
    setModalType(null);
  };

  const getStockStatus = (product: Product) => {
    if (!product.inventory) return { status: 'No Data', color: 'text-gray-500' };
    
    const { stock_quantity, low_stock_threshold, is_out_of_stock } = product.inventory;
    
    if (is_out_of_stock) return { status: 'Out of Stock', color: 'text-red-600' };
    if (stock_quantity <= low_stock_threshold) return { status: 'Low Stock', color: 'text-orange-600' };
    return { status: 'In Stock', color: 'text-green-600' };
  };

  const getStockPercentage = (product: Product) => {
    if (!product.inventory || product.inventory.initial_stock === 0) return 0;
    return Math.round((product.inventory.stock_quantity / product.inventory.initial_stock) * 100);
  };

  if (productsLoading) {
    return <LoadingSpinner />;
  }

  const filteredProducts = getFilteredProducts();

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Inventory Management</h1>
        <p className="text-gray-600">Manage product stock levels and track inventory changes</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center">
            <Package className="w-8 h-8 text-blue-600" />
            <div className="ml-3">
              <p className="text-sm text-gray-600">Total Products</p>
              <p className="text-xl font-semibold">{productsData?.data?.length || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center">
            <AlertTriangle className="w-8 h-8 text-orange-600" />
            <div className="ml-3">
              <p className="text-sm text-gray-600">Low Stock</p>
              <p className="text-xl font-semibold">{lowStockData?.total || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center">
            <TrendingDown className="w-8 h-8 text-red-600" />
            <div className="ml-3">
              <p className="text-sm text-gray-600">Out of Stock</p>
              <p className="text-xl font-semibold">{outOfStockData?.total || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center">
            <TrendingUp className="w-8 h-8 text-green-600" />
            <div className="ml-3">
              <p className="text-sm text-gray-600">In Stock</p>
              <p className="text-xl font-semibold">
                {(productsData?.data?.length || 0) - (outOfStockData?.total || 0)}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="flex items-center gap-4">
          <Filter className="w-5 h-5 text-gray-500" />
          <div className="flex gap-2">
            <button
              onClick={() => setFilter('all')}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                filter === 'all' 
                  ? 'bg-blue-100 text-blue-700' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              All Products
            </button>
            <button
              onClick={() => setFilter('low-stock')}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                filter === 'low-stock' 
                  ? 'bg-orange-100 text-orange-700' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Low Stock
            </button>
            <button
              onClick={() => setFilter('out-of-stock')}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                filter === 'out-of-stock' 
                  ? 'bg-red-100 text-red-700' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Out of Stock
            </button>
          </div>
        </div>
      </div>

      {/* Products Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Product
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Current Stock
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Sold
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Stock %
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredProducts.map((product) => {
                const stockStatus = getStockStatus(product);
                const stockPercentage = getStockPercentage(product);
                
                return (
                  <tr key={product.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{product.title}</div>
                        <div className="text-sm text-gray-500">{product.category}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900">
                        {product.inventory?.stock_quantity || 0}
                      </div>
                      <div className="text-xs text-gray-500">
                        Threshold: {product.inventory?.low_stock_threshold || 5}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900">
                        {product.inventory?.sold_quantity || 0}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${stockStatus.color}`}>
                        {stockStatus.status}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <div className="w-12 bg-gray-200 rounded-full h-1.5 mr-2">
                          <div 
                            className="bg-blue-600 h-1.5 rounded-full" 
                            style={{ width: `${stockPercentage}%` }}
                          ></div>
                        </div>
                        <span className="text-xs text-gray-600">{stockPercentage}%</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => openStockModal(product, 'update')}
                          className="text-blue-600 hover:text-blue-900 text-sm font-medium"
                        >
                          <Edit className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => openStockModal(product, 'add')}
                          className="text-green-600 hover:text-green-900 text-sm font-medium"
                        >
                          <Plus className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => openStockModal(product, 'remove')}
                          className="text-red-600 hover:text-red-900 text-sm font-medium"
                        >
                          <Minus className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => openLogsModal(product)}
                          className="text-gray-600 hover:text-gray-900 text-sm font-medium"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {filteredProducts.length === 0 && (
          <div className="text-center py-8">
            <Package className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No products found</p>
          </div>
        )}
      </div>

      {/* Modals */}
      {modalType === 'stock' && selectedProduct && (
        <StockUpdateModal
          product={selectedProduct}
          operation={stockOperation}
          onClose={closeModal}
          onSuccess={() => {
            queryClient.invalidateQueries({ queryKey: ['products'] });
            queryClient.invalidateQueries({ queryKey: ['low-stock-products'] });
            queryClient.invalidateQueries({ queryKey: ['out-of-stock-products'] });
          }}
        />
      )}

      {modalType === 'logs' && selectedProduct && (
        <InventoryLogsModal
          product={selectedProduct}
          onClose={closeModal}
        />
      )}
    </div>
  );
};

export default InventoryPage;

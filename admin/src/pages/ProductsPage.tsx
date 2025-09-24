import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Search, Plus, Eye, Edit, Check, X, Trash2, ToggleLeft, ToggleRight, Store, Users } from 'lucide-react';
import { apiService } from '@/services/api';
import { Product, ProductFilters } from '@/types';
import { toast } from 'react-hot-toast';
import LoadingSpinner from '@/components/LoadingSpinner';

interface EditProductFormProps {
  product: Product;
  onSubmit: (data: Partial<Product>) => void;
  onCancel: () => void;
}

interface AddProductFormProps {
  onSubmit: (data: Partial<Product>) => void;
  onCancel: () => void;
}

const AddProductForm: React.FC<AddProductFormProps> = ({ onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    price: 0,
    category: 'Electronics',
    faculty: '',
    approved: true,
    discontinued: false,
    images: [] as string[],
    stock_quantity: 0,
    low_stock_threshold: 5
  });
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [uploadingImages, setUploadingImages] = useState(false);

  // Reset form function
  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      price: 0,
      category: 'Electronics',
      faculty: '',
      approved: true,
      discontinued: false,
      images: [] as string[],
      stock_quantity: 0,
      low_stock_threshold: 5
    });
    setSelectedFiles([]);
    setUploadingImages(false);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    setSelectedFiles(prev => [...prev, ...files]);
  };

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Prevent multiple submissions
    if (uploadingImages) {
      return;
    }
    
    setUploadingImages(true);
    
    try {
      let finalImages: string[] = [];
      
      // Upload images first if any are selected
      if (selectedFiles.length > 0) {
        console.log(`Uploading ${selectedFiles.length} images...`);
        
        const uploadPromises = selectedFiles.map(async (file) => {
          try {
            console.log(`Attempting to upload: ${file.name} (${file.size} bytes)`);
            const response = await apiService.uploadImage(file);
            console.log('Upload response:', response);
            
            if (response.success && response.data) {
              const imageUrl = `http://localhost:8000/images/${response.data.filename}`;
              console.log(`Successfully uploaded: ${imageUrl}`);
              return imageUrl;
            } else {
              console.error('Upload response not successful:', response);
              console.error('Response details:', JSON.stringify(response, null, 2));
              throw new Error(`Upload failed: ${response.message || 'Unknown error'}`);
            }
          } catch (error: any) {
            console.error('Error uploading file:', file.name, error);
            if (error.response) {
              console.error('Error response:', error.response.data);
              console.error('Error status:', error.response.status);
            }
            throw error;
          }
        });
        
        // Wait for all uploads to complete
        const uploadedUrls = await Promise.all(uploadPromises);
        finalImages = [...finalImages, ...uploadedUrls];
        console.log(`All images uploaded successfully:`, finalImages);
      }
      
      // Prepare final product data
      const finalProductData = {
        ...formData,
        images: finalImages
      };
      
      console.log('Submitting product with images:', finalProductData);
      
      // Submit the product data
      onSubmit(finalProductData);
      
      // Reset form after successful submission
      resetForm();
      
    } catch (error) {
      console.error('Error in handleSubmit:', error);
      toast.error('Failed to upload images. Please try again.');
    } finally {
      setUploadingImages(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700">Title</label>
        <input
          type="text"
          value={formData.title}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          required
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700">Description</label>
        <textarea
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          rows={3}
          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          required
        />
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Price</label>
          <input
            type="number"
            step="0.01"
            min="0"
            value={formData.price}
            onChange={(e) => setFormData({ ...formData, price: parseFloat(e.target.value) || 0 })}
            className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Category</label>
          <select
            value={formData.category}
            onChange={(e) => setFormData({ ...formData, category: e.target.value })}
            className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          >
            <option value="Electronics">Electronics</option>
            <option value="Books">Books</option>
            <option value="Clothing">Clothing</option>
            <option value="Furniture">Furniture</option>
            <option value="Appliances">Appliances</option>
            <option value="Sports">Sports</option>
            <option value="Beauty">Beauty</option>
            <option value="Other">Other</option>
          </select>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Faculty</label>
        <select
          value={formData.faculty}
          onChange={(e) => setFormData({ ...formData, faculty: e.target.value })}
          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Faculties</option>
          <option value="humanities">Humanities</option>
          <option value="health_environmental">Health and Environmental Science</option>
          <option value="FEBIT">FEBIT</option>
          <option value="management_science">Management Science</option>
        </select>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Initial Stock Quantity</label>
          <input
            type="number"
            min="0"
            value={formData.stock_quantity}
            onChange={(e) => setFormData({ ...formData, stock_quantity: parseInt(e.target.value) || 0 })}
            className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="How many units available"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Low Stock Threshold</label>
          <input
            type="number"
            min="0"
            value={formData.low_stock_threshold}
            onChange={(e) => setFormData({ ...formData, low_stock_threshold: parseInt(e.target.value) || 5 })}
            className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Alert when stock goes below this number"
            required
          />
        </div>
      </div>


      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Product Images</label>
        <div className="space-y-4">
          <div>
            <input
              type="file"
              multiple
              accept="image/*"
              onChange={handleFileSelect}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
          </div>
          
          {selectedFiles.length > 0 && (
            <div className="grid grid-cols-2 gap-4">
              {selectedFiles.map((file, index) => (
                <div key={index} className="relative">
                  <img
                    src={URL.createObjectURL(file)}
                    alt={`Preview ${index + 1}`}
                    className="w-full h-32 object-cover rounded-lg"
                  />
                  <button
                    type="button"
                    onClick={() => removeFile(index)}
                    className="absolute top-2 right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs hover:bg-red-600"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
      
      <div>
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={formData.approved}
            onChange={(e) => setFormData({ ...formData, approved: e.target.checked })}
            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <span className="ml-2 text-sm text-gray-700">Approved</span>
        </label>
      </div>
      
      <div className="flex justify-end space-x-3 pt-4">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={uploadingImages}
          className="px-4 py-2 bg-blue-600 border border-transparent rounded-md text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {uploadingImages ? 'Uploading Images...' : 'Create Product'}
        </button>
      </div>
    </form>
  );
};

const EditProductForm: React.FC<EditProductFormProps> = ({ product, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    title: product.title,
    description: product.description,
    price: product.price,
    category: product.category,
    faculty: product.faculty || '',
    approved: product.status === 'approved',
    stock_quantity: product.inventory?.stock_quantity || 0,
    low_stock_threshold: product.inventory?.low_stock_threshold || 5
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700">Title</label>
        <input
          type="text"
          value={formData.title}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          required
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700">Description</label>
        <textarea
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          rows={3}
          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          required
        />
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Price</label>
          <input
            type="number"
            step="0.01"
            value={formData.price}
            onChange={(e) => setFormData({ ...formData, price: parseFloat(e.target.value) })}
            className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Category</label>
          <select
            value={formData.category}
            onChange={(e) => setFormData({ ...formData, category: e.target.value })}
            className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          >
            <option value="Electronics">Electronics</option>
            <option value="Books">Books</option>
            <option value="Clothing">Clothing</option>
            <option value="Furniture">Furniture</option>
            <option value="Appliances">Appliances</option>
            <option value="Sports">Sports</option>
            <option value="Beauty">Beauty</option>
            <option value="Other">Other</option>
          </select>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Faculty</label>
        <select
          value={formData.faculty}
          onChange={(e) => setFormData({ ...formData, faculty: e.target.value })}
          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Faculties</option>
          <option value="humanities">Humanities</option>
          <option value="health_environmental">Health and Environmental Science</option>
          <option value="FEBIT">FEBIT</option>
          <option value="management_science">Management Science</option>
        </select>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Stock Quantity</label>
          <input
            type="number"
            min="0"
            value={formData.stock_quantity}
            onChange={(e) => setFormData({ ...formData, stock_quantity: parseInt(e.target.value) || 0 })}
            className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Current stock available"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Low Stock Threshold</label>
          <input
            type="number"
            min="0"
            value={formData.low_stock_threshold}
            onChange={(e) => setFormData({ ...formData, low_stock_threshold: parseInt(e.target.value) || 5 })}
            className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Alert when stock goes below this number"
            required
          />
        </div>
      </div>
      
      <div>
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={formData.approved}
            onChange={(e) => setFormData({ ...formData, approved: e.target.checked })}
            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <span className="ml-2 text-sm text-gray-700">Approved</span>
        </label>
      </div>
      
      <div className="flex justify-end space-x-3 pt-4">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          Cancel
        </button>
        <button
          type="submit"
          className="px-4 py-2 bg-blue-600 border border-transparent rounded-md text-sm font-medium text-white hover:bg-blue-700"
        >
          Update Product
        </button>
      </div>
    </form>
  );
};

const ProductsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'admin' | 'enduser'>('admin');
  
  // Function to handle tab change with cache invalidation
  const handleTabChange = (tab: 'admin' | 'enduser') => {
    setActiveTab(tab);
    setCurrentPage(1); // Reset to first page
    // Reset filters when switching tabs
    setFilters({});
    setSearchTerm('');
    // Invalidate cache to ensure fresh data
    queryClient.invalidateQueries({ queryKey: ['products'] });
  };
  const [filters, setFilters] = useState<ProductFilters>({});
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [isViewModalOpen, setIsViewModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [isImageModalOpen, setIsImageModalOpen] = useState(false);
  const queryClient = useQueryClient();

  const { data: productsData, isLoading } = useQuery({
    queryKey: ['products', filters, currentPage, activeTab],
    queryFn: () => {
      const tabFilters = {
        ...filters,
        created_via: activeTab === 'admin' ? 'admin_web' : 'flutter'
      };
      console.log('Fetching products with filters:', tabFilters);
      console.log('Active tab:', activeTab);
      return apiService.getProducts(tabFilters, currentPage, 10);
    },
    placeholderData: (previousData) => previousData,
  });

  // Log data when it changes
  useEffect(() => {
    if (productsData) {
      console.log('Products data received for tab:', activeTab);
      console.log('Products count:', productsData?.data?.length);
      if (productsData?.data) {
        console.log('First product created_via:', productsData.data[0]?.created_via);
        console.log('All products created_via:', productsData.data.map((p: any) => ({ id: p.id, title: p.title, created_via: p.created_via })));
      }
    }
  }, [productsData, activeTab]);

  const approveMutation = useMutation({
    mutationFn: (id: number) => apiService.approveProduct(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
      toast.success('Product approved successfully');
    },
    onError: () => {
      toast.error('Failed to approve product');
    },
  });

  const rejectMutation = useMutation({
    mutationFn: (id: number) => apiService.rejectProduct(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
      toast.success('Product rejected');
    },
    onError: () => {
      toast.error('Failed to reject product');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => apiService.deleteProduct(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
      toast.success('Product deleted successfully');
    },
    onError: () => {
      toast.error('Failed to delete product');
    },
  });

  const discontinueMutation = useMutation({
    mutationFn: ({ id, discontinued, reason }: { id: number; discontinued: boolean; reason?: string }) => 
      apiService.discontinueProduct(id, discontinued, reason),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
      const action = variables.discontinued ? 'discontinued' : 're-enabled';
      toast.success(`Product ${action} successfully`);
    },
    onError: () => {
      toast.error('Failed to update product status');
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Product> }) => apiService.updateProduct(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
      toast.success('Product updated successfully');
    },
    onError: () => {
      toast.error('Failed to update product');
    },
  });

  const createMutation = useMutation({
    mutationFn: (data: Partial<Product>) => apiService.createProduct(data as any),
    onSuccess: (response: any) => {
      console.log('Product created successfully:', response);
      queryClient.invalidateQueries({ queryKey: ['products'] });
      toast.success('Product created successfully');
      setIsAddModalOpen(false);
    },
    onError: (error) => {
      console.error('Failed to create product:', error);
      toast.error('Failed to create product. Please try again.');
    },
  });

  const handleSearch = (value: string) => {
    setSearchTerm(value);
    setFilters(prev => ({ ...prev, search: value }));
    setCurrentPage(1);
  };


  const handleFilterChange = (key: keyof ProductFilters, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setCurrentPage(1);
  };

  const handleApprove = (id: number) => {
    if (confirm('Are you sure you want to approve this product?')) {
      approveMutation.mutate(id);
    }
  };

  const handleReject = (id: number) => {
    if (confirm('Are you sure you want to reject this product?')) {
      rejectMutation.mutate(id);
    }
  };

  const handleDelete = (id: number) => {
    if (confirm('Are you sure you want to delete this product? This action cannot be undone.')) {
      deleteMutation.mutate(id);
    }
  };

  const handleDiscontinue = (id: number, discontinued: boolean) => {
    const action = discontinued ? 'discontinue' : 're-enable';
    const reason = prompt(`Reason for ${action}ing this product (optional):`);
    if (confirm(`Are you sure you want to ${action} this product?`)) {
      discontinueMutation.mutate({ id, discontinued, reason: reason || undefined });
    }
  };

  const handleView = (product: Product) => {
    setSelectedProduct(product);
    setIsViewModalOpen(true);
  };

  const handleEdit = (product: Product) => {
    setSelectedProduct(product);
    setIsEditModalOpen(true);
  };

  const handleUpdateProduct = (updatedData: Partial<Product>) => {
    if (selectedProduct) {
      console.log('Updating product with data:', updatedData);
      console.log('Product ID:', selectedProduct.id);
      updateMutation.mutate({ id: selectedProduct.id, data: updatedData });
      setIsEditModalOpen(false);
      setSelectedProduct(null);
    }
  };

  const handleCreateProduct = (newProduct: Partial<Product>) => {
    createMutation.mutate(newProduct);
  };

  const getStatusBadge = (product: Product) => {
    if (activeTab === 'admin') {
      // For admin products, show general status
      const status = product.status || 'approved';
      const statusConfig = {
        pending: { color: 'bg-warning-100 text-warning-800', text: 'Pending' },
        approved: { color: 'bg-success-100 text-success-800', text: 'Active' },
        rejected: { color: 'bg-danger-100 text-danger-800', text: 'Rejected' },
        sold: { color: 'bg-secondary-100 text-secondary-800', text: 'Sold' },
      };
      const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.approved;
      return (
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.color}`}>
          {config.text}
        </span>
      );
    } else {
      // For end-user products, show approval status
      const isApproved = product.approved;
      const statusConfig = isApproved 
        ? { color: 'bg-success-100 text-success-800', text: 'Approved' }
        : { color: 'bg-warning-100 text-warning-800', text: 'Pending Approval' };
      
      return (
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusConfig.color}`}>
          {statusConfig.text}
        </span>
      );
    }
  };

  if (isLoading) {
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
          <h1 className="text-2xl font-semibold text-secondary-900">Products</h1>
          <p className="text-secondary-600">Manage and moderate student marketplace products</p>
        </div>
        {activeTab === 'admin' && (
          <button
            onClick={() => setIsAddModalOpen(true)}
            className="btn btn-primary whitespace-nowrap min-w-fit px-4 py-2"
          >
            <Plus className="h-4 w-4 mr-2 flex-shrink-0" />
            <span>Add Product</span>
          </button>
        )}
      </div>

      {/* Product Type Tabs */}
      <div className="card">
        <div className="card-content p-0">
          <div className="border-b border-secondary-200">
            <nav className="-mb-px flex space-x-8 px-6" aria-label="Tabs">
              <button
                onClick={() => handleTabChange('admin')}
                className={`${
                  activeTab === 'admin'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-secondary-500 hover:text-secondary-700 hover:border-secondary-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2`}
              >
                <Store className="h-4 w-4" />
                Student Marketplace
                <span className="ml-2 bg-secondary-100 text-secondary-600 py-0.5 px-2.5 rounded-full text-xs">
                  Admin Products
                </span>
              </button>
              <button
                onClick={() => handleTabChange('enduser')}
                className={`${
                  activeTab === 'enduser'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-secondary-500 hover:text-secondary-700 hover:border-secondary-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2`}
              >
                <Users className="h-4 w-4" />
                Market Page
                <span className="ml-2 bg-secondary-100 text-secondary-600 py-0.5 px-2.5 rounded-full text-xs">
                  End-User Products
                </span>
              </button>
            </nav>
          </div>
          
          {/* Tab Description */}
          <div className="px-6 py-4 bg-secondary-50 border-b border-secondary-200">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3">
                {activeTab === 'admin' ? (
                  <>
                    <div className="flex-shrink-0">
                      <Store className="h-5 w-5 text-primary-600" />
                    </div>
                    <div>
                      <h3 className="text-sm font-medium text-secondary-900">Student Marketplace Products</h3>
                      <p className="text-sm text-secondary-600 mt-1">
                        Products uploaded by administrators that appear on the Home page (Student Marketplace). 
                        These products are immediately visible to all users.
                      </p>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="flex-shrink-0">
                      <Users className="h-5 w-5 text-primary-600" />
                    </div>
                    <div>
                      <h3 className="text-sm font-medium text-secondary-900">Market Page Products</h3>
                      <p className="text-sm text-secondary-600 mt-1">
                        Products uploaded by end-users through the Flutter app that appear on the Market page. 
                        These products require admin approval before becoming visible to users.
                      </p>
                    </div>
                  </>
                )}
              </div>
              {productsData && (
                <div className="flex-shrink-0">
                  <div className="text-right">
                    <div className="text-2xl font-bold text-secondary-900">
                      {productsData.total}
                    </div>
                    <div className="text-xs text-secondary-500">
                      {activeTab === 'admin' ? 'Admin Products' : 'End-User Products'}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="card-content">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-secondary-400" />
              <input
                type="text"
                placeholder="Search products..."
                value={searchTerm}
                onChange={(e) => handleSearch(e.target.value)}
                className="input pl-10"
              />
            </div>

            {/* Category filter */}
            <select
              value={filters.category || ''}
              onChange={(e) => handleFilterChange('category', e.target.value)}
              className="input"
            >
              <option value="">All Categories</option>
              <option value="electronics">Electronics</option>
              <option value="books">Books</option>
              <option value="clothing">Clothing</option>
              <option value="furniture">Furniture</option>
              <option value="sports">Sports</option>
            </select>

            {/* Status filter */}
            <select
              value={filters.status || ''}
              onChange={(e) => handleFilterChange('status', e.target.value)}
              className="input"
            >
              <option value="">All Status</option>
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
              <option value="sold">Sold</option>
            </select>

            {/* Discontinued filter */}
            <select
              value={filters.discontinued === undefined ? '' : filters.discontinued.toString()}
              onChange={(e) => {
                const value = e.target.value;
                if (value === '') {
                  setFilters(prev => ({ ...prev, discontinued: undefined }));
                } else {
                  setFilters(prev => ({ ...prev, discontinued: value === 'true' }));
                }
                setCurrentPage(1);
              }}
              className="input"
            >
              <option value="">All Products</option>
              <option value="false">Active</option>
              <option value="true">Discontinued</option>
            </select>

            {/* Price range */}
            <div className="flex gap-2">
              <input
                type="number"
                placeholder="Min price"
                value={filters.min_price || ''}
                onChange={(e) => handleFilterChange('min_price', e.target.value)}
                className="input"
              />
              <input
                type="number"
                placeholder="Max price"
                value={filters.max_price || ''}
                onChange={(e) => handleFilterChange('max_price', e.target.value)}
                className="input"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Products table */}
      <div className="card">
        <div className="card-content">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-secondary-200">
              <thead className="bg-secondary-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                    Product
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                    Seller
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                    Category
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                    Price
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                    Inventory
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                    {activeTab === 'admin' ? 'Status' : 'Approval Status'}
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                    Discontinued
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-secondary-200">
                {productsData?.data.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="px-6 py-12 text-center">
                      <div className="flex flex-col items-center">
                        {activeTab === 'admin' ? (
                          <Store className="h-12 w-12 text-secondary-400 mb-4" />
                        ) : (
                          <Users className="h-12 w-12 text-secondary-400 mb-4" />
                        )}
                        <h3 className="text-lg font-medium text-secondary-900 mb-2">
                          No {activeTab === 'admin' ? 'Admin' : 'End-User'} Products Found
                        </h3>
                        <p className="text-secondary-500 mb-4">
                          {activeTab === 'admin' 
                            ? 'No products have been uploaded by administrators yet. Click "Add Product" to create the first one.'
                            : 'No products have been uploaded by end-users yet, or all products have been processed.'
                          }
                        </p>
                        {activeTab === 'admin' && (
                          <button
                            onClick={() => setIsAddModalOpen(true)}
                            className="btn btn-primary"
                          >
                            <Plus className="h-4 w-4 mr-2" />
                            Add First Product
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ) : (
                  productsData?.data.map((product) => (
                    <tr key={product.id}>
                                         <td className="px-6 py-4 whitespace-nowrap">
                       <div className="flex items-center">
                         <div className="h-12 w-12 flex-shrink-0">
                           <img
                             className="h-12 w-12 rounded-lg object-cover border border-gray-200"
                             src={product.images && product.images.length > 0 ? product.images[0] : 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgdmlld0JveD0iMCAwIDEwMCAxMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiBmaWxsPSIjRjNGNEY2Ii8+CjxwYXRoIGQ9Ik0zMCAzNUg3MFY2NUgzMFYzNVoiIGZpbGw9IiNEMUQ1REIiLz4KPHBhdGggZD0iTTM1IDQwSDY1VjYwSDM1VjQwWiIgZmlsbD0iIzlDQTNBRiIvPgo8L3N2Zz4K'}
                             alt={product.title}
                             onError={(e) => {
                               const target = e.target as HTMLImageElement;
                               target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgdmlld0JveD0iMCAwIDEwMCAxMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiBmaWxsPSIjRjNGNEY2Ii8+CjxwYXRoIGQ9Ik0zMCAzNUg3MFY2NUgzMFYzNVoiIGZpbGw9IiNEMUQ1REIiLz4KPHBhdGggZD0iTTM1IDQwSDY1VjYwSDM1VjQwWiIgZmlsbD0iIzlDQTNBRiIvPgo8L3N2Zz4K';
                               target.alt = 'Image not available';
                             }}
                           />
                         </div>
                         <div className="ml-4">
                           <div className="flex items-center gap-2">
                             <div className="text-sm font-medium text-secondary-900">
                               {product.title}
                             </div>
                             <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium ${
                               product.created_via === 'admin_web' 
                                 ? 'bg-blue-100 text-blue-800' 
                                 : 'bg-purple-100 text-purple-800'
                             }`}>
                               {product.created_via === 'admin_web' ? 'Admin' : 'User'}
                             </span>
                           </div>
                           <div className="text-sm text-secondary-500">
                             {product.description.substring(0, 50)}...
                           </div>
                           {product.images && product.images.length > 0 && (
                             <div className="text-xs text-gray-400 mt-1">
                               {product.images.length} image{product.images.length !== 1 ? 's' : ''}
                             </div>
                           )}
                         </div>
                       </div>
                     </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-900">
                      {product.seller.name} {product.seller.surname}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-500">
                      {product.category}
                    </td>
                                         <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-900">
                       R{product.price}
                     </td>
                     <td className="px-6 py-4 whitespace-nowrap">
                       <div className="text-sm text-secondary-900">
                         <div className="flex items-center gap-2">
                           <span className="font-medium">
                             {product.inventory?.stock_quantity || 0}
                           </span>
                           <span className="text-xs text-secondary-500">in stock</span>
                         </div>
                         {product.inventory && (
                           <div className="text-xs text-secondary-500 mt-1">
                             Sold: {product.inventory.sold_quantity || 0}
                           </div>
                         )}
                         {product.inventory?.is_out_of_stock && (
                           <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800 mt-1">
                             Out of Stock
                           </span>
                         )}
                       </div>
                     </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getStatusBadge(product)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        product.discontinued 
                          ? 'bg-red-100 text-red-800' 
                          : 'bg-green-100 text-green-800'
                      }`}>
                        {product.discontinued ? 'Discontinued' : 'Active'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleView(product)}
                          className="text-primary-600 hover:text-primary-900"
                          title="View"
                        >
                          <Eye className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleEdit(product)}
                          className="text-secondary-600 hover:text-secondary-900"
                          title="Edit"
                        >
                          <Edit className="h-4 w-4" />
                        </button>
                        {/* Show approve/reject buttons based on active tab */}
                        {((activeTab === 'admin' && product.status === 'pending') || 
                          (activeTab === 'enduser' && !product.approved)) && (
                          <>
                            <button
                              onClick={() => handleApprove(product.id)}
                              className="text-success-600 hover:text-success-900"
                              title="Approve"
                            >
                              <Check className="h-4 w-4" />
                            </button>
                            <button
                              onClick={() => handleReject(product.id)}
                              className="text-danger-600 hover:text-danger-900"
                              title="Reject"
                            >
                              <X className="h-4 w-4" />
                            </button>
                          </>
                        )}
                        <button
                          onClick={() => handleDiscontinue(product.id, !product.discontinued)}
                          className={`${
                            product.discontinued 
                              ? 'text-green-600 hover:text-green-900' 
                              : 'text-orange-600 hover:text-orange-900'
                          }`}
                          title={product.discontinued ? 'Re-enable Product (Set to Active)' : 'Discontinue Product (Set to Discontinued)'}
                        >
                          {product.discontinued ? (
                            <ToggleRight className="h-4 w-4" />
                          ) : (
                            <ToggleLeft className="h-4 w-4" />
                          )}
                        </button>
                        <button
                          onClick={() => handleDelete(product.id)}
                          className="text-danger-600 hover:text-danger-900"
                          title="Delete"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {productsData && productsData.total_pages > 1 && (
            <div className="flex items-center justify-between px-6 py-3 border-t border-secondary-200">
              <div className="text-sm text-secondary-700">
                Showing {((currentPage - 1) * 10) + 1} to {Math.min(currentPage * 10, productsData.total)} of {productsData.total} results
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                  disabled={currentPage === 1}
                  className="btn btn-secondary btn-sm disabled:opacity-50"
                >
                  Previous
                </button>
                <button
                  onClick={() => setCurrentPage(prev => Math.min(productsData.total_pages, prev + 1))}
                  disabled={currentPage === productsData.total_pages}
                  className="btn btn-secondary btn-sm disabled:opacity-50"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* View Product Modal */}
      {isViewModalOpen && selectedProduct && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Product Details</h2>
              <button
                onClick={() => {
                  setIsViewModalOpen(false);
                  setSelectedProduct(null);
                }}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Title</label>
                <p className="mt-1 text-sm text-gray-900">{selectedProduct.title}</p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Description</label>
                <p className="mt-1 text-sm text-gray-900">{selectedProduct.description}</p>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Price</label>
                  <p className="mt-1 text-sm text-gray-900">R{selectedProduct.price}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Category</label>
                  <p className="mt-1 text-sm text-gray-900">{selectedProduct.category}</p>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Seller</label>
                  <p className="mt-1 text-sm text-gray-900">
                    {selectedProduct.seller.name} {selectedProduct.seller.surname}
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Status</label>
                  <p className="mt-1 text-sm text-gray-900">
                    {selectedProduct.status || 'Pending'}
                  </p>
                </div>
              </div>
              
              {selectedProduct.images && selectedProduct.images.length > 0 && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Product Images
                    <span className="text-xs text-gray-500 ml-2">(Click to enlarge)</span>
                  </label>
                  <div className="mt-1 grid grid-cols-2 gap-4">
                    {selectedProduct.images.map((image, index) => (
                      <div key={index} className="relative">
                        <img
                          src={image}
                          alt={`Product image ${index + 1}`}
                          className="w-full h-48 object-cover rounded-lg border border-gray-200 cursor-pointer hover:opacity-90 transition-opacity"
                          onClick={() => {
                            setSelectedImage(image);
                            setIsImageModalOpen(true);
                          }}
                          onError={(e) => {
                            const target = e.target as HTMLImageElement;
                            target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgdmlld0JveD0iMCAwIDEwMCAxMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiBmaWxsPSIjRjNGNEY2Ii8+CjxwYXRoIGQ9Ik0zMCAzNUg3MFY2NUgzMFYzNVoiIGZpbGw9IiNEMUQ1REIiLz4KPHBhdGggZD0iTTM1IDQwSDY1VjYwSDM1VjQwWiIgZmlsbD0iIzlDQTNBRiIvPgo8L3N2Zz4K';
                            target.alt = 'Image not available';
                          }}
                        />
                        <div className="absolute bottom-2 left-2 bg-black bg-opacity-50 text-white text-xs px-2 py-1 rounded">
                          Image {index + 1}
                        </div>
                      </div>
                    ))}
                  </div>
                  <p className="text-xs text-gray-500 mt-2">
                    {selectedProduct.images.length} image{selectedProduct.images.length !== 1 ? 's' : ''} uploaded
                  </p>
                </div>
              )}
              
              {(!selectedProduct.images || selectedProduct.images.length === 0) && (
                <div>
                  <label className="block text-sm font-medium text-gray-700">Images</label>
                  <div className="mt-1 p-4 border-2 border-dashed border-gray-300 rounded-lg text-center">
                    <p className="text-gray-500 text-sm">No images uploaded for this product</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Edit Product Modal */}
      {isEditModalOpen && selectedProduct && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Edit Product</h2>
              <button
                onClick={() => {
                  setIsEditModalOpen(false);
                  setSelectedProduct(null);
                }}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            
            <EditProductForm
              product={selectedProduct}
              onSubmit={handleUpdateProduct}
              onCancel={() => {
                setIsEditModalOpen(false);
                setSelectedProduct(null);
              }}
            />
          </div>
        </div>
      )}

      {/* Add Product Modal */}
      {isAddModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Add New Product</h2>
              <button
                onClick={() => setIsAddModalOpen(false)}
                className="text-gray-500 hover:text-gray-700 p-1 rounded-full hover:bg-gray-100"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            
            <AddProductForm
              onSubmit={handleCreateProduct}
              onCancel={() => setIsAddModalOpen(false)}
            />
          </div>
                 </div>
       )}

       {/* Image Modal */}
       {isImageModalOpen && selectedImage && (
         <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
           <div className="relative max-w-4xl max-h-full">
             <button
               onClick={() => {
                 setIsImageModalOpen(false);
                 setSelectedImage(null);
               }}
               className="absolute top-4 right-4 bg-black bg-opacity-50 text-white rounded-full w-8 h-8 flex items-center justify-center hover:bg-opacity-75 transition-colors"
             >
               ✕
             </button>
             <img
               src={selectedImage}
               alt="Product image"
               className="max-w-full max-h-full object-contain rounded-lg"
               onError={(e) => {
                 const target = e.target as HTMLImageElement;
                 target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgdmlld0JveD0iMCAwIDEwMCAxMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiBmaWxsPSIjRjNGNEY2Ii8+CjxwYXRoIGQ9Ik0zMCAzNUg3MFY2NUgzMFYzNVoiIGZpbGw9IiNEMUQ1REIiLz4KPHBhdGggZD0iTTM1IDQwSDY1VjYwSDM1VjQwWiIgZmlsbD0iIzlDQTNBRiIvPgo8L3N2Zz4K';
                 target.alt = 'Image not available';
               }}
             />
           </div>
         </div>
       )}
     </div>
   );
 };

export default ProductsPage;

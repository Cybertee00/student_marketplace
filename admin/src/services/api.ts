import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { 
  User, 
  Product, 
  Order, 
  Revenue, 
  Message, 
  NotificationType, 
  DashboardStats,
  LoginCredentials,
  AuthResponse,
  ProductFilters,
  OrderFilters,
  UserFilters,
  PaginatedResponse,
  ApiResponse,
  InventorySummary,
  InventoryLog,
  StockUpdateRequest,
  MessageFilters,
  Conversation,
  MessageStats
} from '@/types';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    // Use environment variable for API URL, fallback to proxy for development
    const apiBaseUrl = import.meta.env.VITE_API_URL || '/api';
    this.api = axios.create({
      baseURL: apiBaseUrl.startsWith('http') ? apiBaseUrl : '/api',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.api.interceptors.request.use(
      async (config) => {
        // Try to get token from Supabase session first
        const { supabase } = await import('./supabase');
        const { data: { session } } = await supabase.auth.getSession();
        
        if (session?.access_token) {
          config.headers.Authorization = `Bearer ${session.access_token}`;
        } else {
          // Fallback to localStorage token
          const token = localStorage.getItem('admin_token');
          if (token) {
            config.headers.Authorization = `Bearer ${token}`;
          }
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor to handle errors
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error.response?.status, error.response?.data);
        if (error.response?.status === 401) {
          localStorage.removeItem('admin_token');
          localStorage.removeItem('admin_user');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth endpoints
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    console.log('ApiService login - making request with:', credentials);
    const response: AxiosResponse<AuthResponse> = await this.api.post('/auth/login', credentials);
    console.log('ApiService login - response:', response.data);
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response: AxiosResponse<User> = await this.api.get('/auth/me');
    return response.data;
  }

  // Dashboard endpoints
  async getDashboardStats(): Promise<DashboardStats> {
    const response: AxiosResponse<DashboardStats> = await this.api.get('/admin/dashboard');
    return response.data;
  }

  // Product endpoints
  async getProducts(filters?: ProductFilters, page = 1, limit = 10): Promise<PaginatedResponse<Product>> {
    const params = { page, limit, ...filters };
    const response: AxiosResponse<PaginatedResponse<Product>> = await this.api.get('/admin/products', { params });
    return response.data;
  }

  async getProduct(id: number): Promise<Product> {
    const response: AxiosResponse<Product> = await this.api.get(`/admin/products/${id}`);
    return response.data;
  }

  async approveProduct(id: number): Promise<ApiResponse<Product>> {
    const response: AxiosResponse<ApiResponse<Product>> = await this.api.put(`/admin/products/${id}/approve`);
    return response.data;
  }

  async rejectProduct(id: number, reason?: string): Promise<ApiResponse<Product>> {
    const response: AxiosResponse<ApiResponse<Product>> = await this.api.put(`/admin/products/${id}/reject`, { reason });
    return response.data;
  }

  async updateProduct(id: number, data: Partial<Product>): Promise<ApiResponse<Product>> {
    const response: AxiosResponse<ApiResponse<Product>> = await this.api.put(`/admin/products/${id}`, data);
    return response.data;
  }

  async deleteProduct(id: number): Promise<ApiResponse<void>> {
    const response: AxiosResponse<ApiResponse<void>> = await this.api.delete(`/admin/products/${id}`);
    return response.data;
  }

  async discontinueProduct(id: number, discontinued: boolean, reason?: string): Promise<ApiResponse<Product>> {
    const response: AxiosResponse<ApiResponse<Product>> = await this.api.patch(`/admin/products/${id}/discontinue`, {
      discontinued,
      reason
    });
    return response.data;
  }

  async createProduct(data: Omit<Product, 'id' | 'created_at' | 'updated_at'>): Promise<ApiResponse<Product>> {
    const response: AxiosResponse<ApiResponse<Product>> = await this.api.post('/admin/products', data);
    return response.data;
  }

  async uploadImage(file: File): Promise<ApiResponse<{ filename: string; url: string }>> {
    // Get signed URL from backend for Supabase Storage
    const { data: uploadData } = await this.api.post('/images/upload-url', {
      bucket: 'products',
      filename: file.name,
    });
    
    const { signed_url, path, public_url } = uploadData;
    
    // Upload directly to Supabase Storage using signed URL
    const uploadResponse = await fetch(signed_url, {
      method: 'PUT',
      body: file,
      headers: {
        'Content-Type': file.type,
      },
    });
    
    if (!uploadResponse.ok) {
      throw new Error('Failed to upload image to Supabase Storage');
    }
    
    return {
      success: true,
      message: 'Image uploaded successfully',
      data: {
        filename: path,
        url: public_url,
      },
    };
  }

  async getUploadUrl(bucket: string, filename: string): Promise<{ signed_url: string; path: string; public_url: string }> {
    const response: AxiosResponse<{ signed_url: string; path: string; public_url: string }> = await this.api.post('/images/upload-url', {
      bucket,
      filename,
    });
    return response.data;
  }

  // Order endpoints
  async getOrders(filters?: OrderFilters, page = 1, limit = 10): Promise<PaginatedResponse<Order>> {
    const params = { page, limit, ...filters };
    const response: AxiosResponse<PaginatedResponse<Order>> = await this.api.get('/admin/orders', { params });
    return response.data;
  }

  async getOrder(id: number): Promise<Order> {
    const response: AxiosResponse<Order> = await this.api.get(`/admin/orders/${id}`);
    return response.data;
  }

  async updateOrderStatus(id: number, status: Order['status']): Promise<ApiResponse<Order>> {
    const response: AxiosResponse<ApiResponse<Order>> = await this.api.put(`/admin/orders/${id}/status`, { status });
    return response.data;
  }

  // User endpoints
  async getUsers(filters?: UserFilters, page = 1, limit = 10): Promise<any> {
    const params: any = { page, limit };
    
    // Map frontend filter names to backend parameter names
    if (filters?.search) params.search = filters.search;
    if (filters?.role) params.role_filter = filters.role;
    if (filters?.is_active !== undefined) {
      params.status = filters.is_active ? 'active' : 'inactive';
    }
    
    console.log('getUsers - params:', params);
    console.log('getUsers - token:', localStorage.getItem('admin_token'));
    
    // Remove trailing slash to match backend route
    const response: AxiosResponse<PaginatedResponse<User>> = await this.api.get('/admin/users', { params });
    console.log('getUsers - response:', response.data);
    return response.data;
  }

  async getUser(id: number): Promise<User> {
    const response: AxiosResponse<User> = await this.api.get(`/admin/users/${id}`);
    return response.data;
  }

  async updateUser(id: number, data: Partial<User>): Promise<ApiResponse<User>> {
    const response: AxiosResponse<ApiResponse<User>> = await this.api.put(`/admin/users/${id}`, data);
    return response.data;
  }

  async deactivateUser(id: number): Promise<ApiResponse<void>> {
    const response: AxiosResponse<ApiResponse<void>> = await this.api.put(`/admin/users/${id}/deactivate`);
    return response.data;
  }

  async assignRole(userId: number, roleName: string): Promise<ApiResponse<any>> {
    const response: AxiosResponse<ApiResponse<any>> = await this.api.post(`/admin/users/${userId}/roles`, { role_name: roleName });
    return response.data;
  }

  async removeRole(userId: number, roleName: string): Promise<ApiResponse<void>> {
    const response: AxiosResponse<ApiResponse<void>> = await this.api.delete(`/admin/users/${userId}/roles/${roleName}`);
    return response.data;
  }

  async getAvailableRoles(): Promise<{ roles: any[] }> {
    console.log('getAvailableRoles - token:', localStorage.getItem('admin_token'));
    const response: AxiosResponse<{ roles: any[] }> = await this.api.get('/admin/users/roles/available');
    console.log('getAvailableRoles - response:', response.data);
    return response.data;
  }

  async getUserStats(): Promise<any> {
    console.log('getUserStats - token:', localStorage.getItem('admin_token'));
    const response: AxiosResponse<any> = await this.api.get('/admin/users/stats');
    console.log('getUserStats - response:', response.data);
    return response.data;
  }

  // Revenue endpoints
  async getRevenue(filters?: any): Promise<any> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== '' && value !== null) {
          params.append(key, value.toString());
        }
      });
    }
    const response: AxiosResponse<any> = await this.api.get(`/admin/revenue?${params}`);
    return response.data;
  }

  async getRevenueSummary(filters?: any): Promise<any> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== '' && value !== null) {
          params.append(key, value.toString());
        }
      });
    }
    const response: AxiosResponse<any> = await this.api.get(`/admin/revenue/summary?${params}`);
    return response.data;
  }

  async exportRevenue(filters?: any): Promise<any> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== '' && value !== null) {
          params.append(key, value.toString());
        }
      });
    }
    const response: AxiosResponse<any> = await this.api.get(`/admin/revenue/export?${params}`);
    return response.data;
  }

  // ==================== ADMIN MESSAGING ====================
  
  // Get all messages with filters
  async getAdminMessages(filters: MessageFilters = {}, page = 1, limit = 20): Promise<PaginatedResponse<Message>> {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
      ...(filters.conversation_id && { conversation_id: filters.conversation_id }),
      ...(filters.user_id && { user_id: filters.user_id.toString() }),
      ...(filters.message_type && { message_type: filters.message_type }),
      ...(filters.is_read !== undefined && { is_read: filters.is_read.toString() }),
      ...(filters.is_important !== undefined && { is_important: filters.is_important.toString() }),
      ...(filters.search && { search: filters.search }),
      ...(filters.date_from && { date_from: filters.date_from }),
      ...(filters.date_to && { date_to: filters.date_to })
    });
    
    const response = await this.api.get(`/admin/messages?${params}`);
    return response.data;
  }

  // Get all conversations
  async getAdminConversations(page = 1, limit = 20, userId?: number): Promise<PaginatedResponse<Conversation>> {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
      ...(userId && { user_id: userId.toString() })
    });
    
    const response = await this.api.get(`/admin/messages/conversations?${params}`);
    return response.data;
  }

  // Get conversation messages
  async getConversationMessages(conversationId: string, page = 1, limit = 50): Promise<PaginatedResponse<Message>> {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString()
    });
    
    const response = await this.api.get(`/admin/messages/conversations/${conversationId}?${params}`);
    return response.data;
  }

  // Send message as admin
  async sendAdminMessage(messageData: {
    receiver_id: number;
    message: string;
    conversation_id?: string;
    message_type?: string;
    parent_message_id?: number;
  }): Promise<Message> {
    const response = await this.api.post('/admin/messages/send', messageData);
    return response.data;
  }

  // Mark message as read
  async markMessageAsRead(messageId: number): Promise<{ message: string; message_id: number }> {
    const response = await this.api.put(`/admin/messages/${messageId}/read`);
    return response.data;
  }

  // Toggle message importance
  async toggleMessageImportant(messageId: number): Promise<{ message: string; message_id: number; is_important: boolean }> {
    const response = await this.api.put(`/admin/messages/${messageId}/important`);
    return response.data;
  }

  // Delete message
  async deleteMessage(messageId: number): Promise<{ message: string; message_id: number }> {
    const response = await this.api.delete(`/admin/messages/${messageId}`);
    return response.data;
  }

  // Get message statistics
  async getMessageStats(): Promise<MessageStats> {
    const response = await this.api.get('/admin/messages/stats');
    return response.data;
  }

  // Notification endpoints
  async getNotifications(filters?: any): Promise<any> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== '' && value !== null) {
          params.append(key, value.toString());
        }
      });
    }
    const response: AxiosResponse<any> = await this.api.get(`/admin/notifications?${params}`);
    return response.data;
  }

  async getUnreadNotificationsCount(): Promise<any> {
    const response: AxiosResponse<any> = await this.api.get('/admin/notifications/unread-count');
    return { unread_count: response.data.unread_count };
  }

  async markNotificationAsRead(id: number): Promise<ApiResponse<void>> {
    const response: AxiosResponse<any> = await this.api.put(`/admin/notifications/${id}/read`);
    return { success: true, message: response.data.message, data: undefined };
  }

  async markAllNotificationsAsRead(): Promise<ApiResponse<void>> {
    const response: AxiosResponse<any> = await this.api.put('/admin/notifications/read-all');
    return { success: true, message: response.data.message, data: undefined };
  }

  async deleteNotification(id: number): Promise<ApiResponse<void>> {
    const response: AxiosResponse<any> = await this.api.delete(`/admin/notifications/${id}`);
    return { success: true, message: response.data.message, data: undefined };
  }

  async deleteAllNotifications(): Promise<ApiResponse<void>> {
    const response: AxiosResponse<any> = await this.api.delete('/admin/notifications');
    return { success: true, message: response.data.message, data: undefined };
  }

  // Inventory endpoints
  async getProductInventory(productId: number): Promise<InventorySummary> {
    const response: AxiosResponse<InventorySummary> = await this.api.get(`/admin/products/${productId}/inventory`);
    return response.data;
  }

  async updateProductStock(productId: number, data: StockUpdateRequest): Promise<ApiResponse<Product>> {
    const response: AxiosResponse<ApiResponse<Product>> = await this.api.put(`/admin/products/${productId}/inventory/stock`, data);
    return response.data;
  }

  async addProductStock(productId: number, data: StockUpdateRequest): Promise<ApiResponse<Product>> {
    const response: AxiosResponse<ApiResponse<Product>> = await this.api.post(`/admin/products/${productId}/inventory/add-stock`, data);
    return response.data;
  }

  async removeProductStock(productId: number, data: StockUpdateRequest): Promise<ApiResponse<Product>> {
    const response: AxiosResponse<ApiResponse<Product>> = await this.api.post(`/admin/products/${productId}/inventory/remove-stock`, data);
    return response.data;
  }

  async getProductInventoryLogs(productId: number, limit = 50, offset = 0): Promise<InventoryLog[]> {
    const response: AxiosResponse<InventoryLog[]> = await this.api.get(`/admin/products/${productId}/inventory/logs`, {
      params: { limit, offset }
    });
    return response.data;
  }

  async getLowStockProducts(limit = 50): Promise<{ products: any[], total: number }> {
    const response: AxiosResponse<{ products: any[], total: number }> = await this.api.get('/admin/products/inventory/low-stock', {
      params: { limit }
    });
    return response.data;
  }

  async getOutOfStockProducts(limit = 50): Promise<{ products: any[], total: number }> {
    const response: AxiosResponse<{ products: any[], total: number }> = await this.api.get('/admin/products/inventory/out-of-stock', {
      params: { limit }
    });
    return response.data;
  }
}

export const apiService = new ApiService();

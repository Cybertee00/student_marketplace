// User types
export interface User {
  id: number;
  name: string;
  surname: string;
  email: string;
  phone: string;
  username: string;
  profile_img?: string;
  created_at: string;
  is_active?: boolean;
}

// Role types
export interface Role {
  id: number;
  name: string;
  description: string;
  assigned_at?: string;
  assigned_by?: number;
  permissions?: Permission[];
  permission_count?: number;
}

export interface Permission {
  id: number;
  name: string;
  description: string;
  resource: string;
  action: string;
}

// Product types
export interface Product {
  id: number;
  title: string;
  description: string;
  price: number;
  category: string;
  faculty?: string;
  images: string[];
  seller_id: number;
  seller: User;
  status: 'pending' | 'approved' | 'rejected' | 'sold';
  approved?: boolean;
  discontinued?: boolean;
  created_at: string;
  updated_at: string;
  created_via?: string;
  // Inventory fields
  inventory?: {
    stock_quantity: number;
    initial_stock: number;
    sold_quantity: number;
    low_stock_threshold: number;
    is_out_of_stock: boolean;
    last_stock_update: string;
  };
}

// Inventory types
export interface InventorySummary {
  product_id: number;
  product_title: string;
  current_stock: number;
  initial_stock: number;
  sold_quantity: number;
  is_out_of_stock: boolean;
  low_stock_alert: boolean;
  last_stock_update: string;
  stock_percentage: number;
}

export interface InventoryLog {
  id: number;
  product_id: number;
  change_type: string;
  quantity_changed: number;
  previous_stock: number;
  new_stock: number;
  reason?: string;
  user_id?: number;
  order_id?: number;
  created_at: string;
}

export interface StockUpdateRequest {
  stock_quantity: number;
  reason?: string;
}

// Order types
export interface OrderItem {
  id: number;
  order_id: number;
  product_id: number;
  product: Product;
  quantity: number;
  price: number;
}

export interface Order {
  id: number;
  buyer_id: number;
  buyer: User;
  items: OrderItem[];
  total_amount: number;
  status: 'pending' | 'paid' | 'completed' | 'cancelled';
  payment_method: string;
  created_at: string;
  updated_at: string;
}

// Revenue types
export interface Revenue {
  id: number;
  order_id: number;
  amount: number;
  commission: number;
  platform_fee: number;
  seller_revenue: number;
  created_at: string;
}

// Message types
export interface Message {
  id: number;
  sender_id: number;
  receiver_id: number;
  sender: User;
  receiver: User;
  content: string;
  message: string;
  message_type: string;
  conversation_id?: string;
  is_read: boolean;
  is_important: boolean;
  parent_message_id?: number;
  created_at: string;
  updated_at: string;
  replies_count?: number;
}

export interface Conversation {
  conversation_id: string;
  latest_message: Message;
  participants: User[];
  unread_count: number;
  total_messages: number;
}

export interface MessageStats {
  total_messages: number;
  unread_messages: number;
  important_messages: number;
  recent_messages: number;
  active_conversations: number;
  message_types: Record<string, number>;
}

export interface MessageFilters {
  conversation_id?: string;
  user_id?: number;
  message_type?: string;
  is_read?: boolean;
  is_important?: boolean;
  search?: string;
  date_from?: string;
  date_to?: string;
}

// Notification types
export interface NotificationType {
  id: number;
  user_id: number;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  is_read: boolean;
  created_at: string;
}

// Dashboard stats
export interface DashboardStats {
  total_revenue: number;
  total_users: number;
  total_products: number;
  total_orders: number;
  pending_approvals: number;
  active_users: number;
  revenue_trend: RevenueTrend[];
  top_products: TopProduct[];
  top_categories: TopCategory[];
}

export interface RevenueTrend {
  date: string;
  revenue: number;
}

export interface TopProduct {
  id: number;
  title: string;
  total_sales: number;
  revenue: number;
}

export interface TopCategory {
  category: string;
  total_products: number;
  total_sales: number;
}

// API Response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

// Auth types
export interface LoginCredentials {
  identifier: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// Filter types
export interface ProductFilters {
  category?: string;
  status?: string;
  discontinued?: boolean;
  seller_id?: number;
  min_price?: number;
  max_price?: number;
  search?: string;
  created_via?: string;
}

export interface OrderFilters {
  status?: string;
  buyer_id?: number;
  date_from?: string;
  date_to?: string;
  search?: string;
}

export interface UserFilters {
  is_active?: boolean;
  search?: string;
  role?: string;
}

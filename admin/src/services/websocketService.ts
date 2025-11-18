import { io, Socket } from 'socket.io-client';

export interface WebSocketMessage {
  type: string;
  data: any;
}

export interface MessageData {
  id: number;
  sender_id: number;
  receiver_id: number;
  message: string;
  message_type: string;
  conversation_id: string;
  is_read: boolean;
  is_important: boolean;
  parent_message_id?: number;
  created_at: string;
  updated_at: string;
  sender: {
    id: number;
    name: string;
    surname: string;
    email: string;
    username: string;
    phone?: string;
    profile_img?: string;
    created_at: string;
  };
  receiver: {
    id: number;
    name: string;
    surname: string;
    email: string;
    username: string;
    phone?: string;
    profile_img?: string;
    created_at: string;
  };
}

export interface TypingData {
  conversation_id: string;
  user_id: number;
  is_typing: boolean;
  timestamp: string;
}

class WebSocketService {
  private socket: Socket | null = null;
  private isConnected = false;
  private currentUserId: number | null = null;
  private currentConversationId: string | null = null;
  private messageListeners: ((message: MessageData) => void)[] = [];
  private typingListeners: ((typing: TypingData) => void)[] = [];
  private connectionListeners: ((connected: boolean) => void)[] = [];

  // Getters
  get connected(): boolean {
    return this.isConnected;
  }

  get userId(): number | null {
    return this.currentUserId;
  }

  get conversationId(): string | null {
    return this.currentConversationId;
  }

  // Event listeners
  onMessage(callback: (message: MessageData) => void): () => void {
    this.messageListeners.push(callback);
    return () => {
      const index = this.messageListeners.indexOf(callback);
      if (index > -1) {
        this.messageListeners.splice(index, 1);
      }
    };
  }

  onTyping(callback: (typing: TypingData) => void): () => void {
    this.typingListeners.push(callback);
    return () => {
      const index = this.typingListeners.indexOf(callback);
      if (index > -1) {
        this.typingListeners.splice(index, 1);
      }
    };
  }

  onConnection(callback: (connected: boolean) => void): () => void {
    this.connectionListeners.push(callback);
    return () => {
      const index = this.connectionListeners.indexOf(callback);
      if (index > -1) {
        this.connectionListeners.splice(index, 1);
      }
    };
  }

  // Connection management
  async connect(userId: number, token: string): Promise<void> {
    if (this.isConnected && this.currentUserId === userId) {
      return; // Already connected for this user
    }

    await this.disconnect(); // Disconnect any existing connection

    try {
      // Create WebSocket URL with token
      const wsUrl = `ws://localhost:8000/ws/admin/${userId}?token=${token}`;
      
      this.socket = new WebSocket(wsUrl);
      this.currentUserId = userId;

      this.socket.onopen = () => {
        console.log(`WebSocket connected for admin ${userId}`);
        this.isConnected = true;
        this.notifyConnectionListeners(true);
        this.startHeartbeat();
      };

      this.socket.onmessage = (event) => {
        this.handleMessage(event.data);
      };

      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.isConnected = false;
        this.notifyConnectionListeners(false);
      };

      this.socket.onclose = () => {
        console.log('WebSocket disconnected');
        this.isConnected = false;
        this.notifyConnectionListeners(false);
        this.stopHeartbeat();
      };

    } catch (error) {
      console.error('WebSocket connection error:', error);
      this.isConnected = false;
      this.notifyConnectionListeners(false);
      throw error;
    }
  }

  async disconnect(): Promise<void> {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }

    this.isConnected = false;
    this.currentUserId = null;
    this.currentConversationId = null;
    this.stopHeartbeat();
    this.notifyConnectionListeners(false);
    console.log('WebSocket disconnected');
  }

  // Conversation management
  joinConversation(conversationId: string): void {
    if (!this.isConnected || !this.socket) return;

    this.currentConversationId = conversationId;

    const message = {
      type: 'join_conversation',
      conversation_id: conversationId,
    };

    this.socket.send(JSON.stringify(message));
    console.log('Joined conversation:', conversationId);
  }

  leaveConversation(): void {
    if (!this.isConnected || !this.socket || !this.currentConversationId) return;

    const message = {
      type: 'leave_conversation',
      conversation_id: this.currentConversationId,
    };

    this.socket.send(JSON.stringify(message));
    console.log('Left conversation:', this.currentConversationId);

    this.currentConversationId = null;
  }

  // Typing indicators
  sendTypingIndicator(conversationId: string, isTyping: boolean): void {
    if (!this.isConnected || !this.socket) return;

    const message = {
      type: 'typing',
      conversation_id: conversationId,
      is_typing: isTyping,
    };

    this.socket.send(JSON.stringify(message));
  }

  // Heartbeat
  private heartbeatInterval: NodeJS.Timeout | null = null;

  private startHeartbeat(): void {
    this.stopHeartbeat();
    this.heartbeatInterval = setInterval(() => {
      if (this.isConnected && this.socket) {
        this.sendPing();
      } else {
        this.stopHeartbeat();
      }
    }, 30000); // 30 seconds
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  private sendPing(): void {
    if (!this.isConnected || !this.socket) return;

    const message = {
      type: 'ping',
    };

    this.socket.send(JSON.stringify(message));
  }

  // Message handling
  private handleMessage(data: string): void {
    try {
      const message: WebSocketMessage = JSON.parse(data);
      const { type } = message;

      switch (type) {
        case 'new_message':
          this.notifyMessageListeners(message.data);
          break;
        case 'typing':
          this.notifyTypingListeners(message.data);
          break;
        case 'joined_conversation':
          console.log('Successfully joined conversation:', message.data.conversation_id);
          break;
        case 'left_conversation':
          console.log('Successfully left conversation:', message.data.conversation_id);
          break;
        case 'pong':
          // Heartbeat response - connection is alive
          break;
        case 'error':
          console.error('WebSocket error:', message.data.message);
          break;
        default:
          console.log('Unknown WebSocket message type:', type);
      }
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  }

  // Notify listeners
  private notifyMessageListeners(message: MessageData): void {
    this.messageListeners.forEach(callback => callback(message));
  }

  private notifyTypingListeners(typing: TypingData): void {
    this.typingListeners.forEach(callback => callback(typing));
  }

  private notifyConnectionListeners(connected: boolean): void {
    this.connectionListeners.forEach(callback => callback(connected));
  }
}

// Export singleton instance
export const websocketService = new WebSocketService();
export default websocketService;

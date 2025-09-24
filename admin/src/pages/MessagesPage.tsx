import React, { useState, useEffect, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  MessageSquare, 
  Users, 
  Search, 
  Filter, 
  Send, 
  Star, 
  StarOff, 
  Eye, 
  Trash2,
  Phone,
  Mail,
  User,
  AlertCircle,
  Reply,
  X
} from 'lucide-react';
import { apiService } from '@/services/api';
import { websocketService, MessageData, TypingData } from '@/services/websocketService';
import { Message, MessageFilters } from '@/types';
import { formatMessageTime } from '@/utils/formatters';
import { useAuth } from '@/contexts/AuthContext';

interface NewConversationModalProps {
  onClose: () => void;
  onStartConversation: (userId: number) => void;
}

const NewConversationModal: React.FC<NewConversationModalProps> = ({ onClose, onStartConversation }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedUser, setSelectedUser] = useState<number | null>(null);

  // Fetch users for the modal
  const { data: usersData, isLoading } = useQuery({
    queryKey: ['users-for-conversation', searchTerm],
    queryFn: () => apiService.getUsers({ search: searchTerm || undefined }, 1, 50),
  });

  const handleStartConversation = () => {
    if (selectedUser) {
      onStartConversation(selectedUser);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-secondary-900">Start New Conversation</h3>
          <button
            onClick={onClose}
            className="text-secondary-400 hover:text-secondary-600"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="mb-4">
          <input
            type="text"
            placeholder="Search users..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-3 py-2 border border-secondary-200 rounded-lg focus:ring-2 focus:ring-secondary-500 focus:border-transparent"
          />
        </div>

        <div className="max-h-64 overflow-y-auto mb-4">
          {isLoading ? (
            <div className="text-center text-secondary-500 py-4">Loading users...</div>
          ) : usersData?.users?.length === 0 ? (
            <div className="text-center text-secondary-500 py-4">No users found</div>
          ) : (
            usersData?.users?.map((user: any) => (
              <div
                key={user.id}
                onClick={() => setSelectedUser(user.id)}
                className={`p-3 border border-secondary-200 rounded-lg mb-2 cursor-pointer hover:bg-secondary-50 ${
                  selectedUser === user.id ? 'bg-secondary-100 border-secondary-300' : ''
                }`}
              >
                <div className="flex items-center space-x-3">
                  <div className="h-8 w-8 bg-primary-100 rounded-full flex items-center justify-center">
                    <User className="h-4 w-4 text-primary-600" />
                  </div>
                  <div>
                    <p className="font-medium text-secondary-900">{user.name} {user.surname}</p>
                    <p className="text-sm text-secondary-600">{user.email}</p>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        <div className="flex justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-secondary-600 border border-secondary-200 rounded-lg hover:bg-secondary-50"
          >
            Cancel
          </button>
          <button
            onClick={handleStartConversation}
            disabled={!selectedUser}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Start Conversation
          </button>
        </div>
      </div>
    </div>
  );
};

const MessagesPage: React.FC = () => {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const [selectedConversation, setSelectedConversation] = useState<string | null>(null);
  const [selectedUser, setSelectedUser] = useState<number | null>(null);
  const [filters, setFilters] = useState<MessageFilters>({});
  const [searchTerm, setSearchTerm] = useState('');
  const [messageText, setMessageText] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [viewMode, setViewMode] = useState<'conversations' | 'messages'>('conversations');
  const [showNewConversationModal, setShowNewConversationModal] = useState(false);
  
  // WebSocket state
  const [isTyping, setIsTyping] = useState(false);
  const [typingUserId, setTypingUserId] = useState<number | null>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // WebSocket initialization
  useEffect(() => {
    const initializeWebSocket = async () => {
      if (!user?.id) return;
      
      try {
        const token = localStorage.getItem('auth_token');
        if (!token) return;
        
        await websocketService.connect(user.id, token);
        
        // Listen to real-time messages
        const unsubscribeMessage = websocketService.onMessage((_messageData: MessageData) => {
          // Invalidate queries to refresh data
          queryClient.invalidateQueries({ queryKey: ['conversation-messages'] });
          queryClient.invalidateQueries({ queryKey: ['admin-conversations'] });
          queryClient.invalidateQueries({ queryKey: ['admin-messages'] });
        });
        
        // Listen to typing indicators
        const unsubscribeTyping = websocketService.onTyping((typingData: TypingData) => {
          setIsTyping(typingData.is_typing);
          setTypingUserId(typingData.user_id);
        });
        
        
        // Cleanup function
        return () => {
          unsubscribeMessage();
          unsubscribeTyping();
          websocketService.disconnect();
        };
      } catch (error) {
        console.error('🔌 WebSocket initialization error:', error);
      }
    };
    
    const cleanup = initializeWebSocket();
    
    return () => {
      cleanup.then(cleanupFn => cleanupFn?.());
    };
  }, [user?.id, queryClient]);

  // Fetch conversations
  const { data: conversationsData, isLoading: conversationsLoading } = useQuery({
    queryKey: ['admin-conversations', filters, selectedUser],
    queryFn: () => apiService.getAdminConversations(1, 50, selectedUser || undefined),
    // Refetch when selectedUser changes to ensure we get the right conversations
    refetchOnWindowFocus: false,
  });

  // Fetch messages for selected conversation
  const { data: messagesData, isLoading: messagesLoading } = useQuery({
    queryKey: ['conversation-messages', selectedConversation],
    queryFn: () => selectedConversation ? apiService.getConversationMessages(selectedConversation, 1, 100) : null,
    enabled: !!selectedConversation,
  });

  // Fetch all messages with filters
  const { data: allMessagesData, isLoading: allMessagesLoading } = useQuery({
    queryKey: ['admin-messages', filters, viewMode],
    queryFn: () => viewMode === 'messages' ? apiService.getAdminMessages(filters, 1, 50) : null,
    enabled: viewMode === 'messages',
  });

  // Fetch message stats
  const { data: messageStats } = useQuery({
    queryKey: ['message-stats'],
    queryFn: () => apiService.getMessageStats(),
  });

  // Mutations
  const sendMessageMutation = useMutation({
    mutationFn: (data: any) => apiService.sendAdminMessage(data),
    onSuccess: (response) => {
      queryClient.invalidateQueries({ queryKey: ['conversation-messages'] });
      queryClient.invalidateQueries({ queryKey: ['admin-conversations'] });
      setMessageText('');
      
      // If we were starting a new conversation, set the conversation ID
      if (selectedUser && !selectedConversation && response.conversation_id) {
        setSelectedConversation(response.conversation_id);
        setSelectedUser(null); // Clear selected user since we now have a conversation
      }
    },
    onError: (error) => {
      console.error('Error sending message:', error);
    },
  });

  const markReadMutation = useMutation({
    mutationFn: (messageId: number) => apiService.markMessageAsRead(messageId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['conversation-messages'] });
      queryClient.invalidateQueries({ queryKey: ['admin-conversations'] });
    },
  });

  const toggleImportantMutation = useMutation({
    mutationFn: (messageId: number) => apiService.toggleMessageImportant(messageId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['conversation-messages'] });
      queryClient.invalidateQueries({ queryKey: ['admin-messages'] });
    },
  });

  const deleteMessageMutation = useMutation({
    mutationFn: (messageId: number) => apiService.deleteMessage(messageId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['conversation-messages'] });
      queryClient.invalidateQueries({ queryKey: ['admin-messages'] });
    },
  });

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messagesData]);

  // Auto-mark messages as read when conversation is selected
  useEffect(() => {
    if (selectedConversation && messagesData?.data) {
      // Find all unread messages in the current conversation
      const unreadMessages = messagesData.data.filter(message => !message.is_read);
      
      // Mark each unread message as read
      unreadMessages.forEach(message => {
        markReadMutation.mutate(message.id);
      });
    }
  }, [selectedConversation, messagesData]);

  // Handle URL parameters for starting conversations with specific users
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const userId = urlParams.get('user');
    if (userId) {
      // Find or create conversation with this user
      const userIdNum = parseInt(userId);
      setSelectedUser(userIdNum);
      // Clear the URL parameter
      window.history.replaceState({}, '', '/messages');
    }
  }, []);


  // Handle conversation selection and loading
  useEffect(() => {
    if (selectedConversation && conversationsData?.data) {
      // Check if the selected conversation exists in the conversations list
      const conversation = conversationsData.data.find(c => c.conversation_id === selectedConversation);
      if (!conversation) {
        // Don't invalidate queries - just log the issue
      }
      
      // Join the conversation for real-time updates
      websocketService.joinConversation(selectedConversation);
    } else {
      // Leave current conversation if no conversation is selected
      websocketService.leaveConversation();
    }
  }, [selectedConversation, conversationsData]);

  const handleSendMessage = () => {
    if (!messageText.trim()) {
      return;
    }
    
    // Send typing indicator (stopped typing)
    if (selectedConversation) {
      websocketService.sendTypingIndicator(selectedConversation, false);
    }

    let receiverId: number | null = null;
    let conversationId: string | null = null;

    if (selectedConversation) {
      // Existing conversation
      const participants = conversationsData?.data.find(c => c.conversation_id === selectedConversation)?.participants;
      const receiver = participants?.find(p => p.id !== 1); // Assuming admin ID is 1
      if (receiver) {
        receiverId = receiver.id;
        conversationId = selectedConversation;
      }
    } else if (selectedUser) {
      // New conversation with selected user
      receiverId = selectedUser;
      conversationId = null; // Let backend generate conversation ID
    }

    if (receiverId) {
      sendMessageMutation.mutate({
        receiver_id: receiverId,
        message: messageText,
        conversation_id: conversationId,
        message_type: 'text'
      });
    }
  };
  
  const handleMessageTextChange = (text: string) => {
    setMessageText(text);
    
    // Send typing indicator
    if (selectedConversation) {
      websocketService.sendTypingIndicator(selectedConversation, text.length > 0);
    }
  };

  const handleMarkAsRead = (messageId: number) => {
    markReadMutation.mutate(messageId);
  };

  const handleToggleImportant = (messageId: number) => {
    toggleImportantMutation.mutate(messageId);
  };

  const handleDeleteMessage = (messageId: number) => {
    if (confirm('Are you sure you want to delete this message?')) {
      deleteMessageMutation.mutate(messageId);
    }
  };

  const handleReplyToMessage = (message: Message) => {
    // Get sender ID from either sender_id field or sender object
    const senderId = message.sender_id || message.sender?.id;
    
    if (!senderId) {
      console.error('ERROR: No sender ID found in message:', message);
      alert('Error: Cannot identify message sender. Please try again.');
      return;
    }
    
    // Clear all previous selections
    setSelectedConversation(null);
    setSelectedUser(null);
    
    // Force switch to conversations view
    setViewMode('conversations');
    
    // Always set the user first - this will show the message input
    setSelectedUser(senderId);
    
    // If there's a conversation_id, also set it
    if (message.conversation_id) {
      setSelectedConversation(message.conversation_id);
    }
  };

  const getMessageTypeIcon = (type: string) => {
    switch (type) {
      case 'order_inquiry': return <AlertCircle className="w-4 h-4 text-orange-500" />;
      case 'support': return <Phone className="w-4 h-4 text-blue-500" />;
      case 'text': return <MessageSquare className="w-4 h-4 text-gray-500" />;
      default: return <MessageSquare className="w-4 h-4 text-gray-500" />;
    }
  };


  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-2xl font-semibold text-secondary-900">Messages</h1>
          </div>
          <p className="text-secondary-600">Manage customer communications and support requests</p>
        </div>
        
        {/* Stats Cards */}
        <div className="flex space-x-4">
          {messageStats && (
            <>
              <div className="bg-blue-50 p-3 rounded-lg">
                <div className="text-blue-600 text-sm font-medium">Unread</div>
                <div className="text-blue-900 text-xl font-bold">{messageStats.unread_messages}</div>
              </div>
              <div className="bg-orange-50 p-3 rounded-lg">
                <div className="text-orange-600 text-sm font-medium">Important</div>
                <div className="text-orange-900 text-xl font-bold">{messageStats.important_messages}</div>
              </div>
              <div className="bg-green-50 p-3 rounded-lg">
                <div className="text-green-600 text-sm font-medium">Conversations</div>
                <div className="text-green-900 text-xl font-bold">{messageStats.active_conversations}</div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* View Mode Toggle and Actions */}
      <div className="flex justify-between items-center">
        <div className="flex space-x-2">
          <button
            onClick={() => setViewMode('conversations')}
            className={`px-4 py-2 rounded-lg font-medium ${
              viewMode === 'conversations'
                ? 'bg-secondary-900 text-white'
                : 'bg-white text-secondary-600 border border-secondary-200'
            }`}
          >
            <Users className="w-4 h-4 inline mr-2" />
            Conversations
          </button>
          <button
            onClick={() => setViewMode('messages')}
            className={`px-4 py-2 rounded-lg font-medium ${
              viewMode === 'messages'
                ? 'bg-secondary-900 text-white'
                : 'bg-white text-secondary-600 border border-secondary-200'
            }`}
          >
            <MessageSquare className="w-4 h-4 inline mr-2" />
            All Messages
          </button>
        </div>
        
        {/* Start New Conversation Button */}
        <button
          onClick={() => setShowNewConversationModal(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-2"
        >
          <MessageSquare className="w-4 h-4" />
          <span>Start New Conversation</span>
        </button>
      </div>

      {/* Filters and Search */}
      <div className="bg-white p-4 rounded-lg border border-secondary-200">
        <div className="flex items-center space-x-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-secondary-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search messages..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-secondary-200 rounded-lg focus:ring-2 focus:ring-secondary-500 focus:border-transparent"
              />
            </div>
          </div>
          
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="px-4 py-2 border border-secondary-200 rounded-lg hover:bg-secondary-50"
          >
            <Filter className="w-4 h-4 inline mr-2" />
            Filters
          </button>
        </div>

        {showFilters && (
          <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
            <select
              value={filters.message_type || ''}
              onChange={(e) => setFilters({ ...filters, message_type: e.target.value || undefined })}
              className="px-3 py-2 border border-secondary-200 rounded-lg"
            >
              <option value="">All Types</option>
              <option value="text">Text</option>
              <option value="order_inquiry">Order Inquiry</option>
              <option value="support">Support</option>
            </select>
            
            <select
              value={filters.is_read === undefined ? '' : filters.is_read.toString()}
              onChange={(e) => setFilters({ ...filters, is_read: e.target.value === '' ? undefined : e.target.value === 'true' })}
              className="px-3 py-2 border border-secondary-200 rounded-lg"
            >
              <option value="">All Status</option>
              <option value="false">Unread</option>
              <option value="true">Read</option>
            </select>
            
            <select
              value={filters.is_important === undefined ? '' : filters.is_important.toString()}
              onChange={(e) => setFilters({ ...filters, is_important: e.target.value === '' ? undefined : e.target.value === 'true' })}
              className="px-3 py-2 border border-secondary-200 rounded-lg"
            >
              <option value="">All Priority</option>
              <option value="true">Important</option>
              <option value="false">Normal</option>
            </select>
            
            <input
              type="date"
              value={filters.date_from || ''}
              onChange={(e) => setFilters({ ...filters, date_from: e.target.value || undefined })}
              className="px-3 py-2 border border-secondary-200 rounded-lg"
            />
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Sidebar - Conversations or Message List */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg border border-secondary-200">
            <div className="p-4 border-b border-secondary-200">
              <h3 className="font-medium text-secondary-900">
                {viewMode === 'conversations' ? 'Conversations' : 'Messages'}
              </h3>
            </div>
            
            <div className="max-h-96 overflow-y-auto">
              {viewMode === 'conversations' ? (
                // Conversations List
                conversationsLoading ? (
                  <div className="p-4 text-center text-secondary-500">Loading conversations...</div>
                ) : (
                  conversationsData?.data.map((conversation) => (
                    <div
                      key={conversation.conversation_id}
                      onClick={() => setSelectedConversation(conversation.conversation_id)}
                      className={`p-4 border-b border-secondary-100 cursor-pointer hover:bg-secondary-50 ${
                        selectedConversation === conversation.conversation_id ? 'bg-secondary-50 border-l-4 border-l-secondary-500' : ''
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2 mb-1">
                            <span className="font-medium text-secondary-900">
                              {conversation.participants.map(p => `${p.name} ${p.surname}`).join(', ')}
                            </span>
                            {conversation.unread_count > 0 && (
                              <span className="bg-red-500 text-white text-xs px-2 py-1 rounded-full">
                                {conversation.unread_count}
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-secondary-600 truncate">
                            {conversation.latest_message.message}
                          </p>
                          <div className="flex items-center space-x-2 mt-2 text-xs text-secondary-500">
                            <span>{formatMessageTime(conversation.latest_message.created_at)}</span>
                            <span>•</span>
                            <span>{conversation.total_messages} messages</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))
                )
              ) : (
                // Messages List
                allMessagesLoading ? (
                  <div className="p-4 text-center text-secondary-500">Loading messages...</div>
                ) : (
                  allMessagesData?.data.map((message) => (
                    <div
                      key={message.id}
                      onClick={() => {
                        // Auto-mark as read when message is clicked
                        if (!message.is_read) {
                          handleMarkAsRead(message.id);
                        }
                        // Open conversation with the sender
                        handleReplyToMessage(message);
                      }}
                      className="p-4 border-b border-secondary-100 hover:bg-secondary-50 cursor-pointer transition-colors duration-200"
                      title="Click to respond to this message"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2 mb-1">
                            <span className="font-medium text-secondary-900">
                              {message.sender.name} {message.sender.surname}
                            </span>
                            {getMessageTypeIcon(message.message_type)}
                            {message.is_important && <Star className="w-4 h-4 text-yellow-500" />}
                          </div>
                          <p className="text-sm text-secondary-600 truncate">
                            {message.message}
                          </p>
                          <div className="flex items-center space-x-2 mt-2 text-xs text-secondary-500">
                            <span>{formatMessageTime(message.created_at)}</span>
                            {!message.is_read && <span className="text-blue-500">• Unread</span>}
                          </div>
                        </div>
                        <div className="flex space-x-1">
                          {!message.is_read && (
                            <button
                              onClick={() => handleMarkAsRead(message.id)}
                              className="p-1 hover:bg-secondary-100 rounded"
                              title="Mark as read"
                            >
                              <Eye className="w-4 h-4 text-secondary-500" />
                            </button>
                          )}
                          <button
                            onClick={() => handleToggleImportant(message.id)}
                            className="p-1 hover:bg-secondary-100 rounded"
                            title={message.is_important ? "Remove important" : "Mark important"}
                          >
                            {message.is_important ? (
                              <StarOff className="w-4 h-4 text-yellow-500" />
                            ) : (
                              <Star className="w-4 h-4 text-secondary-400" />
                            )}
                          </button>
                          <button
                            onClick={() => handleReplyToMessage(message)}
                            className="p-1 hover:bg-secondary-100 rounded text-blue-500"
                            title="Reply to message"
                          >
                            <Reply className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDeleteMessage(message.id)}
                            className="p-1 hover:bg-secondary-100 rounded text-red-500"
                            title="Delete message"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))
                )
              )}
            </div>
          </div>
        </div>

        {/* Right Side - Chat Area or Message Details */}
        <div className="lg:col-span-2">
          {selectedConversation ? (
            // Chat Interface
            <div className="bg-white rounded-lg border border-secondary-200 h-96 flex flex-col">
              {/* Chat Header */}
              <div className="p-4 border-b border-secondary-200">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium text-secondary-900">
                      {conversationsData?.data.find(c => c.conversation_id === selectedConversation)?.participants.map(p => `${p.name} ${p.surname}`).join(', ')}
                    </h3>
                    <p className="text-sm text-secondary-500">
                      {conversationsData?.data.find(c => c.conversation_id === selectedConversation)?.total_messages} messages
                    </p>
                  </div>
                  <div className="flex space-x-2">
                    <button className="p-2 hover:bg-secondary-100 rounded-lg">
                      <Phone className="w-4 h-4 text-secondary-500" />
                    </button>
                    <button className="p-2 hover:bg-secondary-100 rounded-lg">
                      <Mail className="w-4 h-4 text-secondary-500" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messagesLoading ? (
                  <div className="text-center text-secondary-500">Loading messages...</div>
                ) : (
                  messagesData?.data.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.sender_id === 1 ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        onClick={() => {
                          // Auto-mark as read when message is clicked
                          if (!message.is_read) {
                            handleMarkAsRead(message.id);
                          }
                        }}
                        className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg cursor-pointer ${
                          message.sender_id === 1
                            ? 'bg-secondary-900 text-white'
                            : 'bg-secondary-100 text-secondary-900'
                        }`}
                      >
                        <div className="flex items-center space-x-2 mb-1">
                          <span className="text-sm font-medium">
                            {message.sender.name} {message.sender.surname}
                          </span>
                          {getMessageTypeIcon(message.message_type)}
                          {message.is_important && <Star className="w-3 h-3 text-yellow-500" />}
                        </div>
                        <p className="text-sm">{message.message}</p>
                        <div className="text-xs opacity-70 mt-1">
                          {formatMessageTime(message.created_at)}
                        </div>
                      </div>
                    </div>
                  ))
                )}
                
                {/* Typing Indicator */}
                {isTyping && typingUserId && typingUserId !== 1 && (
                  <div className="flex justify-start">
                    <div className="max-w-xs lg:max-w-md px-4 py-2 rounded-lg bg-secondary-100 text-secondary-900">
                      <div className="flex items-center space-x-2">
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-secondary-400 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-secondary-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                          <div className="w-2 h-2 bg-secondary-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                        </div>
                        <span className="text-sm text-secondary-600">User is typing...</span>
                      </div>
                    </div>
                  </div>
                )}
                
                <div ref={messagesEndRef} />
              </div>

              {/* Message Input */}
              <div className="p-4 border-t border-secondary-200">
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={messageText}
                    onChange={(e) => handleMessageTextChange(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    placeholder="Type your message..."
                    className="flex-1 px-3 py-2 border border-secondary-200 rounded-lg focus:ring-2 focus:ring-secondary-500 focus:border-transparent"
                  />
                  <button
                    onClick={handleSendMessage}
                    disabled={!messageText.trim()}
                    className="px-4 py-2 bg-secondary-900 text-white rounded-lg hover:bg-secondary-800 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Send className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ) : selectedUser ? (
            // User Selected but No Conversation Yet
            <div className="bg-white rounded-lg border border-secondary-200 flex flex-col h-96">
              <div className="flex-1 p-4 flex items-center justify-center">
                <div className="text-center">
                  <MessageSquare className="w-16 h-16 text-secondary-300 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-secondary-900 mb-2">Start New Conversation</h3>
                  <p className="text-secondary-500">
                    Type a message below to start a conversation with this user
                  </p>
                </div>
              </div>
              
              {/* Message Input */}
              <div className="p-4 border-t border-secondary-200">
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={messageText}
                    onChange={(e) => handleMessageTextChange(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    placeholder="Type your message..."
                    className="flex-1 px-3 py-2 border border-secondary-200 rounded-lg focus:ring-2 focus:ring-secondary-500 focus:border-transparent"
                  />
                  <button
                    onClick={handleSendMessage}
                    disabled={!messageText.trim()}
                    className="px-4 py-2 bg-secondary-900 text-white rounded-lg hover:bg-secondary-800 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Send className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ) : (
            // No Conversation Selected
            <div className="bg-white rounded-lg border border-secondary-200 h-96 flex items-center justify-center">
              <div className="text-center">
                <MessageSquare className="w-16 h-16 text-secondary-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-secondary-900 mb-2">No Conversation Selected</h3>
                <p className="text-secondary-500">
                  Select a conversation from the left or start a new conversation
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* New Conversation Modal */}
      {showNewConversationModal && (
        <NewConversationModal
          onClose={() => setShowNewConversationModal(false)}
          onStartConversation={(userId) => {
            setSelectedUser(userId);
            setViewMode('conversations');
            setShowNewConversationModal(false);
          }}
        />
      )}
    </div>
  );
};

export default MessagesPage;

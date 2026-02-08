import { api, getErrorMessage } from './api';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  intent?: string;
  created_at?: string;
}

export interface ChatResponse {
  reply: string;
  intent: string;
  sources: string[];
}

export interface ChatHistoryResponse {
  messages: ChatMessage[];
  count: number;
}

export interface ChatContext {
  article_id?: string;
}

export const chatService = {
  /**
   * Send a message to the AI chatbot
   */
  sendMessage: async (
    message: string,
    context?: ChatContext
  ): Promise<ChatResponse> => {
    try {
      const response = await api.post<ChatResponse>('/api/chat/message', {
        message,
        context: context || {},
      }, {
        timeout: 130_000,  // LLM responses can take 30-90s on CPU
      });
      return response.data;
    } catch (err) {
      throw new Error(getErrorMessage(err));
    }
  },

  /**
   * Get chat history for the current user
   */
  getHistory: async (limit: number = 20): Promise<ChatHistoryResponse> => {
    try {
      const response = await api.get<ChatHistoryResponse>('/api/chat/history', {
        params: { limit },
      });
      return response.data;
    } catch (err) {
      throw new Error(getErrorMessage(err));
    }
  },
};

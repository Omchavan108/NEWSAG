/**
 * Global event helper for opening the chatbot with article context.
 * Separated from ChatBot.tsx to satisfy react-refresh/only-export-components.
 */
export const openChatWithArticle = (articleId: string, articleTitle: string) => {
  window.dispatchEvent(
    new CustomEvent('openChatBot', {
      detail: { articleId, articleTitle },
    })
  );
};

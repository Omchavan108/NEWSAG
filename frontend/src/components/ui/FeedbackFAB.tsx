import React from 'react';
import { newsService } from '../../services/news.service';

interface FeedbackFABProps {
  onSuccess: (message: string) => void;
  onError: (message: string) => void;
}

export const FeedbackFAB: React.FC<FeedbackFABProps> = ({ onSuccess, onError }) => {
  const handleFeedbackClick = () => {
    const feedback = prompt("How can we improve NewsAura?");
    if (feedback) {
      newsService
        .submitFeedback(feedback)
        .then(() => onSuccess("Thanks for your feedback!"))
        .catch((err) => onError(err.message));
    }
  };

  return (
    <button 
      aria-label="Give feedback"
      onClick={handleFeedbackClick}
      className="fixed bottom-6 right-6 w-14 h-14 bg-indigo-600 text-white rounded-full shadow-2xl flex items-center justify-center hover:scale-110 active:scale-95 transition-all z-40 group"
    >
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
      </svg>
    </button>
  );
};

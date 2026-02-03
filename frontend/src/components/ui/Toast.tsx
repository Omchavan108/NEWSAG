import React from 'react';

interface ToastProps {
  message: string;
  type: 'error' | 'success';
  onClose: () => void;
}

export const Toast: React.FC<ToastProps> = ({ message, type, onClose }) => {
  return (
    <div 
      className={`fixed top-4 left-1/2 -translate-x-1/2 z-[100] px-6 py-3 rounded-2xl shadow-2xl flex items-center gap-3 animate-fade-in border ${
        type === 'error' 
          ? 'bg-rose-50 text-rose-700 border-rose-100 dark:bg-rose-900/40 dark:text-rose-400 dark:border-rose-800' 
          : 'bg-emerald-50 text-emerald-700 border-emerald-100 dark:bg-emerald-900/40 dark:text-emerald-400 dark:border-emerald-800'
      }`}
    >
      <div className={`w-2 h-2 rounded-full ${type === 'error' ? 'bg-rose-500' : 'bg-emerald-500'}`} />
      <p className="font-bold text-sm">{message}</p>
      <button 
        onClick={onClose} 
        className="ml-2 hover:opacity-70"
        aria-label="Close notification"
      >
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  );
};

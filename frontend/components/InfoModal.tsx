// frontend/components/InfoModal.tsx

'use client';

import { useEffect } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';

interface InfoModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

export const InfoModal: React.FC<InfoModalProps> = ({ isOpen, onClose, title, children }) => {
  // Блокируем скролл body при открытом модальном окне
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  // Закрытие по Escape
  useEffect(() => {
    if (!isOpen) return;
    
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 overflow-y-auto">
      {/* Оверлей (полупрозрачный фон) - упрощенная анимация */}
      <div
        onClick={onClose}
        className="fixed inset-0 bg-black/50 animate-in fade-in"
      />

      {/* Сама панель модального окна - упрощенная анимация */}
      <div className="relative w-full max-w-2xl max-h-[90vh] rounded-2xl bg-white dark:bg-neutral-800 shadow-xl animate-in fade-in slide-in-from-top-2 flex flex-col my-auto">
        {/* Заголовок - фиксированный */}
        <div className="flex items-start justify-between p-6 pb-4 border-b border-gray-200 dark:border-neutral-700 flex-shrink-0">
          <h3 className="text-lg font-medium leading-6 text-gray-900 dark:text-gray-100">
            {title}
          </h3>
          {/* Крестик в углу для закрытия */}
          <button 
            onClick={onClose} 
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors ml-4"
            aria-label="Закрыть"
          >
            <XMarkIcon className="w-6 h-6" />
          </button>
        </div>
        
        {/* Контент окна - скроллируемый */}
        <div className="flex-1 overflow-y-auto p-6 pt-4">
          <div className="text-sm text-gray-600 dark:text-gray-300 whitespace-pre-line">
            {children}
          </div>
        </div>

        {/* Кнопка закрытия - фиксированная */}
        <div className="p-6 pt-4 border-t border-gray-200 dark:border-neutral-700 flex justify-end flex-shrink-0">
          <button
            type="button"
            className="inline-flex justify-center rounded-md border border-transparent bg-blue-100 px-4 py-2 text-sm font-medium text-blue-900 hover:bg-blue-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 dark:bg-blue-900/50 dark:text-blue-200 dark:hover:bg-blue-900 transition-colors"
            onClick={onClose}
          >
            Закрыть
          </button>
        </div>
      </div>
    </div>
  );
};
// frontend/components/TendersPanel.tsx
'use client';
import { useEffect, useState } from 'react';
import { XMarkIcon } from '@heroicons/react/24/solid';
import { getTenders } from '@/services/api';
import { Tender } from '@/types';
import { TenderTable } from './TenderTable'; // Таблицу вынесем в отдельный компонент

export const TendersPanel: React.FC<{ isOpen: boolean; onClose: () => void }> = ({ isOpen, onClose }) => {
  const [tenders, setTenders] = useState<Tender[]>([]);

  // Загружаем данные только когда панель собирается открыться
  useEffect(() => {
    if (isOpen) {
      getTenders().then(setTenders);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <>
      {/* Оверлей (затемняющий фон) - упрощенная анимация через CSS */}
      <div
        onClick={onClose}
        className="fixed inset-0 bg-black/50 z-30 animate-in fade-in"
      />
      
      {/* Сама панель - упрощенная анимация через CSS */}
      <div
        className="fixed top-0 right-0 h-full w-full max-w-[90%] bg-gray-50 shadow-2xl z-40 p-6 flex flex-col dark:bg-neutral-900/90 dark:border-l dark:border-neutral-800 animate-in slide-in-from-right"
      >
            {/* Шапка панели */}
            <div className="flex items-center justify-between pb-4 border-b border-gray-200 dark:border-neutral-800 mb-6">
              <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100">Реестр тендеров</h2>
              <button onClick={onClose} className="p-1 rounded-full hover:bg-gray-200 dark:hover:bg-neutral-800">
                <XMarkIcon className="w-6 h-6 text-gray-600 dark:text-gray-200" />
              </button>
            </div>

            {/* Контент (наша таблица) */}
            <div className="flex-grow overflow-y-auto">
              <TenderTable tenders={tenders} />
            </div>
          </div>
    </>
  );
};
// frontend/components/TaskCard.tsx
'use client';

import { useState, memo } from 'react';
import { CalendarIcon, ClockIcon, ChevronDownIcon  } from '@heroicons/react/24/outline';
import { Task } from '../types';
import { formatDate, formatTime } from '../utils/formatters';
import clsx from 'clsx';

export const TaskCard: React.FC<{ task: Task }> = memo(({ task }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const urgencyClass = task.is_urgent
    ? 'border-red-400 bg-red-100'
    : 'border-yellow-400 bg-yellow-100';

  return (
    <div
      className={`
        p-5 rounded-xl shadow-lg border-l-4 
        transition-shadow duration-200 hover:shadow-xl
        ${urgencyClass} 
        h-full flex flex-col
      `}
    >
      {/* Верхняя часть: заказчик и статус "Срочно" */}
      <div className="flex items-center justify-between mb-2">
        <p className="text-xs font-semibold uppercase text-gray-500 tracking-wider">
          {task.customer}
        </p>
        {task.is_urgent && (
            <span className="text-xs font-bold text-red-700 bg-red-200/70 px-2.5 py-1 rounded-full animate-pulse">
              Срочно
            </span>
        )}
      </div>

      {/* Заголовок задачи */}
      <h3 className="text-lg font-bold text-gray-900 mb-4">
        {task.title}
      </h3>

      {/* КНОПКА "ПОДРОБНЕЕ" */}
      {task.details && (
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center justify-between w-full text-sm font-semibold text-blue-600 hover:text-blue-800 transition my-4 py-2 bg-blue-50/50 rounded-lg px-3"
        >
          <span>Подробнее</span>
          <ChevronDownIcon 
            className={clsx("w-5 h-5 transition-transform", { "transform rotate-180": isExpanded })}
          />
        </button>
      )}

      {/* БЛОК С ДЕТАЛЯМИ (упрощенная анимация через CSS) */}
      {isExpanded && task.details && (
        <div className="overflow-hidden animate-in fade-in slide-in-from-top-2">
          <div className="prose prose-sm max-w-none text-gray-700 bg-gray-50/50 p-3 rounded-md mb-4">
            <p className='whitespace-pre-line'>{task.details}</p>
          </div>
        </div>
      )}  
      {/* Нижняя часть: дата, время. Прижимается к низу. */}
      <div className="mt-auto pt-4 border-t border-gray-200/80 flex justify-between text-sm text-gray-700">
        <div className="flex items-center">
          <CalendarIcon className="w-4 h-4 mr-1.5 text-gray-500" />
          <span>{formatDate(task.deadline)}</span>
        </div>

        <div className="flex items-center">
          <ClockIcon className="w-4 h-4 mr-1.5 text-gray-500" />
          <span>{formatTime(task.deadline)}</span>
        </div>
      </div>
    </div>
  );
});

TaskCard.displayName = 'TaskCard';
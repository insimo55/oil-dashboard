// frontend/components/TaskCard.tsx
'use client';

import { useState } from 'react';
import { CalendarIcon, ClockIcon, ChevronDownIcon  } from '@heroicons/react/24/outline';
import { Task } from '../types';
import { formatDate, formatTime } from '../utils/formatters';
import { motion, AnimatePresence } from 'framer-motion';
import clsx from 'clsx';
import Image from 'next/image';

export const TaskCard: React.FC<{ task: Task }> = ({ task }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const urgencyClass = task.is_urgent
    ? 'border-red-400 bg-red-100 backdrop-blur-sm'
    : 'border-yellow-400 bg-yellow-100 backdrop-blur-sm';

  return (
    // Корневой div. Убрали MotionWrap. Добавили стили для выравнивания и эффектов.
    <div
      className={`
        p-5 rounded-xl shadow-lg border-l-4 
        transition-all duration-300 hover:shadow-xl hover:-translate-y-1 
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
            <div className="">
                <span className="text-xs font-bold text-red-700 bg-red-200/70 px-2.5 py-1 rounded-full">
                  Срочно
                </span>
                <Image src="/Alert.gif"  alt="attention animation" width={50} height={50} unoptimized className='absolute right-[20%] top-[4%]'/>
            </div>

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

      {/* АНИМИРОВАННЫЙ БЛОК С ДЕТАЛЯМИ */}
      <AnimatePresence>
        {isExpanded && task.details && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="overflow-hidden"
          >
            <div className="prose prose-sm max-w-none text-gray-700 bg-gray-50/50 p-3 rounded-md mb-4">
              <p className='whitespace-pre-line'>{task.details}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>  
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
};
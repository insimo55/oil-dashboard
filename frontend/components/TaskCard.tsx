// frontend/components/TaskCard.tsx

import { CalendarIcon, ClockIcon } from '@heroicons/react/24/outline';
import { Task } from '../types';
import { formatDate, formatTime } from '../utils/formatters';

export const TaskCard: React.FC<{ task: Task }> = ({ task }) => {
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
          <span className="text-xs font-bold text-red-700 bg-red-200/70 px-2.5 py-1 rounded-full">
            Срочно
          </span>
        )}
      </div>

      {/* Заголовок задачи */}
      <h3 className="text-lg font-bold text-gray-900 mb-4">
        {task.title}
      </h3>

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
// frontend/components/WellCard.tsx
'use client';
import { Well } from '../types';
import { ExclamationTriangleIcon, CheckCircleIcon, UsersIcon  } from '@heroicons/react/24/solid';
import Link from 'next/link'; 
import { MotionWrap } from './MotionWrap';
import { motion } from 'framer-motion';
import clsx from 'clsx';

// Компонент для отображения прогресс-бара
const ProgressBar: React.FC<{ current: number; total: number }> = ({ current, total }) => {
  const percentage = total > 0 ? (current / total) * 100 : 0;
  return (
    <div className="w-full bg-gray-200 rounded-full h-3">
      <motion.div 
        className="bg-gradient-to-r from-sky-500 to-blue-600 h-3 rounded-full" 
        initial={{ width: 0 }}
        animate={{ width: `${percentage}%` }}
        transition={{ duration: 1, ease: "easeInOut" }}
      />
    </div>
  );
};

export const WellCard: React.FC<{ well: Well }> = ({ well }) => {
  // Определяем "статус" скважины по наличию проблем
  const hasIssues = well.nvp_incidents.length > 0 || well.has_overspending;
  const statusColor = hasIssues ? 'border-red-500' : 'border-green-500';
  const engineerList = well.engineers ? well.engineers.split(',').map(name => name.trim()) : [];
  return (
    <MotionWrap>
    <Link href={`/wells/${well.id}`} className="block h-full">
        <div className={`bg-white backdrop-blur-sm rounded-xl shadow-lg p-5 border-l-4 ${statusColor} transition-transform duration-300 hover:scale-105`}>
          {/* Шапка карточки */}
          <div className="flex justify-between items-start mb-3">
            <h3 className="text-xl font-bold text-gray-800">{well.name}</h3>
            <div className="flex items-center gap-2">
          {well.nvp_incidents.length > 0 && (
            <div className="bg-red-100 text-red-800 text-xs font-bold px-2 py-1 rounded-full flex items-center gap-1">
              <ExclamationTriangleIcon className="w-4 h-4" />
              НВП: {well.nvp_incidents.length}
            </div>
          )}
          
        </div>
          </div>
          
          {/* Прогресс бурения */}
          <div className="mb-4">
            <div className="flex justify-between items-baseline mb-1 text-sm">
              <span className="font-semibold text-gray-700">Прогресс:</span>
              <span className="text-gray-600 font-mono">{well.current_depth}м / {well.planned_depth}м</span>
            </div>
            <ProgressBar current={well.current_depth} total={well.planned_depth} />
          </div>

          {/* Информация блоками */}
          
            {/* Блок с основной информацией */}
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Секция:</span>
                <span className="font-semibold text-gray-800">{well.current_section_display}</span>
              </div>
            </div>
            {/* НОВЫЙ БЛОК ДЛЯ ИНЖЕНЕРОВ */}
            {engineerList.length > 0 && (
              <div className="mt-4 pt-4 border-t border-gray-200/80">
                <div className="flex items-center text-sm text-gray-500 mb-2">
                  <UsersIcon className="w-5 h-5 mr-2" />
                  <span className="font-semibold">Инженерный состав:</span>
                </div>
                <ul className="space-y-1 text-sm text-gray-800 list-disc list-inside">
                  {engineerList.map((engineer, index) => (
                    <li key={index}>{engineer}</li>
                  ))}
                </ul>
              </div>
            )}
          
          {/* Текущие работы - ПРИЖИМАЕМ К НИЗУ */}
        <div className="mt-auto pt-4 border-t border-gray-200/80">
          <p className="text-xs text-gray-500 mb-1">Текущие работы:</p>
          <p className="text-gray-700">{well.current_operations || 'Нет данных'}</p>
        </div>
        </div>
    </Link>
    </MotionWrap>
  );
};
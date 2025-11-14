'use client'

import { getWellById } from '@/services/api'; // '@/' - это удобный псевдоним для корневой папки
import Link from 'next/link';
import { ArrowLeftIcon } from '@heroicons/react/24/solid';
import { formatDateTime } from '@/utils/formatters';
import { HourBadge } from '@/components/HourBadge';
import { formatDate } from '@/utils/formatters';
import Image from 'next/image';
import { Well } from '@/types';


  // Компонент для красивого отображения блоков "Да/Нет"
  const StatusBlock: React.FC<{ title: string; status: boolean; details: string | null }> = ({ title, status, details }) => (
    <div className={`p-4 rounded-lg ${
      status
        ? 'bg-red-50 border-l-4 border-red-500 dark:bg-red-900/20 dark:border-red-700'
        : 'bg-green-50 border-l-4 border-green-500 dark:bg-green-900/20 dark:border-green-700'
    }`}>
      <div className="flex items-center justify-between">
        <h4 className="font-semibold text-gray-700 dark:text-gray-300">{title}</h4>
        <span className={`px-3 py-1 text-sm font-bold rounded-full ${
          status
            ? 'bg-red-200 text-red-800 dark:bg-red-400/20 dark:text-red-300'
            : 'bg-green-200 text-green-800 dark:bg-green-400/20 dark:text-green-300'
        }`}>
          {status ? 'Да' : 'Нет'}
        </span>
      </div>
      {status && details && (
        <p className="mt-2 text-sm text-gray-600 dark:text-gray-300 bg-red-100 dark:bg-red-900/20 p-3 rounded-md">{details}</p>
      )}
    </div>
  );

// Эта страница, как и главная, будет асинхронным серверным компонентом
export const WellDetailContent: React.FC<{ well: Well | null }> = ({ well }) => {

  // Обработка случая, если скважина не найдена
  if (!well) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 dark:bg-neutral-900">
        <h1 className="text-4xl font-bold text-red-600 dark:text-red-400 mb-4">Ошибка 404</h1>
        <p className="text-lg text-gray-700 dark:text-gray-300 mb-8">Скважина не найдена.</p>
        <Link href="/" className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition">
          <ArrowLeftIcon className="w-5 h-5 mr-2" />
          Вернуться на главную
        </Link>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-gray-100 dark:bg-neutral-900 p-6 lg:p-10">
      <div className="max-w-4xl mx-auto">
        {/* Кнопка "Назад" */}
        <div className="mb-6">
          <Link href="/" className="inline-flex items-center text-blue-600 dark:text-blue-300 hover:underline">
            <ArrowLeftIcon className="w-5 h-5 mr-2" />
            К списку объектов
          </Link>
        </div>
        
        {/* Основной контент */}
        <div className="bg-white dark:bg-neutral-700/60 rounded-lg shadow-xl p-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">{well.name}</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">Последнее обновление: {formatDateTime(well.updated_at)}</p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Левая колонка */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 border-b dark:border-neutral-800 pb-2">Основная информация</h3>
              <div className="flex justify-between"><span>Текущий забой:</span><span className="font-semibold">{well.current_depth} м</span></div>
              <div className="flex justify-between"><span>Плановый забой:</span><span className="font-semibold">{well.planned_depth} м</span></div>
              <div className="flex justify-between"><span>Текущая секция:</span><span className="font-semibold">{well.current_section_display}</span></div>
              <div><span className="font-semibold">Инженерный состав:</span><p className="text-gray-700 dark:text-gray-300 mt-1">{well.engineers}</p></div>
              <div><span className="font-semibold">Текущие работы:</span><p className="text-gray-700 dark:text-gray-300 mt-1">{well.current_operations}</p></div>
              <div>{well.last_summary_text && (
                  <button 
                      onClick={() => alert(well.last_summary_text)} 
                      className="text-sm text-blue-600 hover:underline">
                      Показать последнюю сводку
                  </button>
              )}</div>
            </div>

            {/* Правая колонка */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 border-b dark:border-neutral-800 pb-2">Статус и Инциденты</h3>
              <div>
            <div className='flex flex-row items-center mb-2'>
              <h4 className="font-semibold text-gray-700 dark:text-gray-300 mb-3">
              Инциденты НВП ({well.nvp_incidents.length})
              
            </h4>
            <Image
                src="/angry_man.gif" // путь к файлу в public/gifs/time.gif
                alt="Clock animation"
                width={80}
                height={80}
                unoptimized // нужно, чтобы GIF-анимация не "замораживалась"
              />
            </div>
            {well.nvp_incidents.length > 0 ? (
              <div className="space-y-4">
                {well.nvp_incidents.map(incident => (
                  <div key={incident.id} className="bg-neutral-200 dark:bg-neutral-800/60 p-4 rounded-lg border border-neutral-300 dark:border-neutral-800">
                    <div className="flex justify-between items-center mb-2">
                      <p className="font-bold text-gray-800 dark:text-gray-100">
                        НВП от {formatDate(incident.incident_date)}
                      </p>
                      <HourBadge duration={incident.duration} /> 
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-300 whitespace-pre-line">
                      {incident.description}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500 dark:text-green-300 bg-green-50 dark:bg-green-900/20 p-4 rounded-lg border-green-200 dark:border-green-800 border">Инцидентов не зафиксировано.</p>
            )}
          </div>
              <StatusBlock title="Перерасход средств" status={well.has_overspending} details={well.overspending_details} />
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
// frontend/app/wells/[id]/page.tsx

import { getWellById } from '@/services/api'; // '@/' - это удобный псевдоним для корневой папки
import Link from 'next/link';
import { ArrowLeftIcon } from '@heroicons/react/24/solid';
import { formatDateTime } from '@/utils/formatters';
import { HourBadge } from '@/components/HourBadge';
import { formatDate } from '@/utils/formatters';

// Эта страница, как и главная, будет асинхронным серверным компонентом
export default async function WellDetailPage({ params }: { params: { id: string } }) {
  const well = await getWellById(params.id);

  // Обработка случая, если скважина не найдена
  if (!well) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
        <h1 className="text-4xl font-bold text-red-600 mb-4">Ошибка 404</h1>
        <p className="text-lg text-gray-700 mb-8">Скважина с ID: {params.id} не найдена.</p>
        <Link href="/" className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition">
          <ArrowLeftIcon className="w-5 h-5 mr-2" />
          Вернуться на главную
        </Link>
      </div>
    );
  }

  // Компонент для красивого отображения блоков "Да/Нет"
  const StatusBlock: React.FC<{ title: string; status: boolean; details: string | null }> = ({ title, status, details }) => (
    <div className={`p-4 rounded-lg ${status ? 'bg-red-50 border-l-4 border-red-500' : 'bg-green-50 border-l-4 border-green-500'}`}>
      <div className="flex items-center justify-between">
        <h4 className="font-semibold text-gray-700">{title}</h4>
        <span className={`px-3 py-1 text-sm font-bold rounded-full ${status ? 'bg-red-200 text-red-800' : 'bg-green-200 text-green-800'}`}>
          {status ? 'Да' : 'Нет'}
        </span>
      </div>
      {status && details && (
        <p className="mt-2 text-sm text-gray-600 bg-red-100 p-3 rounded-md">{details}</p>
      )}
    </div>
  );

  return (
    <main className="min-h-screen bg-gray-100 p-6 lg:p-10">
      <div className="max-w-4xl mx-auto">
        {/* Кнопка "Назад" */}
        <div className="mb-6">
          <Link href="/" className="inline-flex items-center text-blue-600 hover:underline">
            <ArrowLeftIcon className="w-5 h-5 mr-2" />
            К списку объектов
          </Link>
        </div>
        
        {/* Основной контент */}
        <div className="bg-white rounded-lg shadow-xl p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">{well.name}</h1>
          <p className="text-sm text-gray-500 mb-6">Последнее обновление: {formatDateTime(well.updated_at)}</p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Левая колонка */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-800 border-b pb-2">Основная информация</h3>
              <div className="flex justify-between"><span>Текущий забой:</span><span className="font-semibold">{well.current_depth} м</span></div>
              <div className="flex justify-between"><span>Плановый забой:</span><span className="font-semibold">{well.planned_depth} м</span></div>
              <div className="flex justify-between"><span>Текущая секция:</span><span className="font-semibold">{well.current_section_display}</span></div>
              <div><span className="font-semibold">Инженерный состав:</span><p className="text-gray-700 mt-1">{well.engineers}</p></div>
              <div><span className="font-semibold">Текущие работы:</span><p className="text-gray-700 mt-1">{well.current_operations}</p></div>
            </div>

            {/* Правая колонка */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-800 border-b pb-2">Статус и Инциденты</h3>
              <div>
            <h4 className="font-semibold text-gray-700 mb-3">
              Инциденты НВП ({well.nvp_incidents.length})
            </h4>
            {well.nvp_incidents.length > 0 ? (
              <div className="space-y-4">
                {well.nvp_incidents.map(incident => (
                  <div key={incident.id} className="bg-gray-50 p-4 rounded-lg border">
                    <div className="flex justify-between items-center mb-2">
                      <p className="font-bold text-gray-800">
                        НВП от {formatDate(incident.incident_date)}
                      </p>
                      <HourBadge duration={incident.duration} /> 
                    </div>
                    <p className="text-sm text-gray-600 whitespace-pre-line">
                      {incident.description}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500 bg-green-50 p-4 rounded-lg border-green-200 border">Инцидентов не зафиксировано.</p>
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
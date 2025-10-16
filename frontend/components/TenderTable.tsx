// frontend/components/TenderTable.tsx
'use client';
import { Tender, TenderStatus } from '@/types';
import { formatDateTime } from '@/utils/formatters';
import clsx from 'clsx';

const StatusBadge: React.FC<{ status: string; statusDisplay: string }> = ({ status, statusDisplay }) => {
  const colorClasses: Record<TenderStatus, string> = {
    PENDING: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-400/20 dark:text-yellow-300',
    TECH: 'bg-blue-100 text-blue-800 dark:bg-blue-400/20 dark:text-blue-300',
    COMMERCIAL: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-400/20 dark:text-indigo-300',
    CONVERSATION: 'bg-blue-100 text-blue-800 dark:bg-blue-400/20 dark:text-blue-300',
    WON: 'bg-green-100 text-green-800 dark:bg-green-400/20 dark:text-green-300',
    LOST: 'bg-red-100 text-red-800 dark:bg-red-400/20 dark:text-red-300',
    ARCHIVED: 'bg-gray-100 text-gray-800 dark:bg-gray-400/20 dark:text-gray-300',
  };
  return <span className={clsx('px-3 py-1 text-xs font-medium rounded-full', colorClasses[status as TenderStatus])}>{statusDisplay}</span>;
};

export const TenderTable: React.FC<{ tenders: Tender[] }> = ({ tenders }) => {
  if (tenders.length === 0) {
    return <p className="text-gray-500 text-center mt-10">Данных по тендерам пока нет.</p>;
  }
  
  return (
    // Убираем фон и тени, так как они теперь на родительской панели
    <div className="overflow-x-auto rounded-lg bg-white dark:bg-neutral-900/40 border border-gray-200 dark:border-neutral-800">
      <table className="min-w-full divide-y divide-gray-200 dark:divide-neutral-700">
        <thead className="bg-gray-100 dark:bg-neutral-800">
          <tr>
              <th className="px-6 py-3 text-left text-xs font-bold text-gray-600 dark:text-gray-300 uppercase tracking-wider">Наименование</th>
              <th className="px-6 py-3 text-left text-xs font-bold text-gray-600 dark:text-gray-300 uppercase tracking-wider">Этап</th>
              <th className="px-6 py-3 text-left text-xs font-bold text-gray-600 dark:text-gray-300 uppercase tracking-wider">Срок загрузки</th>
              <th className="px-6 py-3 text-left text-xs font-bold text-gray-600 dark:text-gray-300 uppercase tracking-wider">Пояснение</th>
            </tr>
        </thead>
        <tbody className="bg-white dark:bg-transparent divide-y divide-gray-200 dark:divide-neutral-800">
          {tenders.map((tender) => (
            <tr key={tender.id} className="hover:bg-gray-50 dark:hover:bg-neutral-800/60 transition odd:dark:bg-neutral-900/20 even:dark:bg-neutral-900/10">
              <td className="px-6 py-4 whitespace-nowrap font-semibold text-gray-800 dark:text-gray-100">{tender.name}</td>
                <td className="px-6 py-4 whitespace-nowrap"><StatusBadge status={tender.status} statusDisplay={tender.status_display} /></td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">
                  {tender.deadline ? formatDateTime(tender.deadline) : <span className="text-gray-400">—</span>}
                </td>
                <td className="px-6 py-4 text-sm text-gray-600 dark:text-gray-300 max-w-sm whitespace-pre-line">{tender.notes}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
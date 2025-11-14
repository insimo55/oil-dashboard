// frontend/app/page.tsx

'use client';

import { useState, useEffect } from 'react';
import { Well, Task } from '../types';
import { TaskCard } from '../components/TaskCard';
import { WellCard } from '../components/WellCard'; // <-- Импортируем новую карточку
import { getWells,getTasks  } from '../services/api'; 

import { TendersPanel } from '../components/TendersPanel';
import { DocumentTextIcon } from '@heroicons/react/24/outline';



export default function Home() {
  // Так как страница стала клиентской, данные грузим через useEffect
  const [wells, setWells] = useState<Well[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isTendersPanelOpen, setIsTendersPanelOpen] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      const [wellsData, tasksData] = await Promise.all([getWells(), getTasks()]);
      setWells(wellsData);
      setTasks(tasksData);
    };
    fetchData();
  }, []);

  const activeWells = wells.filter(well => well.is_active);
  const completedWells = wells.filter(well => !well.is_active);


  return (
    <main className="mx-auto px-6 lg:px-10 py-8 relative">
      {/* КНОПКА ОТКРЫТИЯ ПАНЕЛИ */}
      <div className="fixed top-20 right-0 z-20">
        <button 
          onClick={() => setIsTendersPanelOpen(true)}
          className="bg-white/80 backdrop-blur-sm p-4 rounded-l-xl shadow-lg hover:bg-blue-50 transition-colors dark:bg-neutral-800/80 dark:hover:bg-neutral-700/80"
          title="Реестр тендеров"
        >
          <DocumentTextIcon className="w-6 h-6 text-blue-600 dark:text-blue-300" />
        </button>
      </div>

      {/* НАША БУДУЩАЯ ПАНЕЛЬ */}
      <TendersPanel 
        isOpen={isTendersPanelOpen} 
        onClose={() => setIsTendersPanelOpen(false)} 
      />
      {/* БЛОК ЗАДАЧ */}
        <div className="mb-12">
        <h2 className="text-3xl font-bold tracking-tight text-gray-900 mb-6 dark:text-gray-100">
          🔥 Актуальные задачи
        </h2>
        <div 
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4 gap-6"
        >
          {tasks.map(task => (
            <div key={task.id}>
              <TaskCard task={task} />
            </div>
          ))}
        </div>
        {/* {tasks && tasks.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {tasks.map(task => (
              <TaskCard key={task.id} task={task} />
            ))}
          </div>
        ) : (
          <p className='text-gray-500'>Актуальных задач нет. Можно отдохнуть!</p>
        )} */}
      </div>


      <div>
        <h2 className="text-3xl font-bold tracking-tight text-gray-900 mb-6 dark:text-gray-100">
          🛢️ Объекты в работе
        </h2>
        <div 
          className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-8"
        >
          {activeWells.map(well => (
              <div key={well.id}>
                <WellCard well={well} />
              </div>
            ))}
        </div>
        {/* {wells && wells.length > 0 ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-8">
            {wells.map(well => (
              <WellCard key={well.id} well={well} />
            ))}
          </div>
        ) : (
          <p className='text-gray-500'>Нет данных по скважинам. Попробуйте добавить их в админ-панели.</p>
        )} */}
      </div>

      <div>
        <h2 className="text-3xl font-semibold tracking-tight text-gray-900 mt-6 mb-6 dark:text-gray-100">
          ✅ Завершенные объекты
        </h2>
        <div 
          className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-8"
        >
          {completedWells.map(well => (
              <div key={well.id}>
                <WellCard well={well} />
              </div>
            ))}
        </div>
        {/* {wells && wells.length > 0 ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-8">
            {wells.map(well => (
              <WellCard key={well.id} well={well} />
            ))}
          </div>
        ) : (
          <p className='text-gray-500'>Нет данных по скважинам. Попробуйте добавить их в админ-панели.</p>
        )} */}
      </div>
      
    </main>
  );
}
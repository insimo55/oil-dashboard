// frontend/app/page.tsx

'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Well, Task } from '../types';
import { TaskCard } from '../components/TaskCard';
import { WellCard } from '../components/WellCard'; // <-- Импортируем новую карточку
import { getWells,getTasks  } from '../services/api'; 

// Конфигурация анимации
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1, // Задержка между появлением дочерних элементов
    },
  },
};

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
    transition: { duration: 0.5 }
  },
};

export default function Home() {
  // Так как страница стала клиентской, данные грузим через useEffect
  const [wells, setWells] = useState<Well[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      const [wellsData, tasksData] = await Promise.all([getWells(), getTasks()]);
      setWells(wellsData);
      setTasks(tasksData);
    };
    fetchData();
  }, []);

  return (
    <div className="mx-auto px-6 lg:px-10 py-8">
      
      {/* БЛОК ЗАДАЧ */}
        <div className="mb-12">
        <h2 className="text-3xl font-bold tracking-tight text-gray-900 mb-6">
          🔥 Актуальные задачи
        </h2>
        <motion.div 
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4 gap-6"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {tasks.map(task => (
            <motion.div key={task.id} variants={itemVariants}>
              <TaskCard task={task} />
            </motion.div>
          ))}
        </motion.div>
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
        <h2 className="text-3xl font-bold tracking-tight text-gray-900 mb-6">
          🛢️ Объекты в работе
        </h2>
        <motion.div 
          className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-8"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {wells.map(well => (
            <motion.div key={well.id} variants={itemVariants}>
              <WellCard well={well} />
            </motion.div>
          ))}
        </motion.div>
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
      
    </div>
  );
}
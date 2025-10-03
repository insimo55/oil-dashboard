// frontend/components/MotionWrap.tsx
'use client'; // <-- Эта директива ОБЯЗАТЕЛЬНА!

import { motion } from 'framer-motion';

export const MotionWrap: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }} // Начальное состояние: прозрачный, смещен на 20px вниз
      animate={{ opacity: 1, y: 0 }}   // Конечное состояние: непрозрачный, на своем месте
      transition={{ duration: 0.5 }}     // Длительность анимации
      className={"h-full flex flex-col mt-auto"}
    >
      {children}
    </motion.div>
  );
};
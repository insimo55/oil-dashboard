// frontend/components/HourBadge.tsx
'use client';
import { ClockIcon } from '@heroicons/react/24/solid';

export const HourBadge: React.FC<{ duration: string }> = ({ duration }) => {
  // Если строка пустая, не рендерим ничего
  if (!duration) {
    return null;
  }

  return (
    <div className="flex items-center gap-2 bg-yellow-100 text-yellow-800 font-bold px-3 py-1.5 rounded-full text-sm">
      {/* Ты можешь вставить свою GIF с песочными часами сюда вместо иконки */}
      <ClockIcon className="w-5 h-5" />
      <span>{duration}</span>
    </div>
  );
};
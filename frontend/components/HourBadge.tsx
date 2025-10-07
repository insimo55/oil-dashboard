// frontend/components/HourBadge.tsx
'use client';
import { ClockIcon } from '@heroicons/react/24/solid';

export const HourBadge: React.FC<{ duration: string }> = ({ duration }) => {
  // Если строка пустая, не рендерим ничего
  if (!duration) {
    return null;
  }

  return (
    <div className="flex items-center gap-2 bg-red-300 text-yellow-900 font-bold px-3 py-1.5 rounded-full text-sm">
      
      <span className='text-[17px]'>{duration}</span>
    </div>
  );
};
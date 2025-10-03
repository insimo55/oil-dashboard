// frontend/utils/formatters.ts

import { format, parseISO } from 'date-fns';
import { ru } from 'date-fns/locale';

/**
 * Форматирует ISO-строку в дату вида "06.10.2025"
 * @param dateString - дата в формате ISO (например, "2025-10-06T14:00:00Z")
 */
export function formatDate(dateString: string): string {
  if (!dateString) return '';
  const date = parseISO(dateString); // Превращаем строку в объект Date
  return format(date, 'dd.MM.yyyy', { locale: ru });
}

/**
 * Форматирует ISO-строку во время вида "14:00"
 * @param dateString - дата в формате ISO
 */
export function formatTime(dateString: string): string {
  if (!dateString) return '';
  const date = parseISO(dateString);
  return format(date, 'HH:mm', { locale: ru });
}

/**
 * Форматирует ISO-строку в полную дату и время вида "06.10.2025, 17:00"
 * @param dateString - дата в формате ISO
 */
export function formatDateTime(dateString: string): string {
  if (!dateString) return '';
  const date = parseISO(dateString);
  return format(date, 'dd.MM.yyyy, HH:mm', { locale: ru });
}
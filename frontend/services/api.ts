// frontend/services/api.ts

import { Well, Task } from '../types';

// Получаем URL нашего API из переменных окружения
const API_URL = process.env.NEXT_PUBLIC_API_URL;

export async function getWells(): Promise<Well[]> {
  try {
    const response = await fetch(`${API_URL}/wells/`);
    
    if (!response.ok) {
      // Если сервер ответил ошибкой (например, 500)
      throw new Error('Failed to fetch wells data');
    }

    const data: Well[] = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching wells:", error);
    // В случае ошибки возвращаем пустой массив, чтобы приложение не "упало"
    return [];
  }
}

export async function getWellById(id: string): Promise<Well | null> {
  try {
    const response = await fetch(`${API_URL}/wells/${id}/`);
    
    if (!response.ok) {
      if (response.status === 404) {
        // Если скважина не найдена, это не ошибка, а ожидаемое поведение
        return null;
      }
      throw new Error('Failed to fetch well data');
    }

    const data: Well = await response.json();
    return data;
  } catch (error) {
    console.error(`Error fetching well with id ${id}:`, error);
    return null;
  }
}

export async function getTasks(): Promise<Task[]> {
  try {
    const response = await fetch(`${API_URL}/tasks/`);
    if (!response.ok) {
      throw new Error('Failed to fetch tasks');
    }
    return await response.json();
  } catch (error) {
    console.error("Error fetching tasks:", error);
    return [];
  }
}
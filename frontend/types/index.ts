// frontend/types/index.ts


export interface NVPIncident {
  id: number;
  incident_date: string; // "YYYY-MM-DD"
  duration: string;  
  description: string;
}

export interface Well {
  id: number;
  name: string;
  is_active: boolean;
  engineers: string;
  current_depth: number;
  planned_depth: number;
  current_section: string;
  // Это поле мы добавили в сериализаторе, помнишь?
  current_section_display: string; 
  current_operations: string;
  has_overspending: boolean;
  overspending_details: string | null;
  created_at: string; // ISO-строка даты
  updated_at: string; // ISO-строка даты
  nvp_incidents: NVPIncident[];
  last_summary_text: string | null;
}

export interface Task {
  id: number;
  title: string;
  customer: string;
  deadline: string; // ISO-строка
  is_completed: boolean;
  is_urgent: boolean;
  details: string | null;
}

export type TenderStatus = 'PENDING' | 'TECH' | 'COMMERCIAL' | 'CONVERSATION' | 'WON' | 'LOST' | 'ARCHIVED';
export interface Tender {
  id: number;
  name: string;
  status: TenderStatus;  
  status_display: string; // 'К загрузке', 'Тех. часть загружена', etc.
  deadline: string | null; // ISO-строка даты
  notes: string;
  created_at: string;
  updated_at: string;
}
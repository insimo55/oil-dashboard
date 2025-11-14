// frontend/app/wells/[id]/page.tsx

import { getWellById } from '@/services/api'; // '@/' - это удобный псевдоним для корневой папки
import { WellDetailContent } from '@/components/WellDetailContent'; 


export default async function WellDetailPage({ params }: { params: { id: string } }) {
  const well = await getWellById(params.id);

  return <WellDetailContent well={well} />;
}
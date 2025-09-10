'use client';

import { GameProvider } from '@/lib/gameContext';
import GameContainer from '@/components/game/GameContainer';

export default function Home() {
  return (
    <GameProvider>
      <GameContainer />
    </GameProvider>
  );
}

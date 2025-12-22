import { useState, useCallback } from 'react';

interface Use3DCardReturn {
  handleMouseMove: (e: React.MouseEvent<HTMLElement>) => void;
  handleMouseLeave: () => void;
  transform: string;
  style: React.CSSProperties;
}

export function use3DCard(intensity: number = 10): Use3DCardReturn {
  const [rotate, setRotate] = useState({ x: 0, y: 0 });

  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLElement>) => {
    const card = e.currentTarget;
    const rect = card.getBoundingClientRect();

    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const centerX = rect.width / 2;
    const centerY = rect.height / 2;

    const rotateX = (y - centerY) / intensity;
    const rotateY = (centerX - x) / intensity;

    setRotate({ x: rotateX, y: rotateY });
  }, [intensity]);

  const handleMouseLeave = useCallback(() => {
    setRotate({ x: 0, y: 0 });
  }, []);

  const transform = `perspective(1000px) rotateX(${rotate.x}deg) rotateY(${rotate.y}deg)`;

  const style: React.CSSProperties = {
    transform,
    transformStyle: 'preserve-3d',
    transition: 'transform 0.1s ease-out',
  };

  return {
    handleMouseMove,
    handleMouseLeave,
    transform,
    style,
  };
}

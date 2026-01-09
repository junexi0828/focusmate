import { useState, useCallback, useRef } from 'react';

interface Use3DCardReturn {
  handleMouseMove: (e: React.MouseEvent<HTMLElement>) => void;
  handleMouseLeave: () => void;
  transform: string;
  style: React.CSSProperties;
}

export function use3DCard(intensity: number = 20): Use3DCardReturn {
  const [rotate, setRotate] = useState({ x: 0, y: 0 });
  const [isHovering, setIsHovering] = useState(false);
  const rafRef = useRef<number | null>(null);

  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLElement>) => {
    if (rafRef.current) return;

    rafRef.current = requestAnimationFrame(() => {
      const card = e.currentTarget;
      const rect = card.getBoundingClientRect();

      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      const centerX = rect.width / 2;
      const centerY = rect.height / 2;

      const rotateX = ((y - centerY) / centerY) * -intensity;
      const rotateY = ((x - centerX) / centerX) * intensity;

      setRotate({ x: rotateX, y: rotateY });
      setIsHovering(true);
      rafRef.current = null;
    });
  }, [intensity]);

  const handleMouseLeave = useCallback(() => {
    setRotate({ x: 0, y: 0 });
    setIsHovering(false);
    if (rafRef.current) {
      cancelAnimationFrame(rafRef.current);
      rafRef.current = null;
    }
  }, []);

  const transform = `perspective(1000px) rotateX(${rotate.x}deg) rotateY(${rotate.y}deg) scale3d(${isHovering ? 1.02 : 1}, ${isHovering ? 1.02 : 1}, 1)`;

  const style: React.CSSProperties = {
    transform,
    transition: isHovering ? 'transform 0.1s ease-out' : 'transform 0.5s ease-out',
    willChange: 'transform',
    transformStyle: 'preserve-3d',
  };

  return {
    handleMouseMove,
    handleMouseLeave,
    transform,
    style,
  };
}

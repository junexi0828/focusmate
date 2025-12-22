import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface CursorPosition {
  x: number;
  y: number;
}

export function InteractiveCursor() {
  const [cursorPos, setCursorPos] = useState<CursorPosition>({ x: 0, y: 0 });
  const [trail, setTrail] = useState<CursorPosition[]>([]);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setCursorPos({ x: e.clientX, y: e.clientY });
      setTrail(prev => [...prev.slice(-8), { x: e.clientX, y: e.clientY }]);
      setIsVisible(true);
    };

    const handleMouseLeave = () => {
      setIsVisible(false);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseleave', handleMouseLeave);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, []);

  if (!isVisible) return null;

  return (
    <div className="pointer-events-none fixed inset-0 z-[9999]">
      {/* Main cursor */}
      <motion.div
        className="fixed w-5 h-5 rounded-full"
        style={{
          background: 'radial-gradient(circle, #7ED6E8, #F9A8D4)',
          mixBlendMode: 'difference',
        }}
        animate={{
          x: cursorPos.x - 10,
          y: cursorPos.y - 10,
        }}
        transition={{
          type: 'spring',
          damping: 30,
          stiffness: 200,
          mass: 0.5,
        }}
      />

      {/* Trail */}
      <AnimatePresence>
        {trail.map((pos, i) => (
          <motion.div
            key={`${pos.x}-${pos.y}-${i}`}
            className="fixed w-2 h-2 rounded-full bg-primary/50"
            initial={{
              x: pos.x - 4,
              y: pos.y - 4,
              opacity: 0.8,
              scale: 1,
            }}
            animate={{
              opacity: 0,
              scale: 0,
            }}
            exit={{
              opacity: 0,
            }}
            transition={{
              duration: 0.5,
              ease: 'easeOut',
            }}
          />
        ))}
      </AnimatePresence>
    </div>
  );
}

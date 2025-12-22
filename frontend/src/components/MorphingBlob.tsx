import { motion } from 'framer-motion';

interface MorphingBlobProps {
  className?: string;
  color?: string;
  duration?: number;
}

export function MorphingBlob({
  className = '',
  color = '#7ED6E8',
  duration = 8
}: MorphingBlobProps) {
  // Different blob shapes
  const shapes = [
    "M60,-60C80,-40,100,-20,100,0C100,20,80,40,60,60C40,80,20,100,0,100C-20,100,-40,80,-60,60C-80,40,-100,20,-100,0C-100,-20,-80,-40,-60,-60C-40,-80,-20,-100,0,-100C20,-100,40,-80,60,-60Z",
    "M40,-60C60,-50,90,-40,100,-20C110,0,100,20,80,30C60,40,30,40,0,40C-30,40,-60,40,-80,30C-100,20,-110,0,-100,-20C-90,-40,-60,-50,-40,-60C-20,-70,0,-80,20,-80C40,-80,20,-70,40,-60Z",
    "M50,-70C70,-60,95,-50,105,-30C115,-10,110,15,95,35C80,55,55,70,25,80C-5,90,-40,95,-65,85C-90,75,-105,50,-110,20C-115,-10,-110,-45,-90,-65C-70,-85,-35,-90,-5,-85C25,-80,30,-80,50,-70Z",
  ];

  return (
    <svg
      viewBox="0 0 200 200"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      <motion.path
        fill={color}
        animate={{
          d: shapes,
        }}
        transition={{
          repeat: Infinity,
          duration,
          ease: "easeInOut",
        }}
      />
    </svg>
  );
}

// Dual color morphing blob
export function DualMorphingBlob({ className = '' }: { className?: string }) {
  return (
    <div className={`relative ${className}`}>
      <MorphingBlob
        className="absolute inset-0 opacity-30"
        color="#7ED6E8"
        duration={10}
      />
      <MorphingBlob
        className="absolute inset-0 opacity-20"
        color="#F9A8D4"
        duration={12}
      />
    </div>
  );
}

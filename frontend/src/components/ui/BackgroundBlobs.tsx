import { useRef, useEffect } from "react";
import { motion, useMotionValue, useSpring, useTransform } from "framer-motion";

export function BackgroundBlobs() {
  const ref = useRef<HTMLDivElement>(null);

  // 1. Mouse Tracking
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  // 2. Smooth Spring Physics for Mouse Follow
  const springConfig = { damping: 20, stiffness: 200 };
  const springX = useSpring(mouseX, springConfig);
  const springY = useSpring(mouseY, springConfig);

  // 3. Parallax Offsets (Increased range for better visibility)
  const x1 = useTransform(springX, [0, window.innerWidth], [-250, 250]);
  const y1 = useTransform(springY, [0, window.innerHeight], [-150, 150]);

  const x2 = useTransform(springX, [0, window.innerWidth], [250, -250]);
  const y2 = useTransform(springY, [0, window.innerHeight], [150, -150]);

  const x3 = useTransform(springX, [0, window.innerWidth], [-150, 150]);
  const y3 = useTransform(springY, [0, window.innerHeight], [250, -250]);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      mouseX.set(e.clientX);
      mouseY.set(e.clientY);
    };

    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, [mouseX, mouseY]);

  return (
    <div ref={ref} className="absolute inset-0 overflow-hidden pointer-events-none">
      {/*
        Blob 1: Top Left
      */}
      <motion.div
        style={{ x: x1, y: y1 }}
        className="absolute -top-20 -left-20"
      >
        <motion.div
          className="w-[400px] h-[400px] bg-purple-400 rounded-full mix-blend-multiply filter blur-[120px] opacity-20"
          animate={{
            scale: [1, 1.4, 1],
            rotate: [0, 90, 0],
          }}
          transition={{
            duration: 5,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      </motion.div>

      {/* Blob 2: Top Right */}
      <motion.div
        style={{ x: x2, y: y2 }}
        className="absolute -top-20 -right-20"
      >
        <motion.div
          className="w-[400px] h-[400px] bg-yellow-300 rounded-full mix-blend-multiply filter blur-[120px] opacity-20"
          animate={{
            scale: [1, 1.5, 1],
            rotate: [0, -60, 0],
          }}
          transition={{
            duration: 6,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 0.5,
          }}
        />
      </motion.div>

      {/* Blob 3: Bottom Left */}
      <motion.div
        style={{ x: x3, y: y3 }}
        className="absolute -bottom-40 left-20"
      >
        <motion.div
          className="w-[500px] h-[500px] bg-pink-300 rounded-full mix-blend-multiply filter blur-[120px] opacity-20"
          animate={{
            scale: [1, 1.3, 1],
            rotate: [0, 45, 0],
            x: [0, 50, 0],
          }}
          transition={{
            duration: 7,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 1,
          }}
        />
      </motion.div>
    </div>
  );
}

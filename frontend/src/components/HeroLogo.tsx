import { useRef } from "react";
import {
  motion,
  useMotionTemplate,
  useMotionValue,
  useSpring,
} from "framer-motion";
import { useTheme } from "../hooks/useTheme";
import logoFull from "../assets/logo-full.png";
import darkLogoFull from "../assets/dark-logo-full.png";

const HALF_ROTATION_RANGE = 15; // Decreased for subtler effect on large element

export function HeroLogo() {
  const ref = useRef<HTMLDivElement>(null);
  const { theme } = useTheme();

  const x = useMotionValue(0);
  const y = useMotionValue(0);

  const xSpring = useSpring(x);
  const ySpring = useSpring(y);

  const transform = useMotionTemplate`rotateX(${xSpring}deg) rotateY(${ySpring}deg)`;

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement, MouseEvent>) => {
    if (!ref.current) return;

    const rect = ref.current.getBoundingClientRect();

    const width = rect.width;
    const height = rect.height;

    const mouseX = (e.clientX - rect.left) * 32.5;
    const mouseY = (e.clientY - rect.top) * 32.5;

    const rX = (mouseY / height - HALF_ROTATION_RANGE) * -1;
    const rY = mouseX / width - HALF_ROTATION_RANGE;

    x.set(rX);
    y.set(rY);
  };

  const handleMouseLeave = () => {
    x.set(0);
    y.set(0);
  };

  return (
    <motion.div
      ref={ref}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{
        transformStyle: "preserve-3d",
        transform,
      }}
      className="relative flex items-center justify-center -my-32 cursor-pointer"
    >
      <img
        src={theme === "dark" ? darkLogoFull : logoFull}
        alt="FocusMate"
        className="h-[35rem] object-contain drop-shadow-2xl transition-all duration-300"
        style={{
          transform: "translateZ(50px)",
        }}
        draggable={false}
      />
      {/* Glare Effect */}
      <div
        style={{
          transform: "translateZ(75px)",
        }}
        className="absolute inset-0 rounded-full bg-gradient-to-tr from-white/0 via-white/10 to-white/0 opacity-0 hover:opacity-100 transition-opacity duration-500 pointer-events-none mix-blend-overlay"
      />
    </motion.div>
  );
}

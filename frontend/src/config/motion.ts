/**
 * Motion Design System
 * Consistent animation configurations for framer-motion
 */

// Animation timing constants
export const MOTION_DURATION = {
  fast: 0.15,
  normal: 0.2,
  slow: 0.3,
  slower: 0.5,
} as const;

// Easing functions
export const MOTION_EASE = {
  easeOut: [0.0, 0.0, 0.2, 1],
  easeIn: [0.4, 0.0, 1, 1],
  easeInOut: [0.4, 0.0, 0.2, 1],
  spring: { type: "spring", stiffness: 300, damping: 30 },
} as const;

// Common transition configurations
export const transitions = {
  default: {
    duration: MOTION_DURATION.normal,
    ease: MOTION_EASE.easeOut,
  },
  fast: {
    duration: MOTION_DURATION.fast,
    ease: MOTION_EASE.easeOut,
  },
  slow: {
    duration: MOTION_DURATION.slow,
    ease: MOTION_EASE.easeInOut,
  },
  spring: MOTION_EASE.spring,
} as const;

// Reusable animation variants
export const fadeIn = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
  transition: transitions.default,
};

export const slideUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
  transition: transitions.default,
};

export const slideDown = {
  initial: { opacity: 0, y: -20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: 20 },
  transition: transitions.default,
};

export const scaleIn = {
  initial: { opacity: 0, scale: 0.95 },
  animate: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.95 },
  transition: transitions.spring,
};

export const slideInFromLeft = {
  initial: { opacity: 0, x: -20 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: 20 },
  transition: transitions.default,
};

export const slideInFromRight = {
  initial: { opacity: 0, x: 20 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: -20 },
  transition: transitions.default,
};

// Stagger animations
export const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.1,
    },
  },
};

export const staggerItem = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
};

// Page transition variants
export const pageTransition = {
  initial: { opacity: 0, x: -10 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: 10 },
  transition: transitions.fast,
};

// Modal/Dialog variants
export const modalBackdrop = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
  transition: transitions.fast,
};

export const modalContent = {
  initial: { opacity: 0, scale: 0.95, y: 20 },
  animate: { opacity: 1, scale: 1, y: 0 },
  exit: { opacity: 0, scale: 0.95, y: 20 },
  transition: transitions.spring,
};

// Hover animations
export const hoverScale = {
  whileHover: { scale: 1.05 },
  whileTap: { scale: 0.95 },
  transition: transitions.fast,
};

export const hoverLift = {
  whileHover: { y: -2 },
  transition: transitions.fast,
};

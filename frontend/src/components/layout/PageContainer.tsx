import React from "react";
import { cn } from "../../utils";
import { motion } from "framer-motion";

interface PageContainerProps {
  children: React.ReactNode;
  className?: string;
}

export function PageContainer({ children, className }: PageContainerProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className={cn(
        "flex-1 m-4 min-h-[calc(100vh-2rem)] h-auto rounded-[2rem]",
        "border border-white/10 dark:border-white/5",
        "bg-white/40 dark:bg-black/40 backdrop-blur-3xl",
        "shadow-2xl",
        className
      )}
    >
      {children}
    </motion.div>
  );
}

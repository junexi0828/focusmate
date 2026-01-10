import React from "react";
import { cn } from "../../utils";

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  variant?: "default" | "interactive";
}

export function GlassCard({
  children,
  className,
  variant = "default",
  ...props
}: GlassCardProps) {
  return (
    <div
      className={cn(
        // Base glass styles
        "bg-white/70 dark:bg-black/60 backdrop-blur-md",
        "border border-white/20 dark:border-white/10",
        "shadow-sm rounded-xl",
        // Interactive variant
        variant === "interactive" && "hover:shadow-md transition-all duration-200 cursor-pointer",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

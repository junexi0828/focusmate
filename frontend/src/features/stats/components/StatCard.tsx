import React from "react";
import { Card, CardContent } from "../../../components/ui/card";
import { LucideIcon } from "lucide-react";
import { cn } from "../../../components/ui/utils";

interface StatCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  variant?: "default" | "primary" | "secondary" | "muted";
  className?: string;
}

export function StatCard({
  title,
  value,
  icon: Icon,
  trend,
  variant = "default",
  className,
}: StatCardProps) {
  const variantStyles = {
    default: "bg-background border",
    primary: "bg-primary/10 border-primary/20",
    secondary: "bg-secondary/10 border-secondary/20",
    muted: "bg-muted border",
  };

  const textStyles = {
    default: "text-foreground",
    primary: "text-primary",
    secondary: "text-secondary",
    muted: "text-muted-foreground",
  };

  return (
    <Card className={cn("hover:shadow-md transition-shadow", variantStyles[variant], className)}>
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2">
              <Icon
                className={cn(
                  "w-4 h-4 flex-shrink-0",
                  variant === "primary" && "text-primary",
                  variant === "secondary" && "text-secondary",
                  variant === "default" && "text-muted-foreground"
                )}
              />
              <p className="text-sm text-muted-foreground truncate">{title}</p>
            </div>
            <p
              className={cn(
                "text-2xl sm:text-3xl font-bold",
                textStyles[variant]
              )}
            >
              {value}
            </p>
            {trend && (
              <div
                className={cn(
                  "flex items-center gap-1 mt-2 text-xs",
                  trend.isPositive ? "text-green-600" : "text-red-600"
                )}
              >
                <span>{trend.isPositive ? "↑" : "↓"}</span>
                <span>{Math.abs(trend.value)}%</span>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}


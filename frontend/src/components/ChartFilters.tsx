import { motion } from "framer-motion";
import { Filter, X } from "lucide-react";
import { useState } from "react";
import { DateRange } from "react-day-picker";
import { DateRangePicker } from "./DateRangePicker";
import { Button } from "./ui/button-enhanced";

interface ChartFiltersProps {
  onFilterChange: (filters: {
    sessionType: string[];
    dateRange?: DateRange;
  }) => void;
}

export function ChartFilters({ onFilterChange }: ChartFiltersProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedTypes, setSelectedTypes] = useState<string[]>(["all"]);
  const [dateRange, setDateRange] = useState<DateRange | undefined>();

  const sessionTypes = [
    { value: "all", label: "전체" },
    { value: "pomodoro", label: "포모도로 (25분)" },
    { value: "short", label: "단기 집중 (15분)" },
    { value: "long", label: "장기 집중 (50분)" },
    { value: "break", label: "휴식" },
  ];

  const handleTypeToggle = (type: string) => {
    let newTypes: string[];
    if (type === "all") {
      newTypes = ["all"];
    } else {
      newTypes = selectedTypes.filter((t) => t !== "all");
      if (selectedTypes.includes(type)) {
        newTypes = newTypes.filter((t) => t !== type);
      } else {
        newTypes = [...newTypes, type];
      }
      if (newTypes.length === 0) {
        newTypes = ["all"];
      }
    }
    setSelectedTypes(newTypes);
    onFilterChange({ sessionType: newTypes, dateRange });
  };

  const handleDateRangeChange = (range: DateRange | undefined) => {
    setDateRange(range);
    onFilterChange({ sessionType: selectedTypes, dateRange: range });
  };

  const handleReset = () => {
    setSelectedTypes(["all"]);
    setDateRange(undefined);
    onFilterChange({ sessionType: ["all"], dateRange: undefined });
  };

  const hasActiveFilters =
    selectedTypes.length > 1 ||
    (selectedTypes.length === 1 && selectedTypes[0] !== "all") ||
    dateRange !== undefined;

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => setIsOpen(!isOpen)}
          className="gap-2"
        >
          <Filter className="h-4 w-4" />
          필터
          {hasActiveFilters && (
            <span className="ml-1 px-1.5 py-0.5 text-xs bg-primary text-primary-foreground rounded-full">
              {selectedTypes.filter((t) => t !== "all").length +
                (dateRange ? 1 : 0)}
            </span>
          )}
        </Button>

        {hasActiveFilters && (
          <Button
            variant="ghost"
            size="sm"
            onClick={handleReset}
            className="gap-2"
          >
            <X className="h-4 w-4" />
            초기화
          </Button>
        )}
      </div>

      {isOpen && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          exit={{ opacity: 0, height: 0 }}
          className="rounded-lg border border-border bg-card p-4 space-y-4"
        >
          {/* Session Type Filter */}
          <div>
            <h4 className="text-sm font-medium mb-3">세션 유형</h4>
            <div className="flex flex-wrap gap-2">
              {sessionTypes.map((type) => (
                <button
                  key={type.value}
                  onClick={() => handleTypeToggle(type.value)}
                  className={`px-3 py-1.5 text-sm rounded-md border transition-colors ${
                    selectedTypes.includes(type.value)
                      ? "bg-primary text-primary-foreground border-primary"
                      : "bg-background border-border hover:bg-accent"
                  }`}
                >
                  {type.label}
                </button>
              ))}
            </div>
          </div>

          {/* Date Range Filter */}
          <div>
            <h4 className="text-sm font-medium mb-3">날짜 범위</h4>
            <DateRangePicker
              dateRange={dateRange}
              onDateRangeChange={handleDateRangeChange}
            />
          </div>
        </motion.div>
      )}
    </div>
  );
}

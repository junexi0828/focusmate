"use client";

import * as React from "react";
import { add, format } from "date-fns";
import { Calendar as CalendarIcon, Clock } from "lucide-react";

import { cn } from "@/utils";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface DateTimePickerProps {
  date: Date | undefined;
  setDate: (date: Date | undefined) => void;
  className?: string;
  placeholder?: string;
}

export function DateTimePicker({
  date,
  setDate,
  className,
  placeholder = "날짜와 시간을 선택하세요",
}: DateTimePickerProps) {
  const [selectedDateTime, setSelectedDateTime] = React.useState<Date | undefined>(
    date
  );

  // Sync internal state with prop
  React.useEffect(() => {
    setSelectedDateTime(date);
  }, [date]);

  const handleSelect = (selectedDate: Date | undefined) => {
    if (selectedDate) {
      const newDate = new Date(selectedDate);
      if (selectedDateTime) {
        newDate.setHours(selectedDateTime.getHours());
        newDate.setMinutes(selectedDateTime.getMinutes());
      } else {
        // Default to current time if no time was selected previously
        const now = new Date();
        newDate.setHours(now.getHours());
        newDate.setMinutes(now.getMinutes());
      }
      setSelectedDateTime(newDate);
      setDate(newDate);
    } else {
      setSelectedDateTime(undefined);
      setDate(undefined);
    }
  };

  const handleTimeChange = (type: "hour" | "minute", value: string) => {
    if (!selectedDateTime) return;

    const newDate = new Date(selectedDateTime);
    if (type === "hour") {
      newDate.setHours(parseInt(value));
    } else {
      newDate.setMinutes(parseInt(value));
    }
    setSelectedDateTime(newDate);
    setDate(newDate);
  };

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button
          variant={"outline"}
          className={cn(
            "w-full justify-start text-left font-normal h-12",
            !date && "text-muted-foreground",
            className
          )}
        >
          <CalendarIcon className="mr-2 h-4 w-4" />
          {date ? (
            format(date, "PPP p") // e.g. "Oct 12, 2024 at 5:00 PM" (locale dependent usually)
          ) : (
            <span>{placeholder}</span>
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-auto p-0" align="start">
        <div className="p-3 border-b border-border">
          <Calendar
            mode="single"
            selected={selectedDateTime}
            onSelect={handleSelect}
            initialFocus
          />
        </div>
        <div className="p-3 flex items-center gap-2">
          <Clock className="w-4 h-4 text-muted-foreground" />
          <Select
            disabled={!selectedDateTime}
            value={selectedDateTime ? selectedDateTime.getHours().toString() : undefined}
            onValueChange={(val) => handleTimeChange("hour", val)}
          >
            <SelectTrigger className="w-[70px]">
              <SelectValue placeholder="시" />
            </SelectTrigger>
            <SelectContent position="popper" className="max-h-[200px]">
              {Array.from({ length: 24 }).map((_, i) => (
                <SelectItem key={i} value={i.toString()}>
                  {i.toString().padStart(2, "0")}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <span className="text-muted-foreground">:</span>
          <Select
            disabled={!selectedDateTime}
            value={selectedDateTime ? selectedDateTime.getMinutes().toString() : undefined}
            onValueChange={(val) => handleTimeChange("minute", val)}
          >
            <SelectTrigger className="w-[70px]">
              <SelectValue placeholder="분" />
            </SelectTrigger>
            <SelectContent position="popper" className="max-h-[200px]">
              {Array.from({ length: 12 }).map((_, i) => (
                <SelectItem key={i * 5} value={(i * 5).toString()}>
                  {(i * 5).toString().padStart(2, "0")}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </PopoverContent>
    </Popover>
  );
}

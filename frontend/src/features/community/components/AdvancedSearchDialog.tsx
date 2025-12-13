import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../../../components/ui/dialog";
import { Button } from "../../../components/ui/button-enhanced";
import { Input } from "../../../components/ui/input";
import { Label } from "../../../components/ui/label";
import { Filter, X } from "lucide-react";
import { Badge } from "../../../components/ui/badge";

interface AdvancedSearchDialogProps {
  authorUsername: string;
  dateFrom: string;
  dateTo: string;
  onAuthorUsernameChange: (value: string) => void;
  onDateFromChange: (value: string) => void;
  onDateToChange: (value: string) => void;
  onClear: () => void;
}

export function AdvancedSearchDialog({
  authorUsername,
  dateFrom,
  dateTo,
  onAuthorUsernameChange,
  onDateFromChange,
  onDateToChange,
  onClear,
}: AdvancedSearchDialogProps) {
  const [open, setOpen] = useState(false);
  const hasFilters = authorUsername || dateFrom || dateTo;

  const handleClear = () => {
    onClear();
    setOpen(false);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" className="relative">
          <Filter className="w-4 h-4 mr-2" />
          고급 검색
          {hasFilters && (
            <Badge
              variant="default"
              className="ml-2 h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs"
            >
              {[authorUsername, dateFrom, dateTo].filter(Boolean).length}
            </Badge>
          )}
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>고급 검색</DialogTitle>
          <DialogDescription>
            작성자, 날짜 범위로 게시글을 검색할 수 있습니다
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-6 py-4">
          {/* Author Username Filter */}
          <div className="space-y-2">
            <Label htmlFor="author-username">작성자</Label>
            <Input
              id="author-username"
              placeholder="작성자 이름을 입력하세요"
              value={authorUsername}
              onChange={(e) => onAuthorUsernameChange(e.target.value)}
            />
            <p className="text-xs text-muted-foreground">
              작성자 이름으로 게시글을 필터링합니다
            </p>
          </div>

          {/* Date Range Filters */}
          <div className="space-y-4">
            <Label>날짜 범위</Label>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="date-from" className="text-sm">
                  시작일
                </Label>
                <Input
                  id="date-from"
                  type="date"
                  value={dateFrom}
                  onChange={(e) => onDateFromChange(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="date-to" className="text-sm">
                  종료일
                </Label>
                <Input
                  id="date-to"
                  type="date"
                  value={dateTo}
                  onChange={(e) => onDateToChange(e.target.value)}
                  min={dateFrom || undefined}
                />
              </div>
            </div>
            <p className="text-xs text-muted-foreground">
              특정 기간에 작성된 게시글만 표시합니다
            </p>
          </div>

          {/* Active Filters Display */}
          {hasFilters && (
            <div className="space-y-2">
              <Label className="text-sm">적용된 필터</Label>
              <div className="flex flex-wrap gap-2">
                {authorUsername && (
                  <Badge variant="secondary" className="gap-1">
                    작성자: {authorUsername}
                    <button
                      onClick={() => onAuthorUsernameChange("")}
                      className="ml-1 hover:bg-muted rounded-full p-0.5"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </Badge>
                )}
                {dateFrom && (
                  <Badge variant="secondary" className="gap-1">
                    시작: {dateFrom}
                    <button
                      onClick={() => onDateFromChange("")}
                      className="ml-1 hover:bg-muted rounded-full p-0.5"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </Badge>
                )}
                {dateTo && (
                  <Badge variant="secondary" className="gap-1">
                    종료: {dateTo}
                    <button
                      onClick={() => onDateToChange("")}
                      className="ml-1 hover:bg-muted rounded-full p-0.5"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </Badge>
                )}
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-end gap-2 pt-4 border-t">
            {hasFilters && (
              <Button variant="outline" onClick={handleClear}>
                필터 초기화
              </Button>
            )}
            <Button variant="primary" onClick={() => setOpen(false)}>
              적용
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}


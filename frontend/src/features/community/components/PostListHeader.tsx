import { Input } from "../../../components/ui/input";
import { Button } from "../../../components/ui/button-enhanced";
import { Search, PlusCircle } from "lucide-react";
import {
  Tabs,
  TabsList,
  TabsTrigger,
} from "../../../components/ui/tabs";
import { AdvancedSearchDialog } from "./AdvancedSearchDialog";

interface PostListHeaderProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  selectedCategory: string;
  onCategoryChange: (category: string) => void;
  onCreatePost: () => void;
  authorUsername: string;
  dateFrom: string;
  dateTo: string;
  onAuthorUsernameChange: (value: string) => void;
  onDateFromChange: (value: string) => void;
  onDateToChange: (value: string) => void;
  onClearAdvancedFilters: () => void;
}

export function PostListHeader({
  searchQuery,
  onSearchChange,
  selectedCategory,
  onCategoryChange,
  onCreatePost,
  authorUsername,
  dateFrom,
  dateTo,
  onAuthorUsernameChange,
  onDateFromChange,
  onDateToChange,
  onClearAdvancedFilters,
}: PostListHeaderProps) {
  return (
    <div className="sticky top-0 z-10 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b">
      <div className="container mx-auto px-4 py-4">
        {/* 상단: 검색 + 고급 검색 + 새 게시글 버튼 */}
        <div className="flex flex-col sm:flex-row gap-4 mb-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="게시글 검색..."
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              className="pl-10"
            />
          </div>
          <div className="flex gap-2 flex-shrink-0">
            <AdvancedSearchDialog
              authorUsername={authorUsername}
              dateFrom={dateFrom}
              dateTo={dateTo}
              onAuthorUsernameChange={onAuthorUsernameChange}
              onDateFromChange={onDateFromChange}
              onDateToChange={onDateToChange}
              onClear={onClearAdvancedFilters}
            />
            <Button onClick={onCreatePost}>
              <PlusCircle className="w-4 h-4 mr-2" />
              새 게시글
            </Button>
          </div>
        </div>

        {/* 하단: 카테고리 탭 (Discourse 스타일) */}
        <Tabs
          value={selectedCategory}
          onValueChange={onCategoryChange}
          className="w-full"
        >
          <TabsList className="w-full justify-start bg-muted/50">
            <TabsTrigger value="all" className="flex-1 sm:flex-none">
              전체
            </TabsTrigger>
            <TabsTrigger value="tips" className="flex-1 sm:flex-none">
              팁
            </TabsTrigger>
            <TabsTrigger value="achievement" className="flex-1 sm:flex-none">
              성취
            </TabsTrigger>
            <TabsTrigger value="question" className="flex-1 sm:flex-none">
              질문
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>
    </div>
  );
}


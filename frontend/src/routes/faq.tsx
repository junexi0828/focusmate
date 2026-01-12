import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "../components/ui/accordion";
import { Input } from "../components/ui/input";
import { Button } from "../components/ui/button";
import {
  Search,
  HelpCircle,
  MessageCircle,
  Settings,
  Zap,
  Mail,
  ChevronRight,
} from "lucide-react";

export const Route = createFileRoute("/faq")({
  component: FAQPage,
});

const faqs = [
  {
    id: "general-1",
    category: "general",
    question: "FocusMate는 어떤 서비스인가요?",
    answer:
      "FocusMate는 실시간으로 친구, 동료들과 함께 집중할 수 있는 온라인 코워킹 스페이스입니다. 포모도로 타이머를 기반으로 서로의 집중 상태를 확인하고, 함께 목표를 달성할 수 있도록 돕습니다.",
  },
  {
    id: "general-2",
    category: "general",
    question: "무료로 사용할 수 있나요?",
    answer:
      "네, FocusMate의 핵심 기능은 무료로 제공됩니다. 친구 초대, 그룹 생성, 타이머 사용 등 기본적인 기능을 마음껏 이용하실 수 있습니다.",
  },
  {
    id: "feature-1",
    category: "features",
    question: "핑크캠퍼스가 무엇인가요?",
    answer:
      "핑크캠퍼스는 FocusMate 내의 특별한 커뮤니티 공간입니다. 비슷한 목표를 가진 사람들과 매칭되어 함께 공부하거나 작업할 수 있는 가상의 캠퍼스입니다.",
  },
  {
    id: "feature-2",
    category: "features",
    question: "타이머는 어떻게 설정하나요?",
    answer:
      "메인 화면의 타이머 위젯에서 직접 시간을 설정하거나, 프리셋(25분, 50분 등)을 클릭하여 간편하게 시작할 수 있습니다. 설정 페이지에서 기본 집중 시간과 휴식 시간을 변경할 수 있습니다.",
  },
  {
    id: "account-1",
    category: "account",
    question: "비밀번호를 잊어버렸어요.",
    answer:
      "로그인 페이지 하단의 '비밀번호 재설정' 링크를 통해 가입한 이메일로 비밀번호 변경 링크를 받으실 수 있습니다.",
  },
  {
    id: "tech-1",
    category: "technical",
    question: "알림이 오지 않아요.",
    answer:
      "브라우저의 알림 권한이 허용되어 있는지 확인해주세요. 또한 FocusMate 설정 페이지에서 '소리 알림' 및 '데스크탑 알림'이 켜져 있는지 확인해보세요.",
  },
  {
    id: "tech-2",
    category: "technical",
    question: "모바일에서도 사용할 수 있나요?",
    answer:
      "네, FocusMate는 반응형 웹 디자인을 지원하여 스마트폰과 태블릿에서도 쾌적하게 이용하실 수 있습니다.",
  },
];

const categories = [
  { id: "all", label: "전체", icon: Zap },
  { id: "general", label: "일반", icon: HelpCircle },
  { id: "features", label: "기능", icon: Settings },
  { id: "account", label: "계정", icon: MessageCircle },
  { id: "technical", label: "기술지원", icon: Zap },
];

function FAQPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [activeCategory, setActiveCategory] = useState("all");

  const filteredFaqs = faqs.filter((faq) => {
    const matchesSearch =
      faq.question.toLowerCase().includes(searchTerm.toLowerCase()) ||
      faq.answer.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory =
      activeCategory === "all" || faq.category === activeCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <div className="relative bg-gradient-to-b from-[#E0F7FD]/50 to-background dark:from-slate-900 dark:to-background pt-24 pb-12 px-4">
        <div className="container mx-auto max-w-4xl text-center space-y-6">
          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-[#7ED6E8] to-[#F9A8D4] bg-clip-text text-transparent pb-2">
            자주 묻는 질문
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            FocusMate 사용에 대해 궁금한 점이 있으신가요? <br className="hidden sm:block" />
            자주 묻는 질문들을 모아두었습니다.
          </p>

          {/* Search Bar */}
          <div className="max-w-xl mx-auto relative mt-8">
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
              <Search className="w-5 h-5" />
            </div>
            <Input
              type="text"
              placeholder="질문을 검색해보세요..."
              className="pl-10 py-6 text-lg bg-background/50 backdrop-blur-sm border-2 focus-visible:ring-[#7ED6E8] focus-visible:border-[#7ED6E8] transition-all rounded-2xl shadow-sm"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 max-w-4xl py-12">
        {/* Category Filters */}
        <div className="flex flex-wrap gap-2 justify-center mb-12">
          {categories.map((category) => {
            const Icon = category.icon;
            const isActive = activeCategory === category.id;
            return (
              <Button
                key={category.id}
                variant={isActive ? "default" : "outline"}
                onClick={() => setActiveCategory(category.id)}
                className={`rounded-full px-6 transition-all duration-300 ${
                  isActive
                    ? "bg-gradient-to-r from-[#7ED6E8] to-[#F9A8D4] border-transparent hover:opacity-90 text-white shadow-md transform scale-105"
                    : "hover:border-[#7ED6E8] hover:text-[#7ED6E8]"
                }`}
              >
                <Icon className="w-4 h-4 mr-2" />
                {category.label}
              </Button>
            );
          })}
        </div>

        {/* FAQ List */}
        <div className="bg-card/50 backdrop-blur-sm rounded-3xl border shadow-sm p-6 md:p-8">
          {filteredFaqs.length > 0 ? (
            <Accordion type="single" collapsible className="space-y-4">
              {filteredFaqs.map((faq) => (
                <AccordionItem
                  key={faq.id}
                  value={faq.id}
                  className="border rounded-xl px-4 data-[state=open]:bg-muted/50 data-[state=open]:border-[#7ED6E8]/30 transition-all duration-200"
                >
                  <AccordionTrigger className="text-left font-medium text-lg hover:no-underline py-4 hover:text-[#7ED6E8] transition-colors">
                    {faq.question}
                  </AccordionTrigger>
                  <AccordionContent className="text-muted-foreground leading-relaxed text-base pb-4">
                    {faq.answer}
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
          ) : (
            <div className="text-center py-12 text-muted-foreground">
              <HelpCircle className="w-12 h-12 mx-auto mb-4 opacity-20" />
              <p className="text-lg font-medium">검색 결과가 없습니다.</p>
              <p>다른 검색어를 입력해보세요.</p>
            </div>
          )}
        </div>

        {/* Contact Support Section */}
        <div className="mt-16 text-center bg-gradient-to-br from-[#E0F7FD] to-[#FCE7F5] dark:from-slate-800 dark:to-slate-900 rounded-3xl p-8 md:p-12 relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-12 opacity-10 transform translate-x-1/2 -translate-y-1/2 group-hover:rotate-12 transition-transform duration-700">
            <Mail className="w-64 h-64" />
          </div>

          <div className="relative z-10 space-y-4">
            <h3 className="text-2xl font-bold">아직 궁금한 점이 있으신가요?</h3>
            <p className="text-muted-foreground max-w-md mx-auto">
              원하시는 답변을 찾지 못하셨다면 언제든지 문의해주세요.<br/>
              FocusMate 팀이 빠르고 친절하게 답변해 드립니다.
            </p>
            <div className="pt-4">
              <Button
                size="lg"
                className="rounded-full bg-white text-black hover:bg-gray-50 border shadow-lg dark:bg-slate-950 dark:text-white dark:hover:bg-slate-900 group"
                onClick={() => window.location.href = 'mailto:support@focusmate.com'}
              >
                <Mail className="w-4 h-4 mr-2 group-hover:scale-110 transition-transform" />
                문의하기
                <ChevronRight className="w-4 h-4 ml-1 opacity-50 group-hover:translate-x-1 transition-transform" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

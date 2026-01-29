import { createFileRoute } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { Timer, Users, Trophy, Heart } from "lucide-react";
import { PageTransition } from "../components/PageTransition";
import { Card } from "../components/ui/card";

export const Route = createFileRoute("/guide")({
  component: GuidePage,
});

function GuidePage() {
  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 },
  };

  const guides = [
    {
      icon: <Timer className="w-8 h-8 text-[#7ED6E8]" />,
      title: "포모도로 타이머",
      description:
        "25분 집중, 5분 휴식의 과학적인 주기로 학습 효율을 극대화하세요. 커스텀 타이머 설정도 가능합니다.",
    },
    {
      icon: <Users className="w-8 h-8 text-[#F9A8D4]" />,
      title: "함께 공부하기",
      description:
        "다른 사용자들과 실시간으로 함께 공부하며 동기부여를 받으세요. 1:1 매칭부터 팀 스터디까지 지원합니다.",
    },
    {
      icon: <Trophy className="w-8 h-8 text-yellow-500" />,
      title: "랭킹 시스템",
      description:
        "공부 시간을 기반으로 한 주간/월간 랭킹으로 선의의 경쟁을 펼쳐보세요. 명예의 전당에 도전하세요!",
    },
    {
      icon: <Heart className="w-8 h-8 text-red-400" />,
      title: "핑크캠퍼스",
      description:
        "대학생들을 위한 특별한 공간. 같은 학교 학우들을 찾거나 다른 학교와 미팅을 가져보세요.",
    },
  ];

  return (
    <PageTransition>
      <div className="min-h-screen bg-background relative overflow-hidden py-12 px-4 sm:px-6 lg:px-8">
        {/* Background Accents */}
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-[#7ED6E8]/10 rounded-full blur-3xl -z-10" />
        <div className="absolute top-0 right-1/4 w-96 h-96 bg-[#F9A8D4]/10 rounded-full blur-3xl -z-10" />

        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
          className="max-w-4xl mx-auto space-y-12"
        >
          {/* Header */}
          <motion.div variants={item} className="text-center space-y-4">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-[#7ED6E8] to-[#F9A8D4] bg-clip-text text-transparent">
              FocusMate 사용 가이드
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              FocusMate와 함께 더 효율적으로, 더 즐겁게 공부하는 방법을
              알아보세요.
            </p>
          </motion.div>

          {/* Guide Cards */}
          <div className="grid md:grid-cols-2 gap-6">
            {guides.map((guide, index) => (
              <motion.div key={index} variants={item}>
                <Card className="p-6 h-full hover:shadow-lg transition-all duration-300 border-border/50 bg-card/30 backdrop-blur-xl group hover:border-[#7ED6E8]/50">
                  <div className="flex items-start gap-4">
                    <div className="p-3 rounded-2xl bg-muted/50 group-hover:bg-gradient-to-br group-hover:from-[#7ED6E8]/10 group-hover:to-[#F9A8D4]/10 transition-colors flex-shrink-0">
                      {guide.icon}
                    </div>
                    <div className="space-y-2">
                      <h3 className="text-xl font-semibold group-hover:text-[#7ED6E8] transition-colors">
                        {guide.title}
                      </h3>
                      <p className="text-muted-foreground leading-relaxed">
                        {guide.description}
                      </p>
                    </div>
                  </div>
                </Card>
              </motion.div>
            ))}
          </div>

          {/* FAQ Section Preview */}
          <motion.div
            variants={item}
            className="text-center rounded-3xl p-8 border border-[#F9A8D4]/20 bg-gradient-to-br from-[#F9A8D4]/5 to-[#7ED6E8]/5"
          >
            <h2 className="text-2xl font-bold mb-4">
              더 궁금한 점이 있으신가요?
            </h2>
            <p className="text-muted-foreground mb-6">
              자주 묻는 질문에서 더 자세한 내용을 확인하실 수 있습니다.
            </p>
            <a
              href="/faq"
              className="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-full text-white bg-gradient-to-r from-[#7ED6E8] to-[#F9A8D4] hover:opacity-90 transition-all shadow-md hover:scale-105"
            >
              FAQ 바로가기
            </a>
          </motion.div>
        </motion.div>
      </div>
    </PageTransition>
  );
}

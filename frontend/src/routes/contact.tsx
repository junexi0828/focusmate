import { createFileRoute } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { Mail, MessageSquare, Send } from "lucide-react";
import { PageTransition } from "../components/PageTransition";
import { Button } from "../components/ui/button";
import { Card } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Textarea } from "../components/ui/textarea";

export const Route = createFileRoute("/contact")({
  component: ContactPage,
});

function ContactPage() {
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

  return (
    <PageTransition>
      <div className="min-h-screen bg-slate-50 dark:bg-slate-900 py-12 px-4 sm:px-6 lg:px-8">
        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
          className="max-w-4xl mx-auto space-y-12"
        >
          {/* Header */}
          <motion.div variants={item} className="text-center space-y-4">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-[#7ED6E8] to-[#F9A8D4] bg-clip-text text-transparent">
              문의하기
            </h1>
            <p className="text-lg text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
              FocusMate 팀은 여러분의 소중한 의견을 기다립니다.
              <br />
              버그 제보, 기능 제안, 파트너십 등 무엇이든 편하게 말씀해주세요.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Contact Info Cards */}
            <motion.div variants={item} className="md:col-span-1 space-y-6">
              <Card className="p-6 border-[#E0F7FD] bg-white/50 dark:bg-slate-800/50 backdrop-blur-sm">
                <div className="space-y-4">
                  <div className="w-12 h-12 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
                    <Mail className="w-6 h-6 text-blue-500" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg text-slate-900 dark:text-slate-100">
                      이메일 문의
                    </h3>
                    <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                      24시간 이내에 답변드립니다.
                    </p>
                    <a
                      href="mailto:support@focusmate.com"
                      className="text-blue-500 hover:text-blue-600 font-medium mt-2 inline-block"
                    >
                      support@focusmate.com
                    </a>
                  </div>
                </div>
              </Card>

              <Card className="p-6 border-[#E0F7FD] bg-white/50 dark:bg-slate-800/50 backdrop-blur-sm">
                <div className="space-y-4">
                  <div className="w-12 h-12 rounded-full bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
                    <MessageSquare className="w-6 h-6 text-purple-500" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg text-slate-900 dark:text-slate-100">
                      실시간 커뮤니티
                    </h3>
                    <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                      다른 사용자들과 소통하세요.
                    </p>
                    <a
                      href="/community"
                      className="text-purple-500 hover:text-purple-600 font-medium mt-2 inline-block"
                    >
                      커뮤니티 바로가기
                    </a>
                  </div>
                </div>
              </Card>
            </motion.div>

            {/* Contact Form */}
            <motion.div variants={item} className="md:col-span-2">
              <Card className="p-8 border-[#E0F7FD] bg-white dark:bg-slate-800 shadow-xl">
                <form className="space-y-6">
                  <div className="grid sm:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="name">이름</Label>
                      <Input id="name" placeholder="홍길동" />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="email">이메일</Label>
                      <Input
                        id="email"
                        type="email"
                        placeholder="example@email.com"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="category">문의 유형</Label>
                    <select
                      id="category"
                      className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      <option value="">선택해주세요</option>
                      <option value="bug">버그 제보</option>
                      <option value="feature">기능 제안</option>
                      <option value="account">계정 관련</option>
                      <option value="other">기타</option>
                    </select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="subject">제목</Label>
                    <Input id="subject" placeholder="문의 제목을 입력해주세요" />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="message">내용</Label>
                    <Textarea
                      id="message"
                      placeholder="자세한 내용을 적어주시면 빠르게 도와드릴 수 있습니다."
                      className="min-h-[150px]"
                    />
                  </div>

                  <Button
                    type="submit"
                    className="w-full bg-gradient-to-r from-[#7ED6E8] to-[#F9A8D4] text-white font-medium py-6"
                  >
                    <Send className="w-4 h-4 mr-2" />
                    문의 보내기
                  </Button>
                </form>
              </Card>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </PageTransition>
  );
}

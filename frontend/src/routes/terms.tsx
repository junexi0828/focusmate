import { createFileRoute } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { PageTransition } from "../components/PageTransition";
import { Card } from "../components/ui/card";

export const Route = createFileRoute("/terms")({
  component: TermsPage,
});

function TermsPage() {
  return (
    <PageTransition>
      <div className="min-h-screen bg-slate-50 dark:bg-slate-900 py-12 px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="max-w-4xl mx-auto"
        >
          <div className="text-center mb-12">
            <h1 className="text-3xl font-bold bg-gradient-to-r from-[#7ED6E8] to-[#F9A8D4] bg-clip-text text-transparent mb-4">
              서비스 이용약관
            </h1>
            <p className="text-slate-600 dark:text-slate-400">
              최종 수정일: 2024년 3월 15일
            </p>
          </div>

          <Card className="p-8 md:p-12 bg-white dark:bg-slate-900 shadow-sm border-[#E0F7FD]">
            <div className="prose prose-slate dark:prose-invert max-w-none space-y-8">
              <section>
                <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-3">
                  제 1 조 (목적)
                </h2>
                <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
                  본 약관은 FocusMate(이하 "회사")가 제공하는 온라인 학습 보조 서비스(이하 "서비스")의 이용조건 및 절차, 회사와 회원의 권리, 의무 및 책임사항 등 기타 필요한 사항을 규정함을 목적으로 합니다.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-3">
                  제 2 조 (용어의 정의)
                </h2>
                <ul className="list-disc pl-5 mt-2 space-y-1 text-slate-600 dark:text-slate-400">
                  <li>"서비스"라 함은 구현되는 단말기와 상관없이 회원이 이용할 수 있는 FocusMate 및 관련 제반 서비스를 의미합니다.</li>
                  <li>"회원"이라 함은 회사의 서비스에 접속하여 본 약관에 따라 회사와 이용계약을 체결하고 회사가 제공하는 서비스를 이용하는 고객을 말합니다.</li>
                </ul>
              </section>

              <section>
                <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-3">
                  제 3 조 (서비스의 제공)
                </h2>
                <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
                  회사는 회원에게 다음과 같은 서비스를 제공합니다.
                </p>
                <ul className="list-disc pl-5 mt-2 space-y-1 text-slate-600 dark:text-slate-400">
                  <li>포모도로 타이머 서비스</li>
                  <li>실시간 채팅 및 커뮤니티 서비스</li>
                  <li>학습 통계 및 랭킹 서비스</li>
                  <li>기타 회사가 추가 개발하거나 제휴 등을 통해 회원에게 제공하는 일체의 서비스</li>
                </ul>
              </section>

              <section>
                <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-3">
                  제 4 조 (면책조항)
                </h2>
                <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
                  회사는 천재지변 또는 이에 준하는 불가항력으로 인하여 서비스를 제공할 수 없는 경우에는 서비스 제공에 관한 책임이 면제됩니다.
                </p>
              </section>
            </div>
          </Card>
        </motion.div>
      </div>
    </PageTransition>
  );
}

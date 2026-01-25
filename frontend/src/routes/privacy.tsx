import { createFileRoute } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { PageTransition } from "../components/PageTransition";
import { Card } from "../components/ui/card";

export const Route = createFileRoute("/privacy")({
  component: PrivacyPage,
});

function PrivacyPage() {
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
              개인정보처리방침
            </h1>
            <p className="text-slate-600 dark:text-slate-400">
              최종 수정일: 2024년 3월 15일
            </p>
          </div>

          <Card className="p-8 md:p-12 bg-white dark:bg-slate-900 shadow-sm border-[#E0F7FD]">
            <div className="prose prose-slate dark:prose-invert max-w-none space-y-8">
              <section>
                <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-3">
                  1. 수집하는 개인정보 항목
                </h2>
                <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
                  FocusMate는 회원가입, 고객상담, 서비스 신청 등을 위해 아래와 같은 개인정보를 수집하고 있습니다.
                </p>
                <ul className="list-disc pl-5 mt-2 space-y-1 text-slate-600 dark:text-slate-400">
                  <li>필수항목: 이메일, 비밀번호, 닉네임</li>
                  <li>선택항목: 프로필 사진, 소속 학교/단체</li>
                  <li>자동수집항목: 서비스 이용기록, 접속 로그, 쿠키, 접속 IP 정보</li>
                </ul>
              </section>

              <section>
                <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-3">
                  2. 개인정보의 수집 및 이용목적
                </h2>
                <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
                  회사는 수집한 개인정보를 다음의 목적을 위해 활용합니다.
                </p>
                <ul className="list-disc pl-5 mt-2 space-y-1 text-slate-600 dark:text-slate-400">
                  <li>서비스 제공: 타이머, 채팅, 랭킹 등 핵심 기능 제공</li>
                  <li>회원 관리: 본인확인, 가입의사 확인, 불만처리 등</li>
                  <li>마케팅 및 광고: 신규 서비스 개발, 이벤트 정보 전달 (동의 시)</li>
                </ul>
              </section>

              <section>
                <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-3">
                  3. 개인정보의 보유 및 이용기간
                </h2>
                <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
                  원칙적으로 개인정보 수집 및 이용목적이 달성된 후에는 해당 정보를 지체 없이 파기합니다. 단, 관계법령의 규정에 의하여 보존할 필요가 있는 경우 회사는 아래와 같이 관계법령에서 정한 일정한 기간 동안 회원정보를 보관합니다.
                </p>
              </section>

              <div className="pt-8 border-t border-slate-200 dark:border-slate-800">
                <p className="text-sm text-slate-500">
                  본 방침에 대해 문의사항이 있으신 경우 support@focusmate.com 으로 연락 주시기 바랍니다.
                </p>
              </div>
            </div>
          </Card>
        </motion.div>
      </div>
    </PageTransition>
  );
}

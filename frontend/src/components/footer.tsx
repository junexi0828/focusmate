import { Link } from "@tanstack/react-router";
import {
  Timer,
  Github,
  Mail,
  Heart,
  Users,
  Trophy,
  MessageSquare,
} from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-[#E0F7FD] bg-gradient-to-b from-[#FCE7F5]/30 to-[#E0F7FD]/30 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto px-4 py-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6">
          {/* Brand Section */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#7ED6E8] to-[#F9A8D4] flex items-center justify-center">
                <Timer className="w-5 h-5 text-white" />
              </div>
              <span className="text-lg font-bold bg-gradient-to-r from-[#7ED6E8] to-[#F9A8D4] bg-clip-text text-transparent">
                FocusMate
              </span>
            </div>
            <p className="text-xs text-muted-foreground leading-relaxed">
              함께 집중하는 학습 파트너
              <br />
              팀과 함께 집중력을 향상시키는 실시간 협업 포모도로 타이머
            </p>
          </div>

          {/* Navigation Links */}
          <div>
            <h3 className="font-semibold mb-3 text-[#7ED6E8] text-sm">주요 기능</h3>
            <ul className="space-y-1.5">
              <li>
                <Link
                  to="/"
                  className="text-sm text-muted-foreground hover:text-[#7ED6E8] transition-colors flex items-center gap-2"
                >
                  <Timer className="w-3 h-3" />홈
                </Link>
              </li>
              <li>
                <Link
                  to="/dashboard"
                  className="text-sm text-muted-foreground hover:text-[#7ED6E8] transition-colors flex items-center gap-2"
                >
                  <Users className="w-3 h-3" />
                  대시보드
                </Link>
              </li>
              <li>
                <Link
                  to="/stats"
                  className="text-sm text-muted-foreground hover:text-[#7ED6E8] transition-colors flex items-center gap-2"
                >
                  <Timer className="w-3 h-3" />
                  통계
                </Link>
              </li>
              <li>
                <Link
                  to="/community"
                  className="text-sm text-muted-foreground hover:text-[#7ED6E8] transition-colors flex items-center gap-2"
                >
                  <MessageSquare className="w-3 h-3" />
                  커뮤니티
                </Link>
              </li>
              <li>
                <Link
                  to="/ranking"
                  className="text-sm text-muted-foreground hover:text-[#7ED6E8] transition-colors flex items-center gap-2"
                >
                  <Trophy className="w-3 h-3" />
                  랭킹전
                </Link>
              </li>
              <li>
                <Link
                  to="/matching"
                  className="text-sm text-muted-foreground hover:text-[#F9A8D4] transition-colors flex items-center gap-2"
                >
                  <Heart className="w-3 h-3" />
                  핑크캠퍼스
                </Link>
              </li>
            </ul>
          </div>

          {/* Support Links */}
          <div>
            <h3 className="font-semibold mb-3 text-[#7ED6E8] text-sm">지원</h3>
            <ul className="space-y-1.5">
              <li>
                <a
                  href="#"
                  className="text-sm text-muted-foreground hover:text-[#7ED6E8] transition-colors"
                >
                  사용 가이드
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="text-sm text-muted-foreground hover:text-[#7ED6E8] transition-colors"
                >
                  FAQ
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="text-sm text-muted-foreground hover:text-[#7ED6E8] transition-colors"
                >
                  문의하기
                </a>
              </li>
              <li>
                <Link
                  to="/settings"
                  className="text-sm text-muted-foreground hover:text-[#7ED6E8] transition-colors"
                >
                  설정
                </Link>
              </li>
            </ul>
          </div>

          {/* Social Links */}
          <div>
            <h3 className="font-semibold mb-3 text-[#7ED6E8] text-sm">연락처</h3>
            <div className="flex gap-3 mb-3">
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="w-10 h-10 rounded-full bg-gradient-to-br from-[#7ED6E8] to-[#F9A8D4] flex items-center justify-center text-white hover:scale-110 transition-transform"
                aria-label="GitHub"
              >
                <Github className="w-5 h-5" />
              </a>
              <a
                href="mailto:support@focusmate.com"
                className="w-10 h-10 rounded-full bg-gradient-to-br from-[#F9A8D4] to-[#7ED6E8] flex items-center justify-center text-white hover:scale-110 transition-transform"
                aria-label="Email"
              >
                <Mail className="w-5 h-5" />
              </a>
            </div>
            <p className="text-xs text-muted-foreground">
              버전 2.0
              <br />© 2024 FocusMate
            </p>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="mt-4 pt-4 border-t border-[#E0F7FD]">
          <div className="flex flex-col md:flex-row justify-between items-center gap-3">
            <p className="text-sm text-muted-foreground">
              © 2024 FocusMate. All rights reserved.
            </p>
            <div className="flex gap-6">
              <a
                href="#"
                className="text-sm text-muted-foreground hover:text-[#7ED6E8] transition-colors"
              >
                개인정보처리방침
              </a>
              <a
                href="#"
                className="text-sm text-muted-foreground hover:text-[#7ED6E8] transition-colors"
              >
                이용약관
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}

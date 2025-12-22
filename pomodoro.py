# ========================================
# ✅ 배포 준비 완료
# ========================================
# 1. 테스트 코드 완전 제거 완료
# 2. 테스트 UI 요소 완전 제거 완료
# 3. 과도한 디버깅 로그 정리 완료
# 4. 불필요한 print문 정리 완료
# ========================================

import tkinter as tk
from tkinter import ttk, messagebox
import collections
from datetime import time, datetime, timedelta
import sqlite3
import os
import sys
import time as time_module
from tkcalendar import Calendar

# pygame 라이브러리 import (알림음 기능용)
try:
    import pygame

    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("pygame이 설치되지 않았습니다. 기본 알림음만 사용 가능합니다.")

# Matplotlib and Pandas are required for graphing
try:
    import pandas as pd
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# 로딩 애니메이션을 위한 추가 import
import math
import random


class StreakAnimation:
    """연속 달성 시 짜릿하고 멋진 애니메이션을 제공하는 클래스"""

    def __init__(self, parent, width=400, height=300):
        self.parent = parent
        self.width = width
        self.height = height
        self.is_running = False
        self.animation_id = None
        self.streak_count = 0
        self.animation_type = None

        # 애니메이션 지속 시간 상수 (밀리초)
        # 이 값을 변경하면 모든 애니메이션의 지속 시간이 동시에 변경됩니다
        self.ANIMATION_DURATION = 3000  # 3초

        # 애니메이션 프레임 생성 (최상위로 표시)
        self.frame = tk.Toplevel(parent)
        self.frame.title("연속 달성 애니메이션")
        self.frame.geometry(f"{width}x{height}")
        self.frame.configure(bg="#000000")
        self.frame.overrideredirect(True)  # 타이틀바 제거

        # 창을 화면 중앙에 배치
        self.frame.update_idletasks()
        x = (self.frame.winfo_screenwidth() // 2) - (width // 2)
        y = (self.frame.winfo_screenheight() // 2) - (height // 2)
        self.frame.geometry(f"+{x}+{y}")

        # 항상 최상위로 표시
        self.frame.attributes("-topmost", True)

        # 초기에는 숨겨져 있음
        self.frame.withdraw()

        self.canvas = tk.Canvas(
            self.frame, width=width, height=height, bg="#000000", highlightthickness=0
        )
        self.canvas.pack(expand=True, fill="both")

        # 애니메이션 변수들
        self.angle = 0
        self.scale = 1.0
        self.particles = []
        self.explosion_particles = []
        self.lightning_points = []
        self.firework_particles = []
        self.rainbow_offset = 0
        self.glow_intensity = 0
        self.glow_direction = 1

    def show_streak_animation(self, streak_count):
        """연속 달성 애니메이션 표시"""
        self.streak_count = streak_count
        self.frame.deiconify()  # 창을 보이게 하기
        self.is_running = True

        # 창을 최상위로 가져오기
        self.frame.lift()
        self.frame.focus_force()

        # 연속 달성 수에 따른 애니메이션 타입 결정 (1-8회)
        if streak_count == 1:
            self.animation_type = "first"  # 첫 번째 달성
        elif streak_count == 2:
            self.animation_type = "second"  # 두 번째 달성
        elif streak_count == 3:
            self.animation_type = "third"  # 세 번째 달성
        elif streak_count == 4:
            self.animation_type = "fourth"  # 네 번째 달성
        elif streak_count == 5:
            self.animation_type = "fifth"  # 다섯 번째 달성
        elif streak_count == 6:
            self.animation_type = "sixth"  # 여섯 번째 달성
        elif streak_count == 7:
            self.animation_type = "seventh"  # 일곱 번째 달성
        elif streak_count == 8:
            self.animation_type = "eighth"  # 여덟 번째 달성 (최고 단계)
        else:
            self.animation_type = "first"  # 기본값

        self._animate()

    def hide(self):
        """애니메이션 숨기기"""
        self.is_running = False
        if self.animation_id:
            self.parent.after_cancel(self.animation_id)
        self.frame.withdraw()  # 창을 숨기기

    def _animate(self):
        """메인 애니메이션 루프"""
        if not self.is_running:
            return

        self.canvas.delete("all")

        # 애니메이션 타입별 다른 효과 실행 (1-8회)
        if self.animation_type == "first":
            self._animate_first()
        elif self.animation_type == "second":
            self._animate_second()
        elif self.animation_type == "third":
            self._animate_third()
        elif self.animation_type == "fourth":
            self._animate_fourth()
        elif self.animation_type == "fifth":
            self._animate_fifth()
        elif self.animation_type == "sixth":
            self._animate_sixth()
        elif self.animation_type == "seventh":
            self._animate_seventh()
        elif self.animation_type == "eighth":
            self._animate_eighth()
        else:
            self._animate_first()

        # 애니메이션 변수 업데이트
        self.angle += 8
        self.scale += 0.02 * self.glow_direction
        if self.scale > 1.3 or self.scale < 0.7:
            self.glow_direction *= -1
        self.rainbow_offset += 0.15
        self.glow_intensity = (self.glow_intensity + 0.1) % (2 * math.pi)

        # 다음 프레임 예약 (더 빠른 애니메이션)
        self.animation_id = self.parent.after(30, self._animate)

    def _animate_first(self):
        """첫 번째 달성 애니메이션 - 별빛 효과"""
        center_x, center_y = self.width // 2, self.height // 2

        # 1. 회전하는 별들
        for i in range(3):
            angle = self.angle + i * 120
            x = center_x + 60 * math.cos(math.radians(angle))
            y = center_y + 60 * math.sin(math.radians(angle))
            self._draw_star(x, y, 12, "#FFD700", angle)

        # 2. 중앙 텍스트
        self.canvas.create_text(
            center_x,
            center_y,
            text=f"{self.streak_count}회 달성!",
            font=("Arial", 20, "bold"),
            fill="#FFD700",
        )

        # 3. 펄스 효과
        for i in range(2):
            radius = 50 * self.scale * (1 - i * 0.4)
            alpha = 1 - i * 0.4
            color = f"#{int(255*alpha):02x}{int(215*alpha):02x}{int(0*alpha):02x}"
            self.canvas.create_oval(
                center_x - radius,
                center_y - radius,
                center_x + radius,
                center_y + radius,
                outline=color,
                width=2,
                dash=(5, 5),
            )

    def _animate_second(self):
        """두 번째 달성 애니메이션 - 번개 효과"""
        center_x, center_y = self.width // 2, self.height // 2

        # 1. 번개 효과
        self._draw_lightning(center_x, center_y)

        # 2. 회전하는 화살표들
        for i in range(4):
            angle = self.angle + i * 90
            x = center_x + 80 * math.cos(math.radians(angle))
            y = center_y + 80 * math.sin(math.radians(angle))
            self._draw_arrow(x, y, 18, "#00FFFF", angle)

        # 3. 중앙 텍스트 (글로우 효과)
        glow_color = f"#{int(0):02x}{int(255*abs(math.sin(self.glow_intensity))):02x}{int(255):02x}"
        self.canvas.create_text(
            center_x,
            center_y,
            text=f"{self.streak_count}회 달성!",
            font=("Arial", 22, "bold"),
            fill=glow_color,
        )

        # 4. 에너지 파장
        for i in range(3):
            radius = 70 * self.scale * (1 - i * 0.3)
            color = f"#{int(0):02x}{int(255*abs(math.sin(self.glow_intensity + i))):02x}{int(255):02x}"
            self.canvas.create_oval(
                center_x - radius,
                center_y - radius,
                center_x + radius,
                center_y + radius,
                outline=color,
                width=2,
            )

    def _animate_third(self):
        """세 번째 달성 애니메이션 - 폭발 효과"""
        center_x, center_y = self.width // 2, self.height // 2

        # 1. 폭발 효과
        self._draw_explosion(center_x, center_y)

        # 2. 회전하는 마법진
        self._draw_magic_circle(center_x, center_y)

        # 3. 중앙 텍스트 (마법 효과)
        magic_color = f"#{int(255*abs(math.sin(self.glow_intensity))):02x}{int(0):02x}{int(255):02x}"
        self.canvas.create_text(
            center_x,
            center_y,
            text=f"{self.streak_count}회 달성!",
            font=("Arial", 24, "bold"),
            fill=magic_color,
        )

        # 4. 마법 파티클
        self._update_magic_particles()

        # 5. 레이저 빔 효과
        for i in range(4):
            angle = self.angle + i * 90
            end_x = center_x + 120 * math.cos(math.radians(angle))
            end_y = center_y + 120 * math.sin(math.radians(angle))
            self.canvas.create_line(
                center_x, center_y, end_x, end_y, fill="#FF00FF", width=2, dash=(8, 4)
            )

    def _animate_fourth(self):
        """네 번째 달성 애니메이션 - 드래곤 효과"""
        center_x, center_y = self.width // 2, self.height // 2

        # 1. 드래곤 효과
        self._draw_dragon(center_x, center_y)

        # 2. 화염 효과
        self._draw_fire_effect(center_x, center_y)

        # 3. 중앙 텍스트 (드래곤 글로우)
        dragon_color = f"#{int(255):02x}{int(100*abs(math.sin(self.glow_intensity))):02x}{int(0):02x}"
        self.canvas.create_text(
            center_x,
            center_y,
            text=f"{self.streak_count}회 달성!",
            font=("Arial", 26, "bold"),
            fill=dragon_color,
        )

        # 4. 화염 파티클
        self._update_fire_particles()

        # 5. 용의 숨결 효과
        for i in range(5):
            angle = self.angle + i * 72
            start_x = center_x + 150 * math.cos(math.radians(angle))
            start_y = center_y + 150 * math.sin(math.radians(angle))
            end_x = start_x + 80 * math.cos(math.radians(angle + 20))
            end_y = start_y + 80 * math.sin(math.radians(angle + 20))
            self.canvas.create_line(
                start_x, start_y, end_x, end_y, fill="#FF4500", width=3
            )

    def _animate_fifth(self):
        """다섯 번째 달성 애니메이션 - 상어 효과"""
        center_x, center_y = self.width // 2, self.height // 2

        # 1. 상어 효과
        self._draw_shark(center_x, center_y)

        # 2. 파도 효과
        self._draw_wave_effect(center_x, center_y)

        # 3. 중앙 텍스트 (상어 글로우)
        shark_color = f"#{int(0):02x}{int(150*abs(math.sin(self.glow_intensity))):02x}{int(255):02x}"
        self.canvas.create_text(
            center_x,
            center_y,
            text=f"{self.streak_count}회 달성!",
            font=("Arial", 28, "bold"),
            fill=shark_color,
        )

        # 4. 물 파티클
        self._update_water_particles()

        # 5. 상어의 물기 효과
        for i in range(6):
            angle = self.angle + i * 60
            start_x = center_x + 160 * math.cos(math.radians(angle))
            start_y = center_y + 160 * math.sin(math.radians(angle))
            end_x = start_x + 90 * math.cos(math.radians(angle + 15))
            end_y = start_y + 90 * math.sin(math.radians(angle + 15))
            self.canvas.create_line(
                start_x, start_y, end_x, end_y, fill="#00CED1", width=2
            )

        # 6. 신의 손길 효과
        self._draw_divine_touch(center_x, center_y)

        # 7. 무지개 빛 효과
        self._draw_rainbow_aura(center_x, center_y)

    def _animate_sixth(self):
        """여섯 번째 달성 애니메이션 - 총쏘기 효과"""
        center_x, center_y = self.width // 2, self.height // 2

        # 1. 총알 효과
        self._draw_bullet_effect(center_x, center_y)

        # 2. 총구 화염
        self._draw_muzzle_flash(center_x, center_y)

        # 3. 중앙 텍스트 (총알 글로우)
        bullet_color = f"#{int(255):02x}{int(255*abs(math.sin(self.glow_intensity))):02x}{int(0):02x}"
        self.canvas.create_text(
            center_x,
            center_y,
            text=f"{self.streak_count}회 달성!",
            font=("Arial", 30, "bold"),
            fill=bullet_color,
        )

        # 4. 총알 궤적
        for i in range(7):
            angle = self.angle + i * 51.4
            start_x = center_x + 180 * math.cos(math.radians(angle))
            start_y = center_y + 180 * math.sin(math.radians(angle))
            end_x = start_x + 100 * math.cos(math.radians(angle + 10))
            end_y = start_y + 100 * math.sin(math.radians(angle + 10))
            self.canvas.create_line(
                start_x, start_y, end_x, end_y, fill="#FFD700", width=2
            )

    def _animate_seventh(self):
        """일곱 번째 달성 애니메이션 - 폭탄 터지기 효과"""
        center_x, center_y = self.width // 2, self.height // 2

        # 1. 폭탄 효과
        self._draw_bomb_explosion(center_x, center_y)

        # 2. 충격파
        self._draw_shockwave(center_x, center_y)

        # 3. 중앙 텍스트 (폭발 글로우)
        bomb_color = f"#{int(255*abs(math.sin(self.glow_intensity))):02x}{int(0):02x}{int(0):02x}"
        self.canvas.create_text(
            center_x,
            center_y,
            text=f"{self.streak_count}회 달성!",
            font=("Arial", 32, "bold"),
            fill=bomb_color,
        )

        # 4. 폭발 파편
        for i in range(8):
            angle = self.angle + i * 45
            start_x = center_x + 200 * math.cos(math.radians(angle))
            start_y = center_y + 200 * math.sin(math.radians(angle))
            end_x = start_x + 110 * math.cos(math.radians(angle + 25))
            end_y = start_y + 110 * math.sin(math.radians(angle + 15))
            self.canvas.create_line(
                start_x, start_y, end_x, end_y, fill="#FF4500", width=3
            )

    def _animate_eighth(self):
        """여덟 번째 달성 애니메이션 - 최고 단계 효과"""
        center_x, center_y = self.width // 2, self.height // 2

        # 1. 우주 폭발
        self._draw_cosmic_explosion(center_x, center_y)

        # 2. 차원 균열
        self._draw_dimension_rift_new(center_x, center_y)

        # 3. 중앙 텍스트 (최고 글로우)
        ultimate_color = f"#{int(255*abs(math.sin(self.glow_intensity))):02x}{int(0):02x}{int(0):02x}"
        self.canvas.create_text(
            center_x,
            center_y,
            text=f"{self.streak_count}회 달성!",
            font=("Arial", 36, "bold"),
            fill=ultimate_color,
        )

        # 4. 시간 왜곡 효과
        self._draw_time_distortion_new(center_x, center_y)

        # 5. 우주 폭풍
        for i in range(12):
            angle = self.angle + i * 30
            start_x = center_x + 300 * math.cos(math.radians(angle))
            start_y = center_y + 300 * math.sin(math.radians(angle))
            end_x = start_x + 150 * math.cos(math.radians(angle + 20))
            end_y = start_y + 150 * math.sin(math.radians(angle + 20))
            self.canvas.create_line(
                start_x, start_y, end_x, end_y, fill="#FFD700", width=4
            )

    # 새로운 애니메이션을 위한 헬퍼 함수들
    def _draw_dragon(self, x, y):
        """드래곤 그리기"""
        # 드래곤 몸체
        self.canvas.create_oval(
            x - 40, y - 20, x + 40, y + 20, fill="#8B0000", outline="#DC143C", width=3
        )
        # 드래곤 머리
        self.canvas.create_oval(
            x - 50, y - 30, x - 30, y - 10, fill="#8B0000", outline="#DC143C", width=2
        )
        # 드래곤 날개
        self.canvas.create_arc(
            x - 60,
            y - 40,
            x + 20,
            y + 40,
            start=0,
            extent=180,
            fill="#DC143C",
            outline="#8B0000",
            width=2,
        )

    def _draw_fire_effect(self, x, y):
        """화염 효과 그리기"""
        for i in range(8):
            angle = i * 45
            end_x = x + 60 * math.cos(math.radians(angle))
            end_y = y + 60 * math.sin(math.radians(angle))
            color = f"#{int(255):02x}{int(100+i*20):02x}{int(0):02x}"
            self.canvas.create_line(x, y, end_x, end_y, fill=color, width=4)

    def _update_fire_particles(self):
        """화염 파티클 업데이트"""
        if not hasattr(self, "fire_particles"):
            self.fire_particles = []
            for _ in range(20):
                self.fire_particles.append(
                    {
                        "x": random.randint(0, self.width),
                        "y": random.randint(0, self.height),
                        "vx": random.uniform(-2, 2),
                        "vy": random.uniform(-2, 2),
                        "size": random.randint(3, 8),
                        "color": random.choice(["#FF4500", "#FF6347", "#FF8C00"]),
                    }
                )

        for particle in self.fire_particles:
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            self.canvas.create_oval(
                particle["x"] - particle["size"],
                particle["y"] - particle["size"],
                particle["x"] + particle["size"],
                particle["y"] + particle["size"],
                fill=particle["color"],
                outline="#FFD700",
                width=1,
            )

    def _draw_shark(self, x, y):
        """상어 그리기"""
        # 상어 몸체
        self.canvas.create_oval(
            x - 50, y - 15, x + 50, y + 15, fill="#2F4F4F", outline="#708090", width=3
        )
        # 상어 지느러미
        self.canvas.create_polygon(
            x - 20,
            y - 25,
            x,
            y - 35,
            x + 20,
            y - 25,
            fill="#2F4F4F",
            outline="#708090",
            width=2,
        )
        # 상어 꼬리
        self.canvas.create_polygon(
            x + 40,
            y - 20,
            x + 60,
            y,
            x + 40,
            y + 20,
            fill="#2F4F4F",
            outline="#708090",
            width=2,
        )

    def _draw_wave_effect(self, x, y):
        """파도 효과 그리기"""
        for i in range(6):
            wave_y = y + 80 + i * 20
            self.canvas.create_arc(
                x - 100,
                wave_y - 10,
                x + 100,
                wave_y + 10,
                start=0,
                extent=180,
                outline="#00CED1",
                width=3,
            )

    def _update_water_particles(self):
        """물 파티클 업데이트"""
        if not hasattr(self, "water_particles"):
            self.water_particles = []
            for _ in range(25):
                self.water_particles.append(
                    {
                        "x": random.randint(0, self.width),
                        "y": random.randint(0, self.height),
                        "vx": random.uniform(-1, 1),
                        "vy": random.uniform(-1, 1),
                        "size": random.randint(2, 6),
                        "color": random.choice(["#00CED1", "#87CEEB", "#4682B4"]),
                    }
                )

        for particle in self.water_particles:
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            self.canvas.create_oval(
                particle["x"] - particle["size"],
                particle["y"] - particle["size"],
                particle["x"] + particle["size"],
                particle["y"] + particle["size"],
                fill=particle["color"],
                outline="#FFFFFF",
                width=1,
            )

    def _draw_bullet_effect(self, x, y):
        """총알 효과 그리기"""
        for i in range(10):
            angle = i * 36
            end_x = x + 100 * math.cos(math.radians(angle))
            end_y = y + 100 * math.sin(math.radians(angle))
            self.canvas.create_line(x, y, end_x, end_y, fill="#FFD700", width=2)

    def _draw_muzzle_flash(self, x, y):
        """총구 화염 그리기"""
        self.canvas.create_oval(
            x - 15, y - 15, x + 15, y + 15, fill="#FFFF00", outline="#FF4500", width=3
        )

    def _draw_bomb_explosion(self, x, y):
        """폭탄 폭발 효과 그리기"""
        for i in range(16):
            angle = i * 22.5
            end_x = x + 100 * math.cos(math.radians(angle))
            end_y = y + 100 * math.sin(math.radians(angle))
            color = f"#{int(255):02x}{int(100+i*10):02x}{int(0):02x}"
            self.canvas.create_line(x, y, end_x, end_y, fill=color, width=5)

    def _draw_shockwave(self, x, y):
        """충격파 효과 그리기"""
        for i in range(5):
            radius = 60 + i * 20
            alpha = 1 - i * 0.2
            color = f"#{int(255*alpha):02x}{int(255*alpha):02x}{int(255*alpha):02x}"
            self.canvas.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                outline=color,
                width=3,
                dash=(10, 5),
            )

    def _draw_cosmic_explosion(self, x, y):
        """우주 폭발 효과 그리기"""
        for i in range(24):
            angle = i * 15
            end_x = x + 150 * math.cos(math.radians(angle))
            end_y = y + 150 * math.sin(math.radians(angle))
            color = f"#{int(255):02x}{int(0):02x}{int(255):02x}"
            self.canvas.create_line(x, y, end_x, end_y, fill=color, width=6)

    def _draw_dimension_rift_new(self, x, y):
        """차원 균열 효과 그리기 (새로운 버전)"""
        for i in range(8):
            angle = i * 45
            start_x = x + 80 * math.cos(math.radians(angle))
            start_y = y + 80 * math.sin(math.radians(angle))
            end_x = x + 120 * math.cos(math.radians(angle))
            end_y = y + 120 * math.sin(math.radians(angle))
            self.canvas.create_line(
                start_x, start_y, end_x, end_y, fill="#FF00FF", width=4
            )

    def _draw_time_distortion_new(self, x, y):
        """시간 왜곡 효과 그리기 (새로운 버전)"""
        for i in range(6):
            radius = 100 + i * 25
            alpha = 1 - i * 0.15
            color = f"#{int(0):02x}{int(255*alpha):02x}{int(255*alpha):02x}"
            self.canvas.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                outline=color,
                width=2,
                dash=(15, 10),
            )

    def _draw_star(self, x, y, size, color, angle):
        """별 그리기"""
        points = []
        for i in range(10):
            t = i * math.pi / 5 + math.radians(angle)
            if i % 2 == 0:
                r = size
            else:
                r = size * 0.4
            px = x + r * math.cos(t)
            py = y + r * math.sin(t)
            points.extend([px, py])

        if len(points) >= 4:
            self.canvas.create_polygon(points, fill=color, outline="#FFA500", width=2)

    def _draw_lightning(self, x, y):
        """번개 효과 그리기"""
        points = [
            x,
            y - 80,
            x + 20,
            y - 40,
            x - 15,
            y - 20,
            x + 25,
            y + 20,
            x - 20,
            y + 60,
            x,
            y + 80,
        ]
        self.canvas.create_line(points, fill="#00FFFF", width=4, smooth=True)

        # 번개 글로우 효과
        glow_points = [
            x,
            y - 80,
            x + 25,
            y - 40,
            x - 20,
            y - 20,
            x + 30,
            y + 20,
            x - 25,
            y + 60,
            x,
            y + 80,
        ]
        self.canvas.create_line(glow_points, fill="#FFFFFF", width=2, smooth=True)

    def _draw_arrow(self, x, y, size, color, angle):
        """화살표 그리기"""
        points = [
            x + size * math.cos(math.radians(angle)),
            y + size * math.sin(math.radians(angle)),
            x + size * math.cos(math.radians(angle + 150)),
            y + size * math.sin(math.radians(angle + 150)),
            x + size * math.cos(math.radians(angle + 210)),
            y + size * math.sin(math.radians(angle + 210)),
        ]
        self.canvas.create_polygon(points, fill=color, outline="#000000", width=1)

    def _draw_explosion(self, x, y):
        """폭발 효과 그리기"""
        for i in range(12):
            angle = i * 30
            end_x = x + 80 * math.cos(math.radians(angle))
            end_y = y + 80 * math.sin(math.radians(angle))
            self.canvas.create_line(x, y, end_x, end_y, fill="#FF4500", width=3)

        # 폭발 중심
        self.canvas.create_oval(
            x - 20, y - 20, x + 20, y + 20, fill="#FFFF00", outline="#FF4500", width=3
        )

    def _draw_magic_circle(self, x, y):
        """마법진 그리기"""
        # 외부 원
        self.canvas.create_oval(
            x - 100, y - 100, x + 100, y + 100, outline="#FF00FF", width=3
        )

        # 내부 마법 문양
        for i in range(6):
            angle = self.angle + i * 60
            point_x = x + 60 * math.cos(math.radians(angle))
            point_y = y + 60 * math.sin(math.radians(angle))
            self.canvas.create_oval(
                point_x - 10,
                point_y - 10,
                point_x + 10,
                point_y + 10,
                fill="#FF00FF",
                outline="#FFFFFF",
            )

    def _update_magic_particles(self):
        """마법 파티클 업데이트"""
        if not self.particles:
            self.particles = []
            for _ in range(15):
                self.particles.append(
                    {
                        "x": random.randint(0, self.width),
                        "y": random.randint(0, self.height),
                        "vx": random.uniform(-3, 3),
                        "vy": random.uniform(-3, 3),
                        "size": random.randint(2, 5),
                        "color": random.choice(["#FF00FF", "#00FFFF", "#FFFF00"]),
                    }
                )

        for particle in self.particles:
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]

            if particle["x"] < 0 or particle["x"] > self.width:
                particle["vx"] *= -1
            if particle["y"] < 0 or particle["y"] > self.height:
                particle["vy"] *= -1

            self.canvas.create_oval(
                particle["x"] - particle["size"],
                particle["y"] - particle["size"],
                particle["x"] + particle["size"],
                particle["y"] + particle["size"],
                fill=particle["color"],
                outline="#FFFFFF",
            )

    def _draw_mega_explosion(self, x, y):
        """거대한 폭발 효과"""
        for i in range(20):
            angle = i * 18
            end_x = x + 120 * math.cos(math.radians(angle))
            end_y = y + 120 * math.sin(math.radians(angle))
            color = f"#{int(255):02x}{int(100+i*7):02x}{int(0):02x}"
            self.canvas.create_line(x, y, end_x, end_y, fill=color, width=4)

    def _draw_gravity_field(self, x, y):
        """중력장 효과"""
        for i in range(8):
            radius = 80 + i * 15
            alpha = 1 - i * 0.1
            color = f"#{int(0):02x}{int(0):02x}{int(255*alpha):02x}"
            self.canvas.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                outline=color,
                width=2,
                dash=(10, 5),
            )

    def _update_space_particles(self):
        """우주 파티클 업데이트"""
        if not self.particles:
            self.particles = []
            for _ in range(25):
                self.particles.append(
                    {
                        "x": random.randint(0, self.width),
                        "y": random.randint(0, self.height),
                        "vx": random.uniform(-2, 2),
                        "vy": random.uniform(-2, 2),
                        "size": random.randint(2, 6),
                        "color": random.choice(
                            ["#FFFFFF", "#87CEEB", "#FFD700", "#FF69B4"]
                        ),
                    }
                )

        for particle in self.particles:
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]

            if particle["x"] < 0 or particle["x"] > self.width:
                particle["vx"] *= -1
            if particle["y"] < 0 or particle["y"] > self.height:
                particle["vy"] *= -1

            self.canvas.create_oval(
                particle["x"] - particle["size"],
                particle["y"] - particle["size"],
                particle["x"] + particle["size"],
                particle["y"] + particle["size"],
                fill=particle["color"],
                outline="#000000",
            )

    def _draw_black_hole(self, x, y):
        """블랙홀 효과"""
        # 블랙홀 중심
        self.canvas.create_oval(
            x - 30, y - 30, x + 30, y + 30, fill="#000000", outline="#FFD700", width=3
        )

        # 중력 왜곡 효과
        for i in range(5):
            radius = 40 + i * 20
            self.canvas.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                outline="#FFD700",
                width=1,
                dash=(5, 10),
            )

    def _draw_supernova(self, x, y):
        """초신성 폭발 효과"""
        for i in range(30):
            angle = i * 12
            end_x = x + 150 * math.cos(math.radians(angle))
            end_y = y + 150 * math.sin(math.radians(angle))
            color = f"#{int(255):02x}{int(255):02x}{int(255):02x}"
            self.canvas.create_line(x, y, end_x, end_y, fill=color, width=5)

    def _draw_dimension_rift(self, x, y):
        """차원 균열 효과"""
        # 균열 선들
        for i in range(10):
            start_x = x + random.randint(-100, 100)
            start_y = y + random.randint(-100, 100)
            end_x = start_x + random.randint(-50, 50)
            end_y = start_y + random.randint(-50, 50)
            self.canvas.create_line(
                start_x, start_y, end_x, end_y, fill="#FF00FF", width=3
            )

    def _draw_time_distortion(self, x, y):
        """시간 왜곡 효과"""
        # 나선형 효과
        for i in range(100):
            angle = i * 3.6
            radius = i * 2
            point_x = x + radius * math.cos(math.radians(angle))
            point_y = y + radius * math.sin(math.radians(angle))
            if 0 <= point_x <= self.width and 0 <= point_y <= self.height:
                self.canvas.create_oval(
                    point_x - 1, point_y - 1, point_x + 1, point_y + 1, fill="#00FFFF"
                )

    def _update_cosmic_storm(self):
        """우주 폭풍 효과"""
        if not self.particles:
            self.particles = []
            for _ in range(40):
                self.particles.append(
                    {
                        "x": random.randint(0, self.width),
                        "y": random.randint(0, self.height),
                        "vx": random.uniform(-4, 4),
                        "vy": random.uniform(-4, 4),
                        "size": random.randint(1, 8),
                        "color": random.choice(
                            [
                                "#FF0000",
                                "#00FF00",
                                "#0000FF",
                                "#FFFF00",
                                "#FF00FF",
                                "#00FFFF",
                            ]
                        ),
                    }
                )

        for particle in self.particles:
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]

            if particle["x"] < 0 or particle["x"] > self.width:
                particle["vx"] *= -1
            if particle["y"] < 0 or particle["y"] > self.height:
                particle["vy"] *= -1

            self.canvas.create_oval(
                particle["x"] - particle["size"],
                particle["y"] - particle["size"],
                particle["x"] + particle["size"],
                particle["y"] + particle["size"],
                fill=particle["color"],
                outline="#FFFFFF",
            )

    def _draw_divine_touch(self, x, y):
        """신의 손길 효과"""
        # 천사 날개 효과
        for wing in range(2):
            wing_x = x + (50 if wing == 0 else -50)
            for i in range(5):
                feather_x = wing_x + random.randint(-20, 20)
                feather_y = y + random.randint(-30, 30)
                self.canvas.create_oval(
                    feather_x - 5,
                    feather_y - 5,
                    feather_x + 5,
                    feather_y + 5,
                    fill="#FFFFFF",
                    outline="#FFD700",
                )

    def _draw_rainbow_aura(self, x, y):
        """무지개 빛 효과"""
        colors = [
            "#FF0000",
            "#FF7F00",
            "#FFFF00",
            "#00FF00",
            "#0000FF",
            "#4B0082",
            "#9400D3",
        ]
        for i, color in enumerate(colors):
            radius = 120 + i * 10
            self.canvas.create_oval(
                x - radius, y - radius, x + radius, y + radius, outline=color, width=2
            )


class LoadingAnimation:
    """재미있는 로딩 애니메이션을 제공하는 클래스"""

    def __init__(self, parent, width=400, height=300):
        self.parent = parent
        self.width = width
        self.height = height
        self.is_running = False
        self.animation_id = None

        # 애니메이션 프레임 생성
        self.frame = tk.Frame(parent, bg="#1a1a1a")
        self.canvas = tk.Canvas(
            self.frame, width=width, height=height, bg="#1a1a1a", highlightthickness=0
        )
        self.canvas.pack(expand=True, fill="both")

        # 애니메이션 변수들
        self.angle = 0
        self.pulse_scale = 1.0
        self.pulse_direction = 1
        self.particles = []
        self.wave_offset = 0

        # 파티클 초기화
        self._init_particles()

    def _init_particles(self):
        """파티클 시스템 초기화"""
        self.particles = []
        for _ in range(20):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            vx = random.uniform(-2, 2)
            vy = random.uniform(-2, 2)
            size = random.randint(2, 6)
            color = random.choice(
                ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"]
            )
            self.particles.append(
                {"x": x, "y": y, "vx": vx, "vy": vy, "size": size, "color": color}
            )

    def show(self):
        """로딩 애니메이션 표시"""
        self.frame.pack(expand=True, fill="both")
        self.is_running = True
        self._animate()

    def hide(self):
        """로딩 애니메이션 숨기기"""
        self.is_running = False
        if self.animation_id:
            self.parent.after_cancel(self.animation_id)
        self.frame.pack_forget()

    def _animate(self):
        """메인 애니메이션 루프"""
        if not self.is_running:
            return

        self.canvas.delete("all")

        # 1. 회전하는 톱니바퀴 애니메이션
        self._draw_rotating_gears()

        # 2. 펄스 효과
        self._draw_pulse_effect()

        # 3. 파티클 시스템
        self._update_particles()

        # 4. 웨이브 효과
        self._draw_wave_effect()

        # 5. 텍스트 애니메이션
        self._draw_loading_text()

        # 애니메이션 변수 업데이트
        self.angle += 5
        self.pulse_scale += 0.05 * self.pulse_direction
        if self.pulse_scale > 1.2 or self.pulse_scale < 0.8:
            self.pulse_direction *= -1
        self.wave_offset += 0.1

        # 다음 프레임 예약
        self.animation_id = self.parent.after(50, self._animate)

    def _draw_rotating_gears(self):
        """회전하는 톱니바퀴 그리기"""
        center_x, center_y = self.width // 2, self.height // 2

        # 메인 톱니바퀴
        self._draw_gear(center_x, center_y, 60, 12, self.angle, "#FF6B6B")

        # 작은 톱니바퀴들
        self._draw_gear(
            center_x - 100, center_y - 50, 30, 8, -self.angle * 1.5, "#4ECDC4"
        )
        self._draw_gear(
            center_x + 100, center_y + 50, 25, 6, self.angle * 0.8, "#45B7D1"
        )

    def _draw_gear(self, x, y, radius, teeth, angle, color):
        """개별 톱니바퀴 그리기"""
        points = []
        for i in range(teeth * 2):
            t = i * math.pi / teeth
            if i % 2 == 0:
                r = radius
            else:
                r = radius * 0.7
            px = x + r * math.cos(t + math.radians(angle))
            py = y + r * math.sin(t + math.radians(angle))
            points.extend([px, py])

        if len(points) >= 4:
            self.canvas.create_polygon(points, fill=color, outline="#333", width=2)
            # 중심 원
            self.canvas.create_oval(
                x - 8, y - 8, x + 8, y + 8, fill="#333", outline="#666"
            )

    def _draw_pulse_effect(self):
        """펄스 효과 그리기"""
        center_x, center_y = self.width // 2, self.height // 2
        max_radius = 80

        for i in range(3):
            radius = max_radius * self.pulse_scale * (1 - i * 0.3)
            alpha = 1 - i * 0.3
            color = f"#{int(255*alpha):02x}{int(107*alpha):02x}{int(107*alpha):02x}"
            self.canvas.create_oval(
                center_x - radius,
                center_y - radius,
                center_x + radius,
                center_y + radius,
                outline=color,
                width=2,
                dash=(5, 5),
            )

    def _update_particles(self):
        """파티클 시스템 업데이트"""
        for particle in self.particles:
            # 파티클 이동
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]

            # 경계 처리
            if particle["x"] < 0 or particle["x"] > self.width:
                particle["vx"] *= -1
            if particle["y"] < 0 or particle["y"] > self.height:
                particle["vy"] *= -1

            # 파티클 그리기
            self.canvas.create_oval(
                particle["x"] - particle["size"],
                particle["y"] - particle["size"],
                particle["x"] + particle["size"],
                particle["y"] + particle["size"],
                fill=particle["color"],
                outline="#333",
            )

    def _draw_wave_effect(self):
        """웨이브 효과 그리기"""
        wave_height = 20
        wave_width = self.width
        points = []

        for x in range(0, wave_width, 5):
            y = self.height - 50 + wave_height * math.sin(x * 0.02 + self.wave_offset)
            points.extend([x, y])

        if len(points) >= 4:
            self.canvas.create_line(points, fill="#4ECDC4", width=3, smooth=True)

    def _draw_loading_text(self):
        """로딩 텍스트 애니메이션"""
        center_x, center_y = self.width // 2, self.height // 2 + 120

        # 메인 텍스트
        self.canvas.create_text(
            center_x,
            center_y,
            text="로딩 중...",
            font=("Arial", 16, "bold"),
            fill="#FFFFFF",
        )

        # 점들 애니메이션
        dots = "." * (int(self.wave_offset * 2) % 4)
        self.canvas.create_text(
            center_x + 80,
            center_y,
            text=dots,
            font=("Arial", 16, "bold"),
            fill="#FF6B6B",
        )


class PomodoroPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Juns Enterprise - Pomodoro Timer & Task Manager v2.1.0")

        # Juns Enterprise-Grade ASCII Art Logo and Legal Notice
        print(
            """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║ ██████╗██╗   ██╗███╗   ██╗███████╗    ████████╗███╗   ███╗███████╗██████╗    ║
║     ██║██║   ██║████╗  ██║██╔════╝    ╚══██╔══╝████╗ ████║██╔════╝██╔══██╗   ║
║     ██║██║   ██║██╔██╗ ██║███████╗       ██║   ██╔████╔██║█████╗  ██████╔╝   ║
║██╗  ██║██║   ██║██║╚██╗██║╚════██║       ██║   ██║╚██╔╝██║██╔══╝  ██╔══██╗   ║
║███████║╚██████╔╝██║ ╚████║███████║       ██║   ██║ ╚═╝ ██║███████╗██║  ██║   ║
║╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝       ╚═╝   ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝   ║
║  ░░░░░░  ░░░░░░  ░░   ░░░░  ░░░░░░       ░░░   ░░░     ░░░  ░░░░░  ░░   ░░   ║
║                      Enterprise-Grade Productivity Suite                     ║
║                                                                              ║
║  ┌────────────────────────────────────────────────────────────────────────┐  ║
║  │                    POMODORO TIMER & TASK MANAGER                       │  ║
║  │                    Version: 2.1.0 (Enterprise Edition)                 │  ║
║  │                    Build: 2025.08.14.001                               │  ║
║  └────────────────────────────────────────────────────────────────────────┘  ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        )

        # Enterprise Legal Notice
        print(
            """
╔══════════════════════════════════════════════════════════════════════════════╗
║                              LEGAL NOTICE                                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  PROPRIETARY SOFTWARE - ALL RIGHTS RESERVED                                  ║
║                                                                              ║
║  This software is the confidential and proprietary information of Juns       ║
║  Corporation ("Company"). It is protected by copyright laws and              ║
║  international copyright treaties, as well as other intellectual property    ║
║  laws and treaties.                                                          ║
║                                                                              ║
║  RESTRICTED RIGHTS:                                                          ║
║  • Unauthorized copying, distribution, or modification is strictly           ║
║    prohibited                                                                ║
║  • Reverse engineering, disassembly, or decompilation is not permitted       ║
║  • Commercial use requires written license agreement                         ║
║  • Educational use requires prior written permission                         ║
║                                                                              ║
║  LICENSING INFORMATION:                                                      ║
║  • Single User License: Personal use only                                    ║
║  • Enterprise License: Contact licensing@juns-corp.com                       ║
║  • Volume Discounts: Available for 100+ users                                ║
║                                                                              ║
║  SUPPORT & MAINTENANCE:                                                      ║
║  • Technical Support: support@juns-corp.com                                  ║
║  • Bug Reports: bugs@juns-corp.com                                           ║
║  • Feature Requests: features@juns-corp.com                                  ║
║                                                                              ║
║  Copyright © 2025 Juns Corporation. All Rights Reserved Worldwide.           ║
║  Juns, the Juns logo, and related marks are trademarks of Juns Corp.         ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        )

        # System Information
        import platform
        import sys

        print(
            f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           SYSTEM INFORMATION                                 ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Platform:     {platform.system()} {platform.release()} {platform.machine()} ║
║  Python:       {sys.version.split()[0]} ({platform.architecture()[0]})       ║
║  Tkinter:      {tk.TkVersion}                                                ║
║  Launch Time:  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                ║
║  Session ID:   {os.getpid():>10}                                             ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        )
        self.root.geometry("1200x800")
        self.root.minsize(600, 400)  # 최소 크기 설정
        self.db_path = "pomodoro_data.db"

        # --- MODEL ---
        self.selected_date = datetime.now().date()
        self.pomodoro_state = "stopped"
        self.paused_from_state = None
        self.work_duration = 25 * 60
        self.break_duration = 5 * 60
        self.pause_duration = 60
        self.seconds_left = self.work_duration
        self.pause_seconds_left = self.pause_duration
        self.alarm_on = False
        
        # 사용자 수동 날짜 변경 추적
        self.user_manually_changed_date = False
        self._alarm_after_id = None
        
        # 작업 이전 관련 플래그 추가
        self.last_transfer_suggested_date = None  # 마지막으로 이전 제안한 날짜
        self.transfer_suggested_today = False  # 오늘 이미 이전 제안했는지 여부

        # 소리 설정 변수들
        self.sound_type = tk.StringVar(value="custom")
        self.sound_volume = tk.StringVar(value="50")

        # pygame 초기화 (알림음 기능용)
        self._init_pygame()

        # 드래그 스크롤 상태 변수
        self.calendar_dragging = False

        # 로딩 애니메이션 초기화
        self.loading_animation = LoadingAnimation(self.root, 400, 300)

        # 연속 달성 애니메이션 초기화
        self.streak_animation = StreakAnimation(self.root, 400, 300)

        # 'today_stats' for live tracking, 'displayed_stats' for UI
        self.today_stats = collections.defaultdict(int)
        self.displayed_stats = self.today_stats

        # 연속 완료 카운트 추적
        self.consecutive_completions = 0

        # 'today_tasks' for live tasks, 'displayed_tasks_data' for UI tasks
        self.today_tasks = collections.OrderedDict()
        self.displayed_tasks_data = (
            self.today_tasks
        )  # Initially points to today's tasks
        self.task_id_counter = 0  # This counter should probably be global for all tasks, not just displayed ones.
        # But for now, it's used for the currently displayed tasks.
        self._timer_id = None
        self.cal_start_hour = 0
        self.cal_end_hour = 24
        self.hour_height = 60
        self.calendar_dragging = False

        self._init_database()
        self._load_today_stats()  # Load today's stats on startup
        self._load_today_tasks()  # Load today's tasks on startup
        # Initialize global next task id to avoid UNIQUE constraint conflicts
        self.next_task_id = self._get_next_task_id()

        # 연속 달성 시스템 초기화 (횟수 기준)
        self.current_streak = 0
        self.last_completion_date = None
        self.streak_milestones = [1, 2, 3, 4, 5, 6, 7, 8]  # 연속 달성 마일스톤 (1-8회)
        self._load_streak_data()  # 연속 달성 데이터 로드

        self._setup_styles()
        self._create_widgets()

        self._update_date_view()
        self._update_timer_display()
        self._update_pomodoro_button()  # Set initial button text
        self.root.after(100, self._draw_calendar_background)
        self._start_timer()

        self.root.protocol("WM_DELETE_WINDOW", self._quit_app)

    def _init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS daily_summary (
                date TEXT PRIMARY KEY,
                completed_pomodoros INTEGER,
                pomodoro_success INTEGER,
                pomodoro_failure INTEGER,
                total_focus_seconds INTEGER
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_date TEXT,
                name TEXT,
                start_time TEXT,
                end_time TEXT,
                status TEXT
            )
        """
        )
        conn.commit()
        conn.close()

    def _load_streak_data(self):
        """연속 달성 데이터를 로드합니다."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 연속 달성 테이블이 없으면 생성
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS streak_data (
                    id INTEGER PRIMARY KEY,
                    current_streak INTEGER DEFAULT 0,
                    last_completion_date TEXT,
                    longest_streak INTEGER DEFAULT 0
                )
            """
            )

            # 기존 데이터 로드
            cursor.execute(
                "SELECT current_streak, last_completion_date, longest_streak FROM streak_data LIMIT 1"
            )
            row = cursor.fetchone()

            if row:
                self.current_streak = row[0]
                self.last_completion_date = row[1]
                self.longest_streak = row[2]
            else:
                # 초기 데이터 삽입
                cursor.execute(
                    "INSERT INTO streak_data (current_streak, longest_streak) VALUES (0, 0)"
                )
                self.current_streak = 0
                self.last_completion_date = None
                self.longest_streak = 0

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"연속 달성 데이터 로드 오류: {e}")
            self.current_streak = 0
            self.last_completion_date = None
            self.longest_streak = 0

    def _save_streak_data(self):
        """연속 달성 데이터를 저장합니다."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE streak_data SET
                current_streak = ?,
                last_completion_date = ?,
                longest_streak = ?
                WHERE id = 1
            """,
                (self.current_streak, self.last_completion_date, self.longest_streak),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"연속 달성 데이터 저장 오류: {e}")

    def _update_streak(self):
        """연속 달성을 업데이트하고 애니메이션을 표시합니다."""
        # 뽀모도로 완료 시 연속 달성 횟수 증가
        self.current_streak += 1

        # 마일스톤 체크
        self._check_streak_milestone()

        # 최장 연속 달성 업데이트 (데이터베이스에 저장된 값과 비교)
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak

        # 데이터베이스에 저장
        self._save_streak_data()

        # 통계 표시 업데이트
        self._update_stats_display()

    def _check_streak_milestone(self):
        """연속 달성 마일스톤을 확인하고 애니메이션을 표시합니다."""
        if self.current_streak in self.streak_milestones:
            # 연속 달성 애니메이션 표시
            self.streak_animation.show_streak_animation(self.current_streak)

            # 애니메이션 지속 시간 상수 사용 (모든 애니메이션 통일)
            self.root.after(
                self.streak_animation.ANIMATION_DURATION, self.streak_animation.hide
            )

            # 터미널에 알림
            print(f"🎉 {self.current_streak}회 연속 달성! 멋진 성과입니다!")

    def _get_next_task_id(self):
        """Returns a globally unique next task id across the whole tasks table and today's in-memory tasks."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT IFNULL(MAX(id), 0) FROM tasks")
            row = cursor.fetchone()
            conn.close()
            max_existing_id = row[0] if row and row[0] is not None else 0
        except Exception:
            max_existing_id = 0
        max_today_id = max(self.today_tasks.keys()) if self.today_tasks else 0
        return max(max_existing_id, max_today_id) + 1

    def _load_today_stats(self):
        """Loads stats for the current day from the DB into today_stats."""
        # 로딩 애니메이션 표시
        self.loading_animation.show()
        self.root.update()

        try:
            date_str = datetime.now().date().strftime("%Y-%m-%d")
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM daily_summary WHERE date = ?", (date_str,))
            stats_data = cursor.fetchone()
            if stats_data:
                self.today_stats["completed_pomodoros"] = stats_data[1]
                self.today_stats["success"] = stats_data[2]
                self.today_stats["failure"] = stats_data[3]
                self.today_stats["total_focus_seconds"] = stats_data[4]
            conn.close()

            # 로딩 완료 후 잠시 대기 (사용자가 애니메이션을 볼 수 있도록)
            self.root.after(1000, self.loading_animation.hide)
        except Exception as e:
            print(f"통계 로드 오류: {e}")
            self.loading_animation.hide()

    def _load_today_tasks(self):
        """Loads tasks for the current day from the DB into today_tasks."""
        # 로딩 애니메이션이 이미 표시되어 있지 않으면 표시
        if not hasattr(self, "_tasks_loading_shown"):
            self.loading_animation.show()
            self.root.update()
            self._tasks_loading_shown = True

        try:
            self.today_tasks.clear()  # Clear existing in-memory tasks for today
            date_str = datetime.now().date().strftime("%Y-%m-%d")
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, start_time, end_time, status FROM tasks WHERE task_date = ?",
                (date_str,),
            )
            tasks_data = cursor.fetchall()
            for row in tasks_data:
                task_id, name, start_t_str, end_t_str, status = row
                self.today_tasks[task_id] = {
                    "name": name,
                    "start_time": datetime.strptime(start_t_str, "%H:%M:%S").time(),
                    "end_time": datetime.strptime(end_t_str, "%H:%M:%S").time(),
                    "is_complete": tk.BooleanVar(value=(status != "pending")),
                    "status": status,
                    "delay_info": None,
                    "widgets": {},  # Widgets will be created when displayed
                }
            conn.close()

            # 로딩 완료 후 잠시 대기 (사용자가 애니메이션을 볼 수 있도록)
            self.root.after(800, self._hide_tasks_loading)
        except Exception as e:
            print(f"작업 로드 오류: {e}")
            self._hide_tasks_loading()

    def _hide_tasks_loading(self):
        """작업 로딩 애니메이션을 숨깁니다."""
        if hasattr(self, "_tasks_loading_shown"):
            delattr(self, "_tasks_loading_shown")
        self.loading_animation.hide()

    def _load_data_for_selected_date(self):
        """선택된 날짜의 데이터를 로드하고 UI를 업데이트합니다."""
        try:
            # 로딩 애니메이션 표시
            self.loading_animation.show()
            self.root.update()

            # Clear current task list widgets from UI
            for widget in self.task_list_frame.winfo_children():
                widget.destroy()

            # Reset widget references for all tasks in today_tasks
            # This ensures that if we return to today, widgets are recreated.
            for task in self.today_tasks.values():
                task['widgets'] = {}

            date_str = self.selected_date.strftime("%Y-%m-%d")
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            is_today = (self.selected_date == datetime.now().date())

            if is_today:
                # 오늘 날짜: 데이터베이스에서 최신 데이터를 로드하여 메모리 업데이트
                
                # today_tasks를 데이터베이스에서 새로 로드
                self.today_tasks.clear()
                cursor.execute(
                    "SELECT id, name, start_time, end_time, status FROM tasks WHERE task_date = ?",
                    (date_str,),
                )
                tasks_data = cursor.fetchall()
                
                for row in tasks_data:
                    task_id, name, start_t_str, end_t_str, status = row
                    self.today_tasks[task_id] = {
                        "name": name,
                        "start_time": datetime.strptime(start_t_str, '%H:%M:%S').time(),
                        "end_time": datetime.strptime(end_t_str, '%H:%M:%S').time(),
                        "is_complete": tk.BooleanVar(value=(status != 'pending')),
                        "status": status,
                        "delay_info": None,
                        "widgets": {}
                    }
                
                # today_stats를 데이터베이스에서 새로 로드
                cursor.execute("SELECT * FROM daily_summary WHERE date = ?", (date_str,))
                stats_data = cursor.fetchone()
                if stats_data:
                    self.today_stats['completed_pomodoros'] = stats_data[1]
                    self.today_stats['success'] = stats_data[2]
                    self.today_stats['failure'] = stats_data[3]
                    self.today_stats['total_focus_seconds'] = stats_data[4]
                
                # 메모리 데이터를 displayed 데이터에 할당
                self.displayed_tasks_data = self.today_tasks
                self.displayed_stats = self.today_stats
                
                # 어제의 미완료 작업 확인 및 이전 제안 (수동 날짜 변경 시에도 작동)
                self._check_and_suggest_task_transfer()
            else:
                # 과거 날짜: 데이터베이스에서 조회
                self.displayed_tasks_data = collections.OrderedDict()
                
                # 작업 데이터 로드
                cursor.execute("SELECT id, name, start_time, end_time, status FROM tasks WHERE task_date = ?", (date_str,))
                tasks_data = cursor.fetchall()
                
                for row in tasks_data:
                    task_id, name, start_t_str, end_t_str, status = row
                    self.displayed_tasks_data[task_id] = {
                        "name": name,
                        "start_time": datetime.strptime(start_t_str, '%H:%M:%S').time(),
                        "end_time": datetime.strptime(end_t_str, '%H:%M:%S').time(),
                        "is_complete": tk.BooleanVar(value=(status != 'pending')),
                        "status": status,
                        "delay_info": None,
                        "widgets": {} 
                    }

                # 통계 데이터 로드
                self.displayed_stats = collections.defaultdict(int)
                cursor.execute("SELECT * FROM daily_summary WHERE date = ?", (date_str,))
                stats_data = cursor.fetchone()
                if stats_data:
                    self.displayed_stats['completed_pomodoros'] = stats_data[1]
                    self.displayed_stats['success'] = stats_data[2]
                    self.displayed_stats['failure'] = stats_data[3]
                    self.displayed_stats['total_focus_seconds'] = stats_data[4]
            
            # UI 업데이트
            for task_id, task in self.displayed_tasks_data.items():
                self._create_task_list_item(task_id)

            # task_id_counter 업데이트
            self.task_id_counter = max(self.displayed_tasks_data.keys()) + 1 if self.displayed_tasks_data else 0
            if self.displayed_tasks_data:
                self.next_task_id = max(self.next_task_id, max(self.displayed_tasks_data.keys()) + 1)

            # 캘린더 및 통계 업데이트
            self._draw_tasks_on_calendar()
            self._update_stats_display()
            self._update_task_scroll_region()
            
            conn.close()

            # 로딩 완료 후 애니메이션 숨기기
            self.root.after(500, self.loading_animation.hide)

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.loading_animation.hide()

    def _save_data(self):
        # This should only save data for the day the work was actually done.
        date_str = datetime.now().date().strftime("%Y-%m-%d")
        with sqlite3.connect(self.db_path) as conn:
            # Wait up to 3s if the DB is temporarily locked
            conn.execute("PRAGMA busy_timeout = 3000")
            cursor = conn.cursor()

            # Always save the live 'today_stats'
            cursor.execute(
                "INSERT OR REPLACE INTO daily_summary VALUES (?, ?, ?, ?, ?)",
                (
                    date_str,
                    self.today_stats.get("completed_pomodoros", 0),
                    self.today_stats.get("success", 0),
                    self.today_stats.get("failure", 0),
                    self.today_stats.get("total_focus_seconds", 0),
                ),
            )

            # Save 'today_tasks' to the database.
            cursor.execute("DELETE FROM tasks WHERE task_date = ?", (date_str,))
            for task_id, task in self.today_tasks.items():  # Use task_id from items()
                cursor.execute(
                    "INSERT INTO tasks (id, task_date, name, start_time, end_time, status) VALUES (?, ?, ?, ?, ?, ?)",  # Added id column
                    (
                        task_id,  # Added task_id
                        date_str,
                        task["name"],
                        task["start_time"].strftime("%H:%M:%S"),
                        task["end_time"].strftime("%H:%M:%S"),
                        task["status"],
                    ),
                )
            conn.commit()

    def _setup_styles(self):
        style = ttk.Style()
        style.configure(
            "OnTime.TLabel", foreground="green", font=("Helvetica", 10, "overstrike")
        )
        style.configure(
            "Delayed.TLabel", foreground="#E69B00", font=("Helvetica", 10, "overstrike")
        )
        style.configure(
            "Failed.TLabel",
            foreground="#FF0000",
            font=("Helvetica", 10, "overstrike"),  # 빨간색
        )
        style.configure("Pending.TLabel", font=("Helvetica", 10))
        style.configure("Timer.TLabel", font=("Helvetica", 36, "bold"))
        style.configure(
            "Paused.Timer.TLabel", foreground="red", font=("Helvetica", 36, "bold")
        )
        style.configure("Date.TButton", font=("Helvetica", 12, "bold"))

    def _create_widgets(self):
        paned_window = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned_window.pack(expand=True, fill=tk.BOTH)

        left_pane = ttk.Frame(paned_window, width=450)
        paned_window.add(left_pane, weight=2)
        self._create_left_pane_widgets(left_pane)

        right_pane = ttk.Frame(paned_window)
        paned_window.add(right_pane, weight=3)

        # 창 크기 변경 시 이벤트 바인딩 (적응형 디바운싱 적용)
        self._resize_timer = None
        self._resize_count = 0
        self._last_resize_time = 0
        self.root.bind("<Configure>", self._on_window_resize)

        # 창 최소화/복원 이벤트 바인딩
        self.root.bind("<Unmap>", self._on_window_minimize)
        self.root.bind("<Map>", self._on_window_restore)

        self._create_right_pane_widgets(right_pane)

    def _create_left_pane_widgets(self, parent):
        left_frame = ttk.Frame(parent, padding="10")
        left_frame.pack(expand=True, fill=tk.BOTH)

        # --- Date Navigation ---
        date_nav_frame = ttk.Frame(left_frame)
        date_nav_frame.pack(pady=(0, 10), fill=tk.X)
        self.prev_day_button = ttk.Button(
            date_nav_frame, text="◀", command=self._go_to_previous_day, width=3
        )
        self.prev_day_button.pack(side=tk.LEFT, padx=(0, 5))
        self.date_button = ttk.Button(
            date_nav_frame,
            text="",
            command=self._show_calendar_popup,
            style="Date.TButton",
        )
        self.date_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        self.next_day_button = ttk.Button(
            date_nav_frame, text="▶", command=self._go_to_next_day, width=3
        )
        self.next_day_button.pack(side=tk.LEFT, padx=(5, 0))

        # --- Pomodoro Timer ---
        self.timer_frame = ttk.LabelFrame(
            left_frame, text="포모도로 타이머", padding="10"
        )
        self.timer_frame.pack(fill=tk.X, pady=5)
        self.time_label = ttk.Label(self.timer_frame, style="Timer.TLabel")
        self.time_label.pack(pady=5)
        control_frame = ttk.Frame(self.timer_frame)
        control_frame.pack()
        self.start_pause_button = ttk.Button(
            control_frame, text="", command=self._toggle_pomodoro_state
        )
        self.start_pause_button.pack(side=tk.LEFT, padx=5)
        self.reset_button = ttk.Button(
            control_frame, text="리셋", command=self._reset_pomodoro
        )
        self.reset_button.pack(side=tk.LEFT, padx=5)

        # --- Task Management ---
        self.task_manager_frame = ttk.LabelFrame(
            left_frame, text="작업 관리", padding="10"
        )
        self.task_manager_frame.pack(fill=tk.X, pady=5)

        add_task_frame = ttk.Frame(self.task_manager_frame)
        add_task_frame.pack(fill=tk.X, pady=5)
        self.task_name_entry = ttk.Entry(add_task_frame)
        self.task_name_entry.pack(fill=tk.X, expand=True, pady=2)

        time_input_frame = ttk.Frame(add_task_frame)
        time_input_frame.pack(fill=tk.X, pady=2)
        ttk.Label(time_input_frame, text="시작:").pack(side=tk.LEFT)
        self.start_hour = tk.Spinbox(
            time_input_frame, from_=0, to=23, width=2, format="%02.f"
        )
        self.start_hour.pack(side=tk.LEFT)
        ttk.Label(time_input_frame, text=":").pack(side=tk.LEFT)
        self.start_minute = tk.Spinbox(
            time_input_frame, from_=0, to=59, width=2, format="%02.f"
        )
        self.start_minute.pack(side=tk.LEFT)
        ttk.Label(time_input_frame, text=" 종료:").pack(side=tk.LEFT)
        self.end_hour = tk.Spinbox(
            time_input_frame, from_=0, to=23, width=2, format="%02.f"
        )
        self.end_hour.pack(side=tk.LEFT)
        ttk.Label(time_input_frame, text=":").pack(side=tk.LEFT)
        self.end_minute = tk.Spinbox(
            time_input_frame, from_=0, to=59, width=2, format="%02.f"
        )
        self.end_minute.pack(side=tk.LEFT)

        self.add_task_button = ttk.Button(
            add_task_frame, text="작업 추가", command=self._add_task
        )
        self.add_task_button.pack(pady=5)

        # 작업 목록을 스크롤 가능한 프레임으로 만들기
        task_list_container = ttk.Frame(self.task_manager_frame)
        task_list_container.pack(fill=tk.BOTH, pady=5)

        # Canvas와 스크롤바 생성
        self.task_canvas = tk.Canvas(
            task_list_container,
            height=200,
            background=ttk.Style().lookup("TFrame", "background"),
            highlightthickness=0,
        )
        task_scrollbar = ttk.Scrollbar(
            task_list_container, orient="vertical", command=self.task_canvas.yview
        )
        self.task_canvas.configure(yscrollcommand=task_scrollbar.set)

        # 스크롤바와 캔버스 배치
        task_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.task_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 마우스 휠 스크롤 바인딩 추가
        self._bind_mouse_wheel_scroll(self.task_canvas)

        # 작업 목록 프레임을 캔버스에 배치
        self.task_list_frame = ttk.Frame(self.task_canvas)
        task_list_window = self.task_canvas.create_window(
            (0, 0), window=self.task_list_frame, anchor="nw"
        )

        # 캔버스 크기가 변경될 때마다 내부 프레임의 너비를 맞추는 함수
        def _configure_task_list_frame(event):
            canvas_width = event.width
            self.task_canvas.itemconfig(task_list_window, width=canvas_width)

        # 스크롤 영역 업데이트 및 너비 조정을 위한 바인딩
        self.task_list_frame.bind(
            "<Configure>",
            lambda e: self.task_canvas.configure(
                scrollregion=self.task_canvas.bbox("all")
            ),
        )
        self.task_canvas.bind("<Configure>", _configure_task_list_frame)

        # 작업 목록에 추가 이벤트 바인딩
        self.task_canvas.bind("<Enter>", lambda e: self.task_canvas.focus_set())
        self.task_canvas.bind("<FocusIn>", lambda e: self._update_task_scroll_region())

        # 마우스 드래그 스크롤 지원
        self.task_canvas.bind("<Button-1>", self._start_scroll_drag)
        self.task_canvas.bind("<B1-Motion>", self._on_scroll_drag)
        self.task_canvas.bind("<ButtonRelease-1>", self._stop_scroll_drag)

        # --- Stats ---
        self.stats_frame = ttk.LabelFrame(left_frame, text="통계", padding="10")
        self.stats_frame.pack(fill=tk.X, pady=5)

        # 통계 내용을 담을 스크롤 가능한 프레임
        stats_content_frame = ttk.Frame(self.stats_frame)
        stats_content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.stats_labels = {
            k: ttk.Label(stats_content_frame, text="")
            for k in [
                "completed",
                "success_rate",
                "focus_time",
                "task_completion",
                "streak",
            ]
        }
        for label in self.stats_labels.values():
            label.pack(anchor="w", pady=2)

        # 버튼들을 담을 프레임 (통계 하단에 중앙정렬)
        self.button_frame = ttk.Frame(stats_content_frame)
        self.button_frame.pack(pady=10)

        # 설정 버튼 (통계 분석 보기 버튼 왼쪽)
        settings_button = ttk.Button(
            self.button_frame, text="설정", command=self._open_settings_window
        )
        settings_button.pack(side=tk.LEFT, padx=(0, 10))

        # 통계 분석 보기 버튼
        analytics_button = ttk.Button(
            self.button_frame,
            text="통계 분석 보기",
            command=self._open_analytics_window,
        )
        analytics_button.pack(side=tk.LEFT, padx=(0, 10))

        # AI 생산성 진단 버튼
        ai_button = ttk.Button(
            self.button_frame, text="AI 생산성 진단", command=self._handle_ai_diagnosis
        )
        ai_button.pack(side=tk.LEFT, padx=(0, 10))

        # 통계 프레임에 이벤트 바인딩 추가
        self.stats_frame.bind("<Enter>", lambda e: self._on_stats_frame_enter())
        self.stats_frame.bind("<Leave>", lambda e: self._on_stats_frame_leave())

        # 통계 프레임에 마우스 휠 스크롤 지원 추가
        self._bind_mouse_wheel_scroll(stats_content_frame)

    def _create_right_pane_widgets(self, parent):
        container = ttk.Frame(parent)
        container.pack(expand=True, fill=tk.BOTH)
        self.calendar_canvas = tk.Canvas(container, bg="white")
        scrollbar = ttk.Scrollbar(
            container, orient="vertical", command=self.calendar_canvas.yview
        )
        self.calendar_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.calendar_canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        # 마우스 휠 스크롤 바인딩 추가
        self._bind_mouse_wheel_scroll(self.calendar_canvas)

        # 마우스 드래그 스크롤 지원 추가
        self.calendar_canvas.bind("<Button-1>", self._start_calendar_scroll_drag)
        self.calendar_canvas.bind("<B1-Motion>", self._on_calendar_scroll_drag)

    def _go_to_previous_day(self):
        # 사용자 수동 날짜 변경 플래그 설정
        self.user_manually_changed_date = True
        
        self.selected_date -= timedelta(days=1)
        self._update_date_view()

    def _go_to_next_day(self):
        if self.selected_date < datetime.now().date():
            # 사용자 수동 날짜 변경 플래그 설정
            self.user_manually_changed_date = True
            
            self.selected_date += timedelta(days=1)
            self._update_date_view()
        else:
            messagebox.showinfo("알림", "미래 날짜로는 이동할 수 없습니다.")

    def _show_calendar_popup(self):
        """달력 팝업을 표시하여 날짜를 선택할 수 있게 합니다."""
        popup = tk.Toplevel(self.root)
        popup.title("날짜 선택")
        popup.geometry("300x250")
        popup.transient(self.root)
        popup.grab_set()

        cal = Calendar(
            popup,
            selectmode="day",
            date_pattern="y-mm-dd",
            year=self.selected_date.year,
            month=self.selected_date.month,
            day=self.selected_date.day,
        )
        cal.pack(pady=20)

        def on_date_select():
            selected = cal.get_date()
            try:
                new_date = datetime.strptime(selected, "%Y-%m-%d").date()
                if new_date <= datetime.now().date():
                    # 사용자 수동 날짜 변경 플래그 설정
                    self.user_manually_changed_date = True
                    
                    self.selected_date = new_date
                    self._update_date_view()
                    popup.destroy()
                else:
                    messagebox.showwarning("경고", "미래 날짜는 선택할 수 없습니다.")
            except ValueError:
                messagebox.showerror("오류", "날짜 형식이 올바르지 않습니다.")

        button_frame = ttk.Frame(popup)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="선택", command=on_date_select).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="취소", command=popup.destroy).pack(
            side=tk.LEFT, padx=5
        )

        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (popup.winfo_width() // 2)
        y = (popup.winfo_screenheight() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")

    def _update_date_view(self):
        """Handles all UI updates when the selected date changes."""
        date_text = self.selected_date.strftime("%Y-%m-%d")
        is_today = self.selected_date == datetime.now().date()

        if is_today:
            date_text += " (오늘)"
            self.stats_frame.config(text="통계 (오늘)")
        else:
            self.stats_frame.config(
                text=f"통계 ({self.selected_date.strftime('%Y-%m-%d')})"
            )

        self.date_button.config(text=date_text)

        self.next_day_button.config(state=tk.NORMAL if not is_today else tk.DISABLED)
        self.add_task_button.config(state=tk.NORMAL if is_today else tk.DISABLED)

        self._load_data_for_selected_date()

    def _open_settings_window(self):
        """설정 창을 엽니다."""
        settings_win = tk.Toplevel(self.root)
        settings_win.title("설정")
        settings_win.geometry("450x450")  # 창 크기 확대
        settings_win.transient(self.root)
        settings_win.grab_set()

        # 소리 설정 프레임
        sound_frame = ttk.LabelFrame(settings_win, text="알림음 설정", padding="10")
        sound_frame.pack(fill=tk.X, padx=10, pady=10)

        # 소리 타입 선택 (라디오 버튼)
        ttk.Label(sound_frame, text="알림음 타입:").pack(anchor=tk.W)
        ttk.Radiobutton(
            sound_frame,
            text="커스텀 (TeamRadioF1.wav)",
            variable=self.sound_type,
            value="custom",
        ).pack(anchor=tk.W, padx=10)
        ttk.Radiobutton(
            sound_frame,
            text="기본 시스템 알림음",
            variable=self.sound_type,
            value="default",
        ).pack(anchor=tk.W, padx=10)

        # 볼륨 설정
        volume_frame = ttk.Frame(sound_frame)
        volume_frame.pack(fill=tk.X, pady=10)
        ttk.Label(volume_frame, text="볼륨:").pack(side=tk.LEFT)
        volume_spinbox = tk.Spinbox(
            volume_frame,
            from_=0,
            to=100,
            width=5,
            textvariable=self.sound_volume,
            command=self._preview_sound,
        )
        volume_spinbox.pack(side=tk.LEFT, padx=5)
        ttk.Label(volume_frame, text="%").pack(side=tk.LEFT)

        # 데이터 관리 프레임
        data_frame = ttk.LabelFrame(settings_win, text="데이터 관리", padding="10")
        data_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        # 경고 메시지
        warning_label = ttk.Label(
            data_frame,
            text="⚠️ 주의: 데이터 삭제는 되돌릴 수 없습니다!",
            foreground="red",
            font=("Arial", 9, "bold"),
        )
        warning_label.pack(pady=(0, 10))

        # 데이터 삭제 버튼
        delete_button = ttk.Button(
            data_frame,
            text="🗑️ 모든 데이터 삭제",
            command=lambda: self._confirm_data_deletion(settings_win),
            style="Danger.TButton",
        )
        delete_button.pack(pady=5)

        # 설정 저장/취소 버튼
        button_frame = ttk.Frame(settings_win)
        button_frame.pack(side=tk.BOTTOM, pady=10)
        ttk.Button(
            button_frame,
            text="저장",
            command=lambda: [self._save_settings(), settings_win.destroy()],
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="취소", command=settings_win.destroy).pack(
            side=tk.LEFT, padx=5
        )

        # 창 중앙 정렬
        settings_win.update_idletasks()
        x = (settings_win.winfo_screenwidth() // 2) - (settings_win.winfo_width() // 2)
        y = (settings_win.winfo_screenheight() // 2) - (
            settings_win.winfo_height() // 2
        )
        settings_win.geometry(f"+{x}+{y}")

    def _preview_sound(self):
        """설정에서 볼륨이 변경될 때 사운드 미리보기를 재생합니다."""
        self._play_notification_sound()

    def _save_settings(self):
        """설정을 저장합니다."""
        # 소리 설정은 이미 StringVar로 연결되어 있어서 자동으로 저장됨
        pass

    def _open_analytics_window(self):
        if not MATPLOTLIB_AVAILABLE:
            messagebox.showerror(
                "라이브러리 오류",
                "통계 그래프를 표시하려면 Matplotlib와 Pandas가 필요합니다.\n\n터미널에서 아래 명령어를 실행해주세요:\npip install matplotlib pandas",
            )
            return
        analytics_win = tk.Toplevel(self.root)
        analytics_win.title("Analytics")
        analytics_win.geometry("800x600")

        # 창을 최상위로 가져오기
        analytics_win.lift()
        analytics_win.focus_force()
        analytics_win.grab_set()  # 모달 창으로 만들기
        graph_frame = ttk.Frame(analytics_win)
        graph_frame.pack(expand=True, fill=tk.BOTH, side=tk.BOTTOM)
        button_frame = ttk.Frame(analytics_win, padding=5)
        button_frame.pack(fill=tk.X, side=tk.TOP)
        btn1 = ttk.Button(
            button_frame,
            text="주간 집중량 추이",
            command=lambda: self._plot_weekly_focus(graph_frame),
        )
        btn1.pack(side=tk.LEFT, padx=5)
        btn2 = ttk.Button(
            button_frame,
            text="시간대별 생산성",
            command=lambda: self._plot_hourly_productivity(graph_frame),
        )
        btn2.pack(side=tk.LEFT, padx=5)
        btn3 = ttk.Button(
            button_frame,
            text="작업 상태 비율",
            command=lambda: self._plot_task_status_pie(graph_frame),
        )
        btn3.pack(side=tk.LEFT, padx=5)
        self._plot_weekly_focus(graph_frame)

    def _clear_graph_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def _plot_weekly_focus(self, frame):
        self._clear_graph_frame(frame)
        conn = sqlite3.connect(self.db_path)
        today = datetime.now().date()
        start_date = today - timedelta(days=6)
        query = f"SELECT date, total_focus_seconds FROM daily_summary WHERE date BETWEEN '{start_date}' AND '{today}'"
        df = pd.read_sql_query(query, conn)
        conn.close()
        if df.empty:
            ttk.Label(frame, text="표시할 데이터가 없습니다.").pack()
            return
        df["date"] = pd.to_datetime(df["date"])
        df["hours"] = df["total_focus_seconds"] / 3600
        df.set_index("date", inplace=True)
        fig, ax = plt.subplots(figsize=(8, 5))
        df["hours"].plot(kind="bar", ax=ax, color="#a1c4fd")
        ax.set_title("Weekly Focus Time (Hours)")
        ax.set_xlabel("Date")
        ax.set_ylabel("Focus Time (Hours)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)

    def _plot_hourly_productivity(self, frame):
        self._clear_graph_frame(frame)
        conn = sqlite3.connect(self.db_path)
        query = "SELECT start_time, end_time FROM tasks WHERE status IN ('on-time', 'delayed')"
        df = pd.read_sql_query(query, conn)
        conn.close()
        if df.empty:
            ttk.Label(frame, text="표시할 데이터가 없습니다.").pack()
            return
        hourly_focus = collections.defaultdict(float)
        for _, row in df.iterrows():
            start = datetime.strptime(row["start_time"], "%H:%M:%S").hour
            end = datetime.strptime(row["end_time"], "%H:%M:%S").hour
            for hour in range(start, end + 1):
                hourly_focus[hour] += 1
        if not hourly_focus:
            ttk.Label(frame, text="표시할 데이터가 없습니다.").pack()
            return
        s = pd.Series(hourly_focus).sort_index()
        fig, ax = plt.subplots(figsize=(8, 5))
        s.plot(kind="bar", ax=ax, color="#f9e2af")
        ax.set_title("Hourly Productivity (Completed Tasks)")
        ax.set_xlabel("Hour")
        ax.set_ylabel("Number of Tasks")
        plt.xticks(rotation=0)
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)

    def _plot_task_status_pie(self, frame):
        self._clear_graph_frame(frame)
        conn = sqlite3.connect(self.db_path)
        query = f"SELECT status FROM tasks WHERE task_date = '{self.selected_date.strftime('%Y-%m-%d')}'"
        df = pd.read_sql_query(query, conn)
        conn.close()
        if df.empty:
            ttk.Label(frame, text="표시할 데이터가 없습니다.").pack()
            return
        status_counts = df["status"].value_counts()
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.pie(
            status_counts,
            labels=status_counts.index,
            autopct="%1.1f%%",
            startangle=90,
            colors=["#f38ba8", "#f9e2af", "#a6e3a1", "#a1c4fd"],
        )
        ax.axis("equal")
        ax.set_title(f'{self.selected_date.strftime("%Y-%m-%d")} Task Status')
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)

    def _handle_ai_diagnosis(self):
        """AI 생산성 진단 시작 핸들러 - 고도화된 버전"""
        # AI 서비스 선택 및 API 키 입력을 위한 고급 설정 창
        self.ai_settings_win = tk.Toplevel(self.root)
        self.ai_settings_win.title("AI 생산성 진단 설정")
        self.ai_settings_win.geometry("700x600")
        self.ai_settings_win.transient(self.root)
        self.ai_settings_win.grab_set()

        # 스크롤 가능한 메인 컨테이너
        main_container = ttk.Frame(self.ai_settings_win)
        main_container.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # 캔버스와 스크롤바 생성
        canvas = tk.Canvas(
            main_container,
            background=ttk.Style().lookup("TFrame", "background"),
            highlightthickness=0,
        )
        scrollbar = ttk.Scrollbar(
            main_container, orient="vertical", command=canvas.yview
        )

        # 스크롤 가능한 프레임
        scrollable_frame = ttk.Frame(canvas, padding="20")

        # 스크롤바와 캔버스 연결
        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 마우스 휠 스크롤 바인딩
        self._bind_mouse_wheel_scroll(canvas)

        # 스크롤바와 캔버스 배치
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # 메인 프레임 (스크롤 가능한 프레임 내부)
        main_frame = scrollable_frame

        # 제목
        title_label = ttk.Label(
            main_frame, text=" AI 생산성 진단 시스템", font=("Helvetica", 18, "bold")
        )
        title_label.pack(pady=(0, 25))

        # AI 서비스 선택 프레임
        service_frame = ttk.LabelFrame(main_frame, text=" AI 서비스 선택", padding="20")
        service_frame.pack(fill=tk.X, pady=(0, 20))

        # AI 서비스 목록
        self.ai_services = [
            {
                "id": "claude",
                "name": "Claude (Anthropic)",
                "icon": "🤖",
                "color": "purple",
            },
            {"id": "gpt", "name": "GPT (OpenAI)", "icon": "🧠", "color": "green"},
            {"id": "groq", "name": "Groq", "icon": "⚡", "color": "blue"},
            {"id": "perplexity", "name": "Perplexity", "icon": "🔍", "color": "orange"},
            {
                "id": "gemini",
                "name": "Gemini (Google)",
                "icon": "🌟",
                "color": "yellow",
            },
        ]

        self.selected_service = tk.StringVar(value="claude")

        for service in self.ai_services:
            service_btn = ttk.Radiobutton(
                service_frame,
                text=f"{service['icon']} {service['name']}",
                variable=self.selected_service,
                value=service["id"],
                command=self._on_service_changed,
            )
            service_btn.pack(anchor=tk.W, pady=2)

        # API 키 입력 프레임
        api_frame = ttk.LabelFrame(main_frame, text="API 키 설정", padding="15")
        api_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(api_frame, text="선택한 AI 서비스의 API 키를 입력하세요:").pack(
            anchor=tk.W, pady=(0, 10)
        )

        # API 키 입력 필드
        key_frame = ttk.Frame(api_frame)
        key_frame.pack(fill=tk.X, pady=(0, 10))

        self.api_key_entry = ttk.Entry(key_frame, show="*", width=50)
        self.api_key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        # API 키 표시/숨김 버튼
        self.show_key_btn = ttk.Button(
            key_frame, text="👁️", width=3, command=self._toggle_api_key_visibility
        )
        self.show_key_btn.pack(side=tk.RIGHT, padx=(5, 0))

        # API 키 삭제 버튼
        self.delete_key_btn = ttk.Button(
            key_frame, text="🗑️", width=3, command=self._delete_api_key
        )
        self.delete_key_btn.pack(side=tk.RIGHT)

        # API 키 표시 상태
        self.api_key_visible = False

        # 저장된 API 키 불러오기
        self._load_saved_api_key()

        # 분석 옵션 프레임
        options_frame = ttk.LabelFrame(main_frame, text="분석 옵션", padding="15")
        options_frame.pack(fill=tk.X, pady=(0, 15))

        # 분석 기간 선택
        period_frame = ttk.Frame(options_frame)
        period_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(period_frame, text="분석 기간:").pack(side=tk.LEFT)
        self.analysis_period = tk.StringVar(value="7")
        period_combo = ttk.Combobox(
            period_frame,
            textvariable=self.analysis_period,
            values=["3", "7", "14", "30"],
            width=10,
            state="readonly",
        )
        period_combo.pack(side=tk.LEFT, padx=(10, 0))

        # 분석 깊이 선택
        depth_frame = ttk.Frame(options_frame)
        depth_frame.pack(fill=tk.X)

        ttk.Label(depth_frame, text="분석 깊이:").pack(side=tk.LEFT)
        self.analysis_depth = tk.StringVar(value="detailed")
        depth_combo = ttk.Combobox(
            depth_frame,
            textvariable=self.analysis_depth,
            values=["basic", "detailed", "comprehensive"],
            width=15,
            state="readonly",
        )
        depth_combo.pack(side=tk.LEFT, padx=(10, 0))

        # 버튼 프레임
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(20, 0))

        ttk.Button(
            button_frame, text="취소", command=self.ai_settings_win.destroy
        ).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(
            button_frame, text="진단 시작", command=self._start_ai_diagnosis
        ).pack(side=tk.LEFT)

        # 창 중앙 정렬
        self.ai_settings_win.update_idletasks()
        screen_width = self.ai_settings_win.winfo_screenwidth()
        screen_height = self.ai_settings_win.winfo_screenheight()
        x = (screen_width - 700) // 2
        y = (screen_height - 600) // 2
        self.ai_settings_win.geometry(f"700x600+{x}+{y}")

    def _toggle_api_key_visibility(self):
        """API 키 표시/숨김 토글"""
        if self.api_key_visible:
            self.api_key_entry.config(show="*")
            self.show_key_btn.config(text="👁️")
            self.api_key_visible = False
        else:
            self.api_key_entry.config(show="")
            self.show_key_btn.config(text="🙈")
            self.api_key_visible = True

    def _start_ai_diagnosis(self):
        """AI 진단 시작"""
        api_key = self.api_key_entry.get().strip()
        if not api_key:
            messagebox.showwarning(
                "API 키 오류", "API 키를 입력해야 합니다.", parent=self.ai_settings_win
            )
            return

        # API 키 유효성 검증
        if not self._validate_api_key(api_key):
            messagebox.showwarning(
                "API 키 오류",
                "올바른 API 키 형식이 아닙니다.",
                parent=self.ai_settings_win,
            )
            return

        # API 키를 로컬에 저장
        self._save_api_key(api_key)

        self.api_key = api_key
        self.selected_ai_service = self.selected_service.get()
        self.analysis_days = int(self.analysis_period.get())
        self.analysis_level = self.analysis_depth.get()

        self.ai_settings_win.destroy()
        self._open_advanced_ai_diagnosis_window()

    def _validate_api_key(self, api_key):
        """API 키 형식 검증"""
        if not api_key or len(api_key) < 10:
            return False

        # 서비스별 기본 검증
        service_id = self.selected_service.get()
        if service_id == "claude" and not api_key.startswith("sk-ant-"):
            return False
        elif service_id == "gpt" and not api_key.startswith("sk-"):
            return False
        elif service_id == "groq" and not api_key.startswith("gsk_"):
            return False
        elif service_id == "perplexity" and not api_key.startswith("pplx-"):
            return False

        return True

    def _load_saved_api_key(self):
        """저장된 API 키를 불러옵니다."""
        try:
            service_id = self.selected_service.get()
            saved_key = self._get_saved_api_key(service_id)
            if saved_key:
                self.api_key_entry.delete(0, tk.END)
                self.api_key_entry.insert(0, saved_key)
                self.delete_key_btn.config(state="normal")
            else:
                self.delete_key_btn.config(state="disabled")
        except Exception as e:
            print(f"API 키 불러오기 실패: {e}")

    def _save_api_key(self, api_key):
        """API 키를 로컬에 저장합니다."""
        try:
            service_id = self.selected_service.get()
            key_name = f"pomodoro_{service_id}_api_key"
            self._save_to_local_storage(key_name, api_key)
            self.delete_key_btn.config(state="normal")
            print(f"{service_id} API 키가 저장되었습니다.")
        except Exception as e:
            print(f"API 키 저장 실패: {e}")

    def _delete_api_key(self):
        """저장된 API 키를 삭제합니다."""
        try:
            service_id = self.selected_service.get()
            key_name = f"pomodoro_{service_id}_api_key"
            self._remove_from_local_storage(key_name)
            self.api_key_entry.delete(0, tk.END)
            self.delete_key_btn.config(state="disabled")
            print(f"{service_id} API 키가 삭제되었습니다.")
        except Exception as e:
            print(f"API 키 삭제 실패: {e}")

    def _get_saved_api_key(self, service_id):
        """저장된 API 키를 가져옵니다."""
        try:
            key_name = f"pomodoro_{service_id}_api_key"
            return self._load_from_local_storage(key_name)
        except Exception as e:
            print(f"저장된 API 키 불러오기 실패: {e}")
            return None

    def _save_to_local_storage(self, key, value):
        """로컬 스토리지에 데이터를 저장합니다."""
        try:
            # 간단한 파일 기반 저장 (실제 환경에서는 더 안전한 방법 사용 권장)
            import json
            import os

            # 사용자 홈 디렉토리에 설정 파일 저장
            home_dir = os.path.expanduser("~")
            config_dir = os.path.join(home_dir, ".pomodoro_app")
            os.makedirs(config_dir, exist_ok=True)

            config_file = os.path.join(config_dir, "api_keys.json")

            # 기존 설정 로드
            config = {}
            if os.path.exists(config_file):
                try:
                    with open(config_file, "r", encoding="utf-8") as f:
                        config = json.load(f)
                except:
                    config = {}

            # 새 설정 추가
            config[key] = value

            # 설정 저장
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"로컬 스토리지 저장 실패: {e}")

    def _load_from_local_storage(self, key):
        """로컬 스토리지에서 데이터를 불러옵니다."""
        try:
            import json
            import os

            home_dir = os.path.expanduser("~")
            config_dir = os.path.join(home_dir, ".pomodoro_app")
            config_file = os.path.join(config_dir, "api_keys.json")

            if os.path.exists(config_file):
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    return config.get(key)
            return None

        except Exception as e:
            print(f"로컬 스토리지 불러오기 실패: {e}")
            return None

    def _remove_from_local_storage(self, key):
        """로컬 스토리지에서 데이터를 삭제합니다."""
        try:
            import json
            import os

            home_dir = os.path.expanduser("~")
            config_dir = os.path.join(home_dir, ".pomodoro_app")
            config_file = os.path.join(config_dir, "api_keys.json")

            if os.path.exists(config_file):
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)

                if key in config:
                    del config[key]

                with open(config_file, "w", encoding="utf-8") as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"로컬 스토리지 삭제 실패: {e}")

    def _on_service_changed(self):
        """AI 서비스가 변경되었을 때 호출됩니다."""
        try:
            # 현재 선택된 서비스의 저장된 API 키 불러오기
            self._load_saved_api_key()
        except Exception as e:
            print(f"서비스 변경 처리 실패: {e}")

    def _open_advanced_ai_diagnosis_window(self):
        """AI 진단 창을 엽니다."""
        self.diag_win = tk.Toplevel(self.root)
        self.diag_win.title(f"AI 생산성 진단 결과 - {self.selected_ai_service.upper()}")
        self.diag_win.geometry("900x600")  # 높이를 600으로 설정
        self.diag_win.transient(self.root)

        # 메인 컨테이너 (버튼 영역을 제외한 스크롤 가능한 영역)
        main_container = ttk.Frame(self.diag_win)
        main_container.pack(expand=True, fill=tk.BOTH, padx=10, pady=(10, 0))

        # 상단 정보 프레임
        info_frame = ttk.LabelFrame(main_container, text="분석 정보", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))

        info_text = f"AI 서비스: {self.selected_ai_service.upper()}\n"
        info_text += f"분석 기간: 최근 {self.analysis_days}일\n"
        info_text += f"분석 수준: {self.analysis_level}"

        info_label = ttk.Label(info_frame, text=info_text, font=("Helvetica", 10))
        info_label.pack(anchor=tk.W)

        # 진행 상황 표시
        progress_frame = ttk.Frame(main_container)
        progress_frame.pack(fill=tk.X, pady=(0, 10))

        self.progress_label = ttk.Label(
            progress_frame, text="🔍 데이터 수집 중...", font=("Helvetica", 11)
        )
        self.progress_label.pack()

        self.progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate")
        self.progress_bar.pack(fill=tk.X, pady=(5, 0))
        self.progress_bar.start()

        # 결과 표시 영역 (스크롤 가능)
        result_frame = ttk.LabelFrame(main_container, text="진단 결과", padding="10")
        result_frame.pack(expand=True, fill=tk.BOTH)

        # 텍스트 위젯과 스크롤바 (마우스 휠 스크롤 지원)
        text_frame = ttk.Frame(result_frame)
        text_frame.pack(expand=True, fill=tk.BOTH)

        # 가독성을 위한 텍스트 위젯 스타일 설정
        self.result_text = tk.Text(
            text_frame,
            wrap="word",
            state="disabled",
            font=("Helvetica", 11),
            bg="#ffffff",  # 흰색 배경
            fg="#1f2937",  # 진한 회색 텍스트
            selectbackground="#3b82f6",  # 파란색 선택 영역
            selectforeground="white",
            relief="solid",
            borderwidth=1,
            padx=15,
            pady=15,
            spacing1=2,  # 문단 위 여백
            spacing2=1,  # 문단 간 여백
            spacing3=2,  # 문단 아래 여백
        )

        # 스크롤바 설정
        scrollbar = ttk.Scrollbar(
            text_frame, orient="vertical", command=self.result_text.yview
        )
        self.result_text.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        # 하단 버튼 (메인 컨테이너 밖에 고정 배치)
        button_frame = ttk.Frame(self.diag_win)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 10))

        # 새로고침 버튼
        refresh_btn = ttk.Button(
            button_frame, text=" 새로고침", command=self._refresh_ai_analysis
        )
        refresh_btn.pack(side=tk.LEFT)

        # 결과 저장 버튼
        save_btn = ttk.Button(
            button_frame, text=" 결과 저장", command=self._save_ai_analysis
        )
        save_btn.pack(side=tk.LEFT, padx=(10, 0))

        # 닫기 버튼
        close_btn = ttk.Button(
            button_frame, text=" 닫기", command=self.diag_win.destroy
        )
        close_btn.pack(side=tk.RIGHT)

        # 분석 시작
        self.root.after(500, lambda: self._perform_advanced_ai_diagnosis())

    def _perform_advanced_ai_diagnosis(self):
        """고도화된 AI 진단 수행"""
        try:
            # 1단계: 데이터 수집
            self._update_progress("📊 데이터 수집 중...")
            data = self._collect_comprehensive_data()

            # 2단계: 데이터 전처리
            self._update_progress("🔧 데이터 전처리 중...")
            processed_data = self._preprocess_data(data)

            # 3단계: AI 분석
            self._update_progress("🤖 AI 분석 수행 중...")
            analysis_result = self._call_ai_analysis(processed_data)

            # 4단계: 결과 표시
            self._update_progress("✨ 분석 완료!")
            self._display_analysis_result(analysis_result)

        except Exception as e:
            self._handle_analysis_error(e)

    def _update_progress(self, message):
        """진행 상황 업데이트"""
        self.progress_label.config(text=message)
        self.diag_win.update_idletasks()

    def _collect_comprehensive_data(self):
        """포괄적인 데이터 수집"""
        try:
            conn = sqlite3.connect(self.db_path)
            start_date = datetime.now().date() - timedelta(days=self.analysis_days)

            # 일일 요약 데이터
            summary_query = f"SELECT * FROM daily_summary WHERE date >= '{start_date}' ORDER BY date"
            summary_df = pd.read_sql_query(summary_query, conn)

            # 작업 데이터
            tasks_query = f"SELECT * FROM tasks WHERE task_date >= '{start_date}' ORDER BY task_date, start_time"
            tasks_df = pd.read_sql_query(tasks_query, conn)

            # 추가 통계 계산
            if not summary_df.empty:
                summary_df["date"] = pd.to_datetime(summary_df["date"])
                summary_df["success_rate"] = (
                    summary_df["pomodoro_success"]
                    / (summary_df["pomodoro_success"] + summary_df["pomodoro_failure"])
                ) * 100
                summary_df["focus_hours"] = summary_df["total_focus_seconds"] / 3600

            conn.close()

            return {
                "summary": summary_df,
                "tasks": tasks_df,
                "period_days": self.analysis_days,
                "analysis_level": self.analysis_level,
            }

        except Exception as e:
            raise Exception(f"데이터 수집 실패: {e}")

    def _preprocess_data(self, data):
        """데이터 전처리 및 분석 준비"""
        try:
            summary_df = data["summary"]
            tasks_df = data["tasks"]

            # 기본 통계 계산
            stats = {}

            if not summary_df.empty:
                stats["total_days"] = len(summary_df)
                stats["total_pomodoros"] = summary_df["completed_pomodoros"].sum()
                stats["total_focus_hours"] = summary_df["focus_hours"].sum()
                stats["avg_success_rate"] = summary_df["success_rate"].mean()
                stats["best_day"] = summary_df.loc[
                    summary_df["focus_hours"].idxmax(), "date"
                ].strftime("%Y-%m-%d")
                stats["worst_day"] = summary_df.loc[
                    summary_df["focus_hours"].idxmin(), "date"
                ].strftime("%Y-%m-%d")

            if not tasks_df.empty:
                task_status_counts = tasks_df["status"].value_counts()
                stats["total_tasks"] = len(tasks_df)
                stats["completed_tasks"] = task_status_counts.get(
                    "on-time", 0
                ) + task_status_counts.get("delayed", 0)
                stats["failed_tasks"] = task_status_counts.get("failed", 0)
                stats["task_completion_rate"] = (
                    (stats["completed_tasks"] / stats["total_tasks"]) * 100
                    if stats["total_tasks"] > 0
                    else 0
                )

            # 패턴 분석
            patterns = self._analyze_productivity_patterns(summary_df, tasks_df)

            return {"stats": stats, "patterns": patterns, "raw_data": data}

        except Exception as e:
            raise Exception(f"데이터 전처리 실패: {e}")

    def _analyze_productivity_patterns(self, summary_df, tasks_df):
        """생산성 패턴 분석"""
        patterns = {}

        try:
            if not summary_df.empty:
                # 요일별 패턴
                summary_df["weekday"] = summary_df["date"].dt.day_name()
                weekday_stats = (
                    summary_df.groupby("weekday")
                    .agg(
                        {
                            "focus_hours": "mean",
                            "completed_pomodoros": "mean",
                            "success_rate": "mean",
                        }
                    )
                    .round(2)
                )
                patterns["weekday_patterns"] = weekday_stats

                # 시간대별 패턴 (작업 데이터 기반)
                if not tasks_df.empty:
                    # 시간 형식을 명시적으로 지정하여 경고 제거
                    tasks_df["start_hour"] = pd.to_datetime(
                        tasks_df["start_time"], format="%H:%M:%S"
                    ).dt.hour
                    hour_stats = tasks_df.groupby("start_hour").size()
                    patterns["hourly_patterns"] = hour_stats

                # 트렌드 분석
                if len(summary_df) > 1:
                    patterns["trend"] = {
                        "focus_trend": (
                            "increasing"
                            if summary_df["focus_hours"].iloc[-1]
                            > summary_df["focus_hours"].iloc[0]
                            else "decreasing"
                        ),
                        "success_trend": (
                            "increasing"
                            if summary_df["success_rate"].iloc[-1]
                            > summary_df["success_rate"].iloc[0]
                            else "decreasing"
                        ),
                    }

        except Exception as e:
            patterns["error"] = f"패턴 분석 오류: {e}"

        return patterns

    def _call_ai_analysis(self, processed_data):
        """AI API 호출 및 분석 수행"""
        try:
            # AI 프롬프트 생성
            prompt = self._create_advanced_ai_prompt(processed_data)

            # 실제 AI API 호출 시도
            try:
                return self._call_real_ai_api(prompt, processed_data)
            except Exception as api_error:
                print(f"AI API 호출 실패: {api_error}")
                # API 호출 실패 시 fallback 분석 제공
                return self._get_fallback_analysis(processed_data)

        except Exception as e:
            raise Exception(f"AI 분석 실패: {e}")

    def _create_advanced_ai_prompt(self, processed_data):
        """고도화된 AI 프롬프트 생성"""
        stats = processed_data["stats"]
        patterns = processed_data["patterns"]

        prompt = f"""당신은 생산성 분석 및 개선 전문가입니다.
사용자의 실제 데이터를 바탕으로 구체적이고 실행 가능한 생산성 진단을 제공해주세요.

## 📊 분석 데이터 (실제 사용자 데이터)
- **분석 기간**: 최근 {processed_data['raw_data']['period_days']}일
- **총 집중 시간**: {stats.get('total_focus_hours', 0):.1f}시간
- **총 뽀모도로 세션**: {stats.get('total_pomodoros', 0)}회
- **평균 성공률**: {stats.get('avg_success_rate', 0):.1f}%
- **작업 완료율**: {stats.get('task_completion_rate', 0):.1f}%

## 🎯 분석 요청사항
{self.analysis_level.upper()} 수준의 분석을 요청합니다. 다음을 포함해주세요:

1. **종합 생산성 진단** (상세한 분석)
2. **강점 및 약점 분석** (구체적인 지표 기반)
3. **생산성 패턴 분석** (요일별, 시간대별 패턴)
4. **개선 전략 제안** (실행 가능한 5가지 팁)
5. **장기적 성장 방향** (목표 설정 및 추적 방법)

## 📈 추가 분석 요청
- 생산성 저하 원인 분석
- 최적의 작업 시간대 파악
- 스트레스 관리 방안
- 동기부여 전략

### 3. 생산성 패턴 분석 (구체적 패턴)
- **요일별 패턴**: 어떤 요일에 생산성이 높고 낮은지, 그 이유
- **시간대별 패턴**: 하루 중 최적/최악 생산성 시간대와 대응 방안
- **작업 유형별 패턴**: 집중 작업 vs 반복 작업의 효율성 차이

### 4. 개선 전략 제안 (실행 가능한 5가지)
- **즉시 실행 가능**: 오늘부터 시작할 수 있는 2가지
- **단기 개선**: 1주일 내에 적용할 수 있는 2가지
- **장기 전략**: 1개월 내에 구현할 수 있는 1가지

### 5. 구체적 실행 계획
- **목표 설정**: 1주일, 1개월, 3개월 단위의 구체적 목표
- **진행 추적**: 생산성 향상을 측정할 수 있는 KPI 제안
- **동기부여**: 지속적인 개선을 위한 동기부여 전략

## 📋 출력 형식 요청

### 필수 포함 요소:
1. **생산성 점수**: 1-100점 평가 + 근거
2. **핵심 문제점**: 3가지 주요 문제와 구체적 수치
3. **개선 우선순위**: 즉시/단기/장기 개선사항
4. **실행 체크리스트**: 구체적인 행동 항목
5. **성공 측정 방법**: 개선 효과를 확인할 수 있는 방법

### 작성 스타일:
- 한국어로 작성
- 구체적이고 실행 가능한 조언
- 수치와 데이터 기반 분석
- 실용적이고 현실적인 제안
- 사용자가 바로 적용할 수 있는 팁

분석 결과는 마크다운 형식으로 작성하고, 사용자가 실제로 행동할 수 있도록 구체적으로 작성해주세요."""

        return prompt

    def _call_real_ai_api(self, prompt, processed_data):
        """통합 AI API 호출 함수 - 모든 서비스 지원"""
        try:
            # API 키 확인 (디버깅 정보 추가)
            print(
                f"API 키 확인: hasattr={hasattr(self, 'api_key')}, api_key={getattr(self, 'api_key', 'None')[:10] if hasattr(self, 'api_key') and self.api_key else 'None'}"
            )

            if not hasattr(self, "api_key") or not self.api_key:
                raise Exception("API 키가 설정되지 않았습니다.")

            # 선택된 AI 서비스에 따른 통합 API 호출
            service_id = self.selected_ai_service.lower()
            print(f"선택된 AI 서비스: {service_id}")

            # 범용성 있는 통합 API 호출
            return self._call_unified_ai_api(prompt, service_id)

        except Exception as e:
            print(f"AI API 호출 실패: {e}")
            # API 호출 실패 시 기본 분석 결과 반환
            return self._get_fallback_analysis(processed_data)

    def _call_unified_ai_api(self, prompt, service_id):
        """범용성 있는 통합 AI API 호출 함수"""
        try:
            import requests

            # 서비스별 API 설정
            api_configs = {
                "claude": {
                    "url": "https://api.anthropic.com/v1/messages",
                    "headers": {
                        "Content-Type": "application/json",
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01",
                    },
                    "data": {
                        "model": "claude-3-sonnet-20240229",
                        "max_tokens": 4000,
                        "messages": [{"role": "user", "content": prompt}],
                    },
                    "response_path": ["content", 0, "text"],
                },
                "gpt": {
                    "url": "https://api.openai.com/v1/chat/completions",
                    "headers": {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}",
                    },
                    "data": {
                        "model": "gpt-4",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 4000,
                        "temperature": 0.7,
                    },
                    "response_path": ["choices", 0, "message", "content"],
                },
                "groq": {
                    "url": "https://api.groq.com/openai/v1/chat/completions",
                    "headers": {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}",
                    },
                    "data": {
                        "model": "llama3-8b-8192",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 4000,
                        "temperature": 0.7,
                    },
                    "response_path": ["choices", 0, "message", "content"],
                },
                "perplexity": {
                    "url": "https://api.perplexity.ai/chat/completions",
                    "headers": {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}",
                    },
                    "data": {
                        "model": "llama-3.1-8b-instant",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 4000,
                        "temperature": 0.7,
                    },
                    "response_path": ["choices", 0, "message", "content"],
                },
                "gemini": {
                    "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
                    "headers": {
                        "Content-Type": "application/json",
                        "X-goog-api-key": self.api_key,
                    },
                    "data": {"contents": [{"parts": [{"text": prompt}]}]},
                    "response_path": ["candidates", 0, "content", "parts", 0, "text"],
                },
            }

            if service_id not in api_configs:
                raise Exception(f"지원하지 않는 AI 서비스: {service_id}")

            config = api_configs[service_id]
            print(f"{service_id.upper()} API 호출 시작: {self.api_key[:10]}...")
            print(f"요청 URL: {config['url']}")

            response = requests.post(
                config["url"],
                headers=config["headers"],
                json=config["data"],
                timeout=60,
            )

            print(f"{service_id.upper()} API 응답 상태: {response.status_code}")

            if response.status_code == 200:
                result = response.json()

                # 응답 경로에 따라 결과 추출
                response_value = result
                for path_item in config["response_path"]:
                    if isinstance(path_item, int):
                        response_value = response_value[path_item]
                    else:
                        response_value = response_value[path_item]

                return response_value
            else:
                raise Exception(
                    f"{service_id.upper()} API 오류: {response.status_code} - {response.text}"
                )

        except Exception as e:
            raise Exception(f"{service_id.upper()} API 호출 실패: {e}")

    def _call_claude_api(self, prompt):
        """Claude API 호출"""
        try:
            import requests

            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
            }

            data = {
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 4000,
                "messages": [{"role": "user", "content": prompt}],
            }

            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=60,
            )

            if response.status_code == 200:
                result = response.json()
                return result["content"][0]["text"]
            else:
                raise Exception(
                    f"Claude API 오류: {response.status_code} - {response.text}"
                )

        except Exception as e:
            raise Exception(f"Claude API 호출 실패: {e}")

    def _call_gpt_api(self, prompt):
        """GPT API 호출"""
        try:
            import requests

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }

            data = {
                "model": "gpt-4",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 4000,
                "temperature": 0.7,
            }

            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=60,
            )

            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                raise Exception(
                    f"GPT API 오류: {response.status_code} - {response.text}"
                )

        except Exception as e:
            raise Exception(f"GPT API 호출 실패: {e}")

    def _call_groq_api(self, prompt):
        """Groq API 호출"""
        try:
            import requests

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }

            data = {
                "model": "llama3-8b-8192",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 4000,
                "temperature": 0.7,
            }

            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=60,
            )

            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                raise Exception(
                    f"Groq API 오류: {response.status_code} - {response.text}"
                )

        except Exception as e:
            raise Exception(f"Groq API 호출 실패: {e}")

    def _call_perplexity_api(self, prompt):
        """Perplexity API 호출"""
        try:
            import requests

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }

            data = {
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 4000,
                "temperature": 0.7,
            }

            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers=headers,
                json=data,
                timeout=60,
            )

            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                raise Exception(
                    f"Perplexity API 오류: {response.status_code} - {response.text}"
                )

        except Exception as e:
            raise Exception(f"Perplexity API 호출 실패: {e}")

    def _call_gemini_api(self, prompt):
        """Gemini API 호출 (구글 공식 스펙 적용)"""
        try:
            import requests

            # 구글 공식 스펙에 맞는 헤더 설정
            headers = {
                "Content-Type": "application/json",
                "X-goog-api-key": self.api_key,
            }

            # 구글 공식 스펙에 맞는 요청 데이터
            data = {"contents": [{"parts": [{"text": prompt}]}]}

            # 구글 공식 스펙에 맞는 URL (gemini-2.0-flash 모델 사용)
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

            print(f"Gemini API 호출 시작: {self.api_key[:10]}...")
            print(f"요청 URL: {url}")
            print(f"사용 모델: gemini-2.0-flash")

            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=60,
            )

            print(f"Gemini API 응답 상태: {response.status_code}")
            print(f"응답 내용: {response.text[:200]}...")

            if response.status_code == 200:
                result = response.json()
                return result["candidates"][0]["content"]["parts"][0]["text"]
            else:
                raise Exception(
                    f"Gemini API 오류: {response.status_code} - {response.text}"
                )

        except Exception as e:
            raise Exception(f"Gemini API 호출 실패: {e}")

    def _get_fallback_analysis(self, processed_data):
        """API 호출 실패 시 기본 분석 결과 반환"""
        stats = processed_data["stats"]

        return f"""# 🔍 기본 생산성 분석 결과

## 📊 현재 상태 요약
- **분석 기간**: 최근 {processed_data['raw_data']['period_days']}일
- **총 집중 시간**: {stats.get('total_focus_hours', 0):.1f}시간
- **평균 성공률**: {stats.get('avg_success_rate', 0):.1f}%

## 💡 기본 개선 제안
1. **뽀모도로 세션 관리**: 25분 집중 + 5분 휴식 패턴 엄격 준수
2. **시간 계획 개선**: 현실적인 시간 계획 수립 및 버퍼 시간 포함
3. **집중력 향상**: 작업 환경 최적화 및 방해 요소 제거

## ⚠️ 참고사항
AI API 연결에 실패하여 기본 분석 결과를 제공합니다.
더 상세한 분석을 원하시면 API 키 설정을 확인하고 다시 시도해주세요."""

    def _display_analysis_result(self, analysis_result):
        """분석 결과 표시"""
        self.progress_bar.stop()
        self.progress_bar.pack_forget()

        self.result_text.config(state="normal")
        self.result_text.delete("1.0", tk.END)

        # 결과 텍스트 삽입
        self.result_text.insert(tk.END, analysis_result)

        # 텍스트 서식 적용
        self._apply_text_formatting()

        self.result_text.config(state="disabled")

    def _apply_text_formatting(self):
        """텍스트 서식을 적용합니다"""
        try:
            # 제목 스타일 적용
            title_patterns = [
                r"^#+\s+(.+)$",  # 마크다운 제목
                r"^(.+?):$",  # 콜론으로 끝나는 제목
                r"^(\*\*[^*]+\*\*)$",  # 볼드 텍스트
            ]

            for pattern in title_patterns:
                start = "1.0"
                while True:
                    match = self.result_text.search(pattern, start, tk.END, regexp=True)
                    if not match:
                        break

                    line_start = match
                    line_end = self.result_text.index(f"{match}+1l")

                    # 제목 스타일 적용
                    self.result_text.tag_add("title", line_start, line_end)
                    start = line_end

                    if start == "end":
                        break

            # 태그 설정
            self.result_text.tag_config(
                "title",
                font=("Helvetica", 12, "bold"),
                foreground="#1f2937",
                spacing1=5,
                spacing3=5,
            )

            # 리스트 스타일 적용
            list_patterns = [
                r"^[\s]*[•\-\*]\s+(.+)$",  # 불릿 포인트
                r"^[\s]*\d+\.\s+(.+)$",  # 번호 매기기
            ]

            for pattern in list_patterns:
                start = "1.0"
                while True:
                    match = self.result_text.search(pattern, start, tk.END, regexp=True)
                    if not match:
                        break

                    line_start = match
                    line_end = self.result_text.index(f"{match}+1l")

                    # 리스트 스타일 적용
                    self.result_text.tag_add("list_item", line_start, line_end)
                    start = line_end

                    if start == "end":
                        break

            # 리스트 태그 설정
            self.result_text.tag_config(
                "list_item",
                font=("Helvetica", 11),
                foreground="#374151",
                spacing1=2,
                spacing3=2,
            )

            # 강조 텍스트 스타일
            emphasis_patterns = [
                r"\*\*([^*]+)\*\*",  # 볼드
                r"\*([^*]+)\*",  # 이탤릭
                r"`([^`]+)`",  # 코드
            ]

            for pattern in emphasis_patterns:
                start = "1.0"
                while True:
                    match = self.result_text.search(pattern, start, tk.END, regexp=True)
                    if not match:
                        break

                    # 강조 태그 적용
                    if "**" in pattern:
                        self.result_text.tag_add(
                            "bold", match, f"{match}+{len(match)}c"
                        )
                    elif "*" in pattern and "**" not in pattern:
                        self.result_text.tag_add(
                            "italic", match, f"{match}+{len(match)}c"
                        )
                    elif "`" in pattern:
                        self.result_text.tag_add(
                            "code", match, f"{match}+{len(match)}c"
                        )

                    start = f"{match}+1c"

                    if start == "end":
                        break

            # 강조 태그 설정
            self.result_text.tag_config("bold", font=("Helvetica", 11, "bold"))
            self.result_text.tag_config("italic", font=("Helvetica", 11, "italic"))
            self.result_text.tag_config(
                "code",
                font=("Courier", 10),
                background="#f3f4f6",
                relief="solid",
                borderwidth=1,
            )

        except Exception as e:
            print(f"텍스트 서식 적용 실패: {e}")

    def _handle_analysis_error(self, error):
        """분석 오류 처리"""
        self.progress_bar.stop()
        self.progress_bar.pack_forget()

        error_message = f"❌ 분석 중 오류가 발생했습니다:\n\n{str(error)}\n\n"
        error_message += "다음 사항을 확인해주세요:\n"
        error_message += "• 인터넷 연결 상태\n"
        error_message += "• API 키 유효성\n"
        error_message += "• 데이터베이스 접근 권한"

        self.progress_label.config(text="오류 발생")
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, error_message)
        self.result_text.config(state="disabled")

    def _refresh_ai_analysis(self):
        """AI 분석 새로고침"""
        self.progress_bar.pack(fill=tk.X, pady=(5, 0))
        self.progress_bar.start()
        self.progress_label.config(text="🔄 분석 새로고침 중...")
        self.root.after(500, lambda: self._perform_advanced_ai_diagnosis())

    def _save_ai_analysis(self):
        """AI 분석 결과 저장"""
        try:
            # 현재 날짜와 시간으로 파일명 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"AI_생산성진단_{timestamp}.txt"

            # 결과 텍스트 추출
            result_content = self.result_text.get("1.0", tk.END)

            # 파일 저장
            with open(filename, "w", encoding="utf-8") as f:
                f.write(result_content)

            messagebox.showinfo(
                "저장 완료",
                f"분석 결과가 '{filename}' 파일로 저장되었습니다.",
                parent=self.diag_win,
            )

        except Exception as e:
            messagebox.showerror(
                "저장 실패",
                f"파일 저장 중 오류가 발생했습니다: {e}",
                parent=self.diag_win,
            )

    def _init_pygame(self):
        """pygame을 초기화하고 사운드 파일을 로드합니다."""
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init()
                # 상대 경로로 사운드 파일 로드
                sound_path = os.path.join(os.path.dirname(__file__), "TeamRadioF1.wav")
                if os.path.exists(sound_path):
                    self.notification_sound = pygame.mixer.Sound(sound_path)
                    self.sound_loaded = True
                else:
                    print(f"사운드 파일을 찾을 수 없습니다: {sound_path}")
                    self.sound_loaded = False
            except Exception as e:
                print(f"pygame 초기화 실패: {e}")
                self.sound_loaded = False
        else:
            self.sound_loaded = False

    def _play_notification_sound(self):
        """선택된 소리 타입에 따라 알림음을 재생합니다."""
        if self.sound_type.get() == "custom" and self.sound_loaded:
            # 커스텀 소리 (TeamRadioF1.wav)
            try:
                volume = int(self.sound_volume.get()) / 100.0
                self.notification_sound.set_volume(volume)
                self.notification_sound.play()
            except Exception as e:
                print(f"사운드 재생 실패: {e}")
                # pygame이 없거나 오류가 발생하면 기본 벨 소리 사용
                self.root.bell()
        else:
            # 기본 알림음
            self.root.bell()

    def _preview_sound(self):
        """볼륨 조정 시 미리듣기를 제공합니다."""
        if self.sound_type.get() == "custom" and self.sound_loaded:
            # 커스텀 소리 미리듣기
            try:
                volume = int(self.sound_volume.get()) / 100.0
                self.notification_sound.set_volume(volume)
                self.notification_sound.play()
            except Exception as e:
                print(f"미리듣기 재생 실패: {e}")
                # pygame이 없거나 오류가 발생하면 기본 벨 소리 사용
                self.root.bell()
        else:
            # 기본 알림음 미리듣기
            self.root.bell()

    def _on_window_resize(self, event):
        """창 크기 변경 시 UI를 반응형으로 재조정합니다."""
        if event.widget == self.root:
            current_time = time_module.time()
            window_width = event.width
            window_height = event.height

            # 적응형 디바운싱: 리사이징 패턴에 따라 지연 시간 조절
            if current_time - self._last_resize_time < 0.05:  # 50ms 이내 연속 리사이징
                self._resize_count += 1
                # 연속 리사이징이 많을수록 더 빠른 응답
                delay = max(50, 150 - (self._resize_count * 10))  # 50ms ~ 150ms
            else:
                # 리사이징이 멈춘 경우 빠른 응답
                self._resize_count = 0
                delay = 50  # 50ms로 빠른 응답

            self._last_resize_time = current_time

            # 디바운싱: 이전 타이머가 있으면 취소하고 새로 설정
            if self._resize_timer:
                self.root.after_cancel(self._resize_timer)

            # 창 크기에 따른 UI 모드 결정 및 재조정 실행
            self._resize_timer = self.root.after(
                delay, lambda: self._adjust_ui_for_size(window_width, window_height)
            )

    def _on_window_minimize(self, event):
        """창이 최소화될 때 호출됩니다."""
        if event.widget == self.root:
            self._show_minimal_ui()

    def _on_window_restore(self, event):
        """창이 복원될 때 호출됩니다."""
        if event.widget == self.root:
            self._show_full_ui()

    def _adjust_ui_for_size(self, width, height):
        """창 크기에 따라 UI를 적응형으로 조정합니다."""
        # 창 크기 임계값 설정
        min_width_threshold = 600
        min_height_threshold = 400

        if width < min_width_threshold or height < min_height_threshold:
            # 작은 창 모드: UI 요소들을 압축하고 스크롤 가능하게 만듦
            self._show_compact_ui()
        else:
            # 일반 모드: 모든 UI 요소를 표시
            self._show_full_ui()

        # 캘린더 재그리기
        self._redraw_calendar()

    def _show_compact_ui(self):
        """압축된 UI 모드: 작은 창에 최적화"""
        if hasattr(self, "_is_compact_mode") and self._is_compact_mode:
            return

        self._is_compact_mode = True

        # 통계 프레임을 압축
        if hasattr(self, "stats_frame"):
            self.stats_frame.configure(padding="5")

        # 버튼들을 세로로 배치
        if hasattr(self, "button_frame"):
            for child in self.button_frame.winfo_children():
                child.pack_forget()
                child.pack(side=tk.TOP, fill=tk.X, pady=2)

        # 작업 관리 프레임을 압축
        if hasattr(self, "task_manager_frame"):
            self.task_manager_frame.configure(padding="5")

        # 창 제목 변경
        self.root.title("Pomodoro Timer (Compact)")

    def _redraw_calendar(self):
        """캘린더를 다시 그립니다."""
        # 캔버스 크기가 유효한지 확인
        if self.calendar_canvas.winfo_width() > 1:
            self._draw_calendar_background()
            self._draw_tasks_on_calendar()
            self._update_current_time_indicator()

    def _draw_calendar_background(self):
        self.calendar_canvas.delete("background")
        width = max(self.calendar_canvas.winfo_width(), 300)  # 최소 너비 보장
        height = self.hour_height * (self.cal_end_hour - self.cal_start_hour + 1)
        self.calendar_canvas.configure(scrollregion=(0, 0, width, height))
        for hour in range(self.cal_start_hour, self.cal_end_hour + 1):
            y = (hour - self.cal_start_hour) * self.hour_height
            self.calendar_canvas.create_line(
                50, y, width, y, fill="#e0e0e0", tags="background"
            )
            self.calendar_canvas.create_text(
                25,
                y,
                text=f"{hour:02d}:00",
                anchor=tk.W,
                tags="background",
                fill="black",
            )

    def _draw_tasks_on_calendar(self):
        self.calendar_canvas.delete("task")
        layouts = self._calculate_task_layouts()
        for (
            task_id,
            task,
        ) in self.displayed_tasks_data.items():  # Use displayed_tasks_data
            layout = layouts.get(task_id)
            if not layout:
                continue
            start_y = self._time_to_y(task["start_time"])
            end_y = self._time_to_y(task["end_time"])
            total_width = max(
                self.calendar_canvas.winfo_width() - 70, 200
            )  # 최소 너비 보장
            col_width = total_width / layout["total_cols"]
            x0 = 60 + layout["col"] * col_width
            x1 = x0 + col_width - 2
            color_map = {
                "pending": "#a1c4fd",
                "on-time": "#a6e3a1",
                "delayed": "#f9e2af",
                "failed": "#f38ba8",
            }
            color = color_map.get(task["status"], "#dcdcdc")
            self.calendar_canvas.create_rectangle(
                x0, start_y, x1, end_y, fill=color, outline="#6699ff", tags="task"
            )
            # 텍스트 너비 제한으로 오버플로우 방지
            text_width = max(int(col_width - 10), 20)
            self.calendar_canvas.create_text(
                x0 + 5,
                start_y + 5,
                text=task["name"],
                anchor=tk.NW,
                tags="task",
                width=text_width,
            )

    def _calculate_task_layouts(self):
        layouts = {}
        sorted_tasks = sorted(
            self.displayed_tasks_data.items(), key=lambda item: item[1]["start_time"]
        )  # Use displayed_tasks_data
        for i in range(len(sorted_tasks)):
            task_id, task = sorted_tasks[i]
            collisions = []
            for j in range(i):
                prev_task_id, prev_task = sorted_tasks[j]
                if (
                    task["start_time"] < prev_task["end_time"]
                    and task["end_time"] > prev_task["start_time"]
                ):
                    collisions.append(layouts[prev_task_id])
            col = 0
            while any(c["col"] == col for c in collisions):
                col += 1
            layouts[task_id] = {"col": col, "total_cols": 1}
        for task_id, layout in layouts.items():
            task = self.displayed_tasks_data[task_id]  # Use displayed_tasks_data
            overlapping_cols = {layout["col"]}
            for other_id, other_layout in layouts.items():
                if task_id == other_id:
                    continue
                other_task = self.displayed_tasks_data[
                    other_id
                ]  # Use displayed_tasks_data
                if (
                    task["start_time"] < other_task["end_time"]
                    and task["end_time"] > other_task["start_time"]
                ):
                    overlapping_cols.add(other_layout["col"])
            layout["total_cols"] = max(layout["total_cols"], len(overlapping_cols))
        return layouts

    def _time_to_y(self, t):
        return (t.hour - self.cal_start_hour + t.minute / 60) * self.hour_height

    def _update_current_time_indicator(self):
        self.calendar_canvas.delete("time_indicator")
        if self.selected_date == datetime.now().date():
            now = datetime.now().time()
            if self.cal_start_hour <= now.hour < self.cal_end_hour:
                y = self._time_to_y(now)
                width = max(self.calendar_canvas.winfo_width(), 300)  # 최소 너비 보장
                self.calendar_canvas.create_line(
                    50, y, width, y, fill="red", width=2, tags="time_indicator"
                )

    def _add_task(self):
        name = self.task_name_entry.get().strip()
        if not name:
            return messagebox.showwarning("Input Error", "Task name is required.")
        try:
            start_t = time(int(self.start_hour.get()), int(self.start_minute.get()))
            end_t = time(int(self.end_hour.get()), int(self.end_minute.get()))
            if start_t >= end_t:
                return messagebox.showwarning(
                    "Time Error", "End time must be after start time."
                )
        except ValueError:
            return messagebox.showwarning(
                "Input Error", "Hours and minutes must be numbers."
            )

        # Add task to today_tasks
        task_id = self.next_task_id
        self.next_task_id += 1
        self.today_tasks[task_id] = {  # Add to today_tasks
            "name": name,
            "start_time": start_t,
            "end_time": end_t,
            "is_complete": tk.BooleanVar(value=False),
            "status": "pending",
            "delay_info": None,
            "widgets": {},
        }

        # If viewing today, update UI directly
        if self.selected_date == datetime.now().date():
            self._create_task_list_item(task_id)  # Create UI for the new task
            self._draw_tasks_on_calendar()
            self._update_stats_display()
            # 스크롤 영역 업데이트
            self._update_task_scroll_region()
        self.task_name_entry.delete(0, tk.END)
        self._save_data()

    def _create_task_list_item(self, task_id):
        # This function now takes task_id and gets task data from displayed_tasks_data
        task = self.displayed_tasks_data.get(
            task_id
        )  # Get task from displayed_tasks_data
        if not task:
                    return

        task_frame = ttk.Frame(self.task_list_frame)
        task_frame.pack(fill=tk.X, pady=2)
        cb = ttk.Checkbutton(
            task_frame,
            var=task["is_complete"],
            command=lambda i=task_id: self._on_task_complete_toggle(i),
        )
        cb.pack(side=tk.LEFT)
        label = ttk.Label(task_frame, text="")
        label.pack(side=tk.LEFT, expand=True, fill=tk.X)
        delete_btn = ttk.Button(
            task_frame, text="삭제", command=lambda i=task_id: self._delete_task(i)
        )
        delete_btn.pack(side=tk.RIGHT)
        task["widgets"] = {
            "frame": task_frame,
            "label": label,
            "checkbox": cb,
            "delete_btn": delete_btn,
        }
        is_today = self.selected_date == datetime.now().date()
        cb.config(state=tk.NORMAL if is_today else tk.DISABLED)
        delete_btn.config(state=tk.NORMAL if is_today else tk.DISABLED)
        self._update_task_list_item_display(task_id)

    def _on_task_complete_toggle(self, task_id):
        # This function should modify today_tasks if viewing today
        if self.selected_date == datetime.now().date():
            task = self.today_tasks[task_id]  # Modify today_tasks
            is_now_complete = task["is_complete"].get()
            if is_now_complete:
                now_dt = datetime.now()
                end_dt = datetime.combine(self.selected_date, task["end_time"])
                start_dt = datetime.combine(self.selected_date, task["start_time"])
                scheduled_duration = end_dt - start_dt
                # NEW CHECK: Handle zero or negative scheduled_duration
                if scheduled_duration.total_seconds() <= 0:
                    task["status"] = "failed"  # Mark as failed if duration is invalid
                    task["delay_info"] = "Invalid duration"
                elif now_dt <= end_dt:
                    task["status"] = "on-time"
                else:
                    delay = now_dt - end_dt
                    delay_percentage = (
                        delay.total_seconds() / scheduled_duration.total_seconds()
                    ) * 100
                    if delay_percentage <= 25:
                        task["status"] = "delayed"
                        task["delay_info"] = f"{delay_percentage:.1f}% 지연"
                    else:
                        task["status"] = "failed"
            else:
                task["status"] = "pending"
                task["delay_info"] = None
            self._update_task_list_item_display(task_id)
            self._draw_tasks_on_calendar()
            self._update_stats_display()
            self._save_data()
        else:
            messagebox.showwarning("경고", "과거 날짜의 작업은 수정할 수 없습니다.")

    def _delete_task(self, task_id):
        # This function should modify today_tasks if viewing today
        if self.selected_date == datetime.now().date():
            task = self.today_tasks.get(task_id)  # Get from today_tasks
            if task and messagebox.askyesno("Delete Task", f"Delete '{task['name']}'?"):
                task["widgets"]["frame"].destroy()
                del self.today_tasks[task_id]  # Delete from today_tasks
                self._draw_tasks_on_calendar()
                self._update_stats_display()
                self._save_data()
                # 스크롤 영역 업데이트
                self._update_task_scroll_region()
        else:
            messagebox.showwarning("경고", "과거 날짜의 작업은 삭제할 수 없습니다.")

    def _update_task_list_item_display(self, task_id):
        # This function now gets task data from displayed_tasks_data
        task = self.displayed_tasks_data.get(
            task_id
        )  # Get task from displayed_tasks_data
        if not task:
                    return

        now = datetime.now()
        remaining_text = ""
        is_today = self.selected_date == datetime.now().date()

        if is_today and not task["is_complete"].get():
            task_start = datetime.combine(self.selected_date, task["start_time"])
            task_end = datetime.combine(self.selected_date, task["end_time"])

            if task_start <= now <= task_end:
                remaining_delta = task_end - now
                if remaining_delta.total_seconds() > 0:
                    mins, secs = divmod(int(remaining_delta.total_seconds()), 60)
                    hours, mins = divmod(mins, 60)
                    remaining_text = f" (남음: {hours:02d}:{mins:02d}:{secs:02d})"

        time_str = f"{task['start_time'].strftime('%H:%M')}-{task['end_time'].strftime('%H:%M')}"
        base_text = f"{task['name']} [{time_str}]"
        delay_text = f" - {task['delay_info']}" if task["delay_info"] else ""
        full_text = base_text + remaining_text + delay_text

        task["widgets"]["label"].config(text=full_text)
        style_map = {
            "pending": "Pending.TLabel",
            "on-time": "OnTime.TLabel",
            "delayed": "Delayed.TLabel",
            "failed": "Failed.TLabel",
        }
        task["widgets"]["label"].config(
            style=style_map.get(task["status"], "Pending.TLabel")
        )

    def _update_clocks(self):
        if self.pomodoro_state in ["work", "break"]:
            self.seconds_left -= 1
            if self.pomodoro_state == "work":
                self.today_stats["total_focus_seconds"] += 1
            if self.seconds_left < 0:
                self._handle_session_end()
        elif self.pomodoro_state == "paused":
            self.pause_seconds_left -= 1
            if self.pause_seconds_left < 0:
                if self.paused_from_state == "work":
                    self.today_stats["failure"] += 1
                self._reset_pomodoro()

        # 자정을 넘어가는 날짜 변경 감지 및 처리
        self._check_and_handle_day_change()

        if self.selected_date == datetime.now().date():
            self._check_and_update_task_statuses()
            for task_id in list(
                self.displayed_tasks_data.keys()
            ):  # Use displayed_tasks_data
                if task_id in self.displayed_tasks_data:  # Use displayed_tasks_data
                    self._update_task_list_item_display(task_id)
            self._update_stats_display()

        self._update_timer_display()
        self._update_current_time_indicator()
        
        # 다음 타이머 호출 예약 (기존 타이머 ID 재사용)
        if self.pomodoro_state != "stopped":
            self._timer_id = self.root.after(1000, self._update_clocks)
        else:
            self._timer_id = None

    def _adjust_ui_for_window_size(self):
        """창 크기에 따라 UI 모드를 조정합니다."""
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()

        # 최소 크기 임계값 설정 (타이머만 표시할 크기)
        min_width_threshold = 400
        min_height_threshold = 300

        if window_width < min_width_threshold or window_height < min_height_threshold:
            # 최소 크기 모드: 타이머만 표시
            self._show_minimal_ui()
        else:
            # 일반 모드: 모든 UI 요소 표시
            self._show_full_ui()

    def _show_minimal_ui(self):
        """최소 UI 모드: 포모도로 타이머만 표시"""
        # UI 상태를 추적하는 변수 설정
        self._is_minimal_mode = True

        # 타이머 프레임을 중앙에 배치
        self.timer_frame.pack(fill=tk.BOTH, expand=True, pady=20)

        # 창 제목을 간단하게 변경
        self.root.title("Pomodoro Timer")

    def _show_full_ui(self):
        """전체 UI 모드: 모든 요소 표시"""
        # UI 상태를 추적하는 변수 설정
        self._is_minimal_mode = False
        self._is_compact_mode = False

        # 타이머 프레임을 원래 위치로 복원
        self.timer_frame.pack(fill=tk.X, pady=5)

        # 통계 프레임을 원래 크기로 복원
        if hasattr(self, "stats_frame"):
            self.stats_frame.configure(padding="10")

        # 버튼들을 원래 가로 배치로 복원
        if hasattr(self, "button_frame"):
            for child in self.button_frame.winfo_children():
                child.pack_forget()
                child.pack(side=tk.LEFT, padx=(0, 10))
            # 마지막 버튼의 padx 제거
            if self.button_frame.winfo_children():
                self.button_frame.winfo_children()[-1].pack_configure(padx=0)

        # 작업 관리 프레임을 원래 크기로 복원
        if hasattr(self, "task_manager_frame"):
            self.task_manager_frame.configure(padding="10")

        # 창 제목 복원
        self.root.title("Juns Enterprise - Pomodoro Timer & Task Manager v2.1.0")

    def _update_task_scroll_region(self):
        """작업 목록의 스크롤 영역을 업데이트합니다."""
        self.task_canvas.update_idletasks()
        self.task_canvas.configure(scrollregion=self.task_canvas.bbox("all"))

    def _start_scroll_drag(self, event):
        """마우스 드래그 스크롤 시작"""
        self.task_canvas.scan_mark(0, event.y)

    def _on_scroll_drag(self, event):
        """마우스 드래그 스크롤 중"""
        self.task_canvas.scan_dragto(0, event.y, gain=1)

    def _stop_scroll_drag(self, event):
        """마우스 드래그 스크롤 종료"""
        pass  # 필요한 경우 추가 로직 구현

    def _check_and_handle_day_change(self):
        """자정을 넘어가는 날짜 변경을 감지하고 처리합니다."""
        # 자정 근처에서만 체크 (23:59 ~ 00:01)
        now = datetime.now()
        current_hour = now.hour
        current_minute = now.minute
        
        # 자정 전후 1분 이내에서만 체크
        if not ((current_hour == 23 and current_minute >= 59) or 
                (current_hour == 0 and current_minute <= 1)):
            return
            
        current_date = now.date()

        # 자정을 넘어간 경우에만 처리
        if self._is_midnight_crossed(current_date):
            self._handle_midnight_crossing(current_date)
        
        # 자정이 지나면 사용자 수동 변경 플래그 자동 리셋
        if current_hour == 0 and current_minute == 1:
            if self.user_manually_changed_date:
                        self.user_manually_changed_date = False

    def _is_midnight_crossed(self, current_date):
        """자정을 넘어갔는지 확인합니다."""
        # 사용자가 수동으로 날짜를 변경한 경우는 자동 날짜 변경을 하지 않음
        if self.user_manually_changed_date:
            return False
        
        # 현재 선택된 날짜가 어제이고, 실제 현재 날짜가 오늘인 경우만 자정 넘어감으로 간주
        yesterday = current_date - timedelta(days=1)
        if self.selected_date == yesterday and current_date > yesterday:
            print(f"자정을 넘어갔습니다: {self.selected_date} → {current_date}")
            return True
        return False

    def _handle_midnight_crossing(self, current_date):
        """자정을 넘어간 경우의 처리를 담당합니다."""
        # 이전 날짜의 미완료 작업 확인
        previous_date = self.selected_date
        incomplete_tasks = self._get_incomplete_tasks_from_date(previous_date)

        # 데이터 저장 및 오늘 날짜로 변경
        self._perform_day_change(current_date)

        # 미완료 작업이 있는 경우 팝업 표시
        if incomplete_tasks:
            self._show_incomplete_tasks_popup(previous_date, incomplete_tasks)

        # 자동 날짜 변경 후 플래그 리셋
        self.user_manually_changed_date = False
        
        # 작업 이전 관련 플래그 리셋 (새로운 날짜가 시작되므로)
        self.transfer_suggested_today = False
        self.last_transfer_suggested_date = None

    def _perform_day_change(self, new_date):
        """날짜 변경을 수행합니다."""
        # 현재 데이터 저장
        self._save_data()

        # 새 날짜로 설정
        self.selected_date = new_date

        # 통계 및 작업 데이터 초기화
        self._reset_daily_data()

        # UI 업데이트
        self._update_date_view()
        
        # 타이머가 계속 작동하도록 보장
        if self.pomodoro_state != "stopped":
            self._start_timer()

    def _reset_daily_data(self):
        """일일 데이터를 초기화합니다."""
        self.today_stats = collections.defaultdict(int)
        self.today_tasks = collections.OrderedDict()

        # 새 날짜의 데이터 로드
        self._load_today_stats()
        self._load_today_tasks()

    def _get_incomplete_tasks_from_date(self, date):
        """지정된 날짜의 미완료 작업 목록을 반환합니다."""
        incomplete_tasks = []
        try:
            date_str = date.strftime("%Y-%m-%d")
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # pending 상태인 작업만 미완료로 간주
            cursor.execute(
                "SELECT id, name, start_time, end_time, status FROM tasks WHERE task_date = ? AND status = 'pending'",
                (date_str,),
            )

            tasks_data = cursor.fetchall()
            for row in tasks_data:
                task_id, name, start_t_str, end_t_str, status = row
                incomplete_tasks.append(
                    {
                        "id": task_id,
                        "name": name,
                        "start_time": datetime.strptime(start_t_str, "%H:%M:%S").time(),
                        "end_time": datetime.strptime(end_t_str, "%H:%M:%S").time(),
                        "status": status,
                    }
                )

            conn.close()
        except Exception as e:
            print(f"미완료 작업 조회 오류: {e}")

        return incomplete_tasks

    def _show_incomplete_tasks_popup(self, previous_date, incomplete_tasks):
        """미완료 작업을 오늘로 이전할지 묻는 팝업을 표시합니다."""
        popup = tk.Toplevel(self.root)
        popup.title("미완료 작업 이전")
        popup.geometry("400x300")
        popup.transient(self.root)
        popup.grab_set()

        # 팝업 내용
        content_frame = ttk.Frame(popup, padding="20")
        content_frame.pack(fill=tk.BOTH, expand=True)

        # 제목
        title_label = ttk.Label(
            content_frame,
            text=f"📅 {previous_date.strftime('%Y-%m-%d')}의 미완료 작업",
            font=("Arial", 12, "bold"),
        )
        title_label.pack(pady=(0, 15))

        # 설명
        desc_label = ttk.Label(
            content_frame,
            text=f"총 {len(incomplete_tasks)}개의 미완료 작업이 있습니다.\n오늘로 이전하시겠습니까?",
            font=("Arial", 10),
        )
        desc_label.pack(pady=(0, 20))

        # 작업 목록 (스크롤 가능)
        list_frame = ttk.Frame(content_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # 스크롤바가 있는 텍스트 위젯
        text_widget = tk.Text(list_frame, height=8, width=50, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(
            list_frame, orient="vertical", command=text_widget.yview
        )
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 작업 목록 표시
        for i, task in enumerate(incomplete_tasks, 1):
            status_emoji = "⏰" if task["status"] == "pending" else "⚠️"
            task_text = f"{i}. {status_emoji} {task['name']} ({task['start_time'].strftime('%H:%M')} - {task['end_time'].strftime('%H:%M')})\n"
            text_widget.insert(tk.END, task_text)

        text_widget.config(state=tk.DISABLED)  # 읽기 전용

        # 버튼 프레임
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        def transfer_tasks():
            """작업을 오늘로 이전합니다."""
            try:
                self._transfer_incomplete_tasks_to_today(
                    previous_date, incomplete_tasks
                )
                messagebox.showinfo("완료", "미완료 작업이 오늘로 이전되었습니다.")
                popup.destroy()
                # UI 새로고침
                self._update_date_view()
            except Exception as e:
                messagebox.showerror("오류", f"작업 이전 중 오류가 발생했습니다: {e}")

        def skip_transfer():
            """작업 이전을 건너뜁니다."""
            popup.destroy()

        # 버튼들
        ttk.Button(
            button_frame,
            text="✅ 이전하기",
            command=transfer_tasks,
            style="Accent.TButton",
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(button_frame, text="❌ 건너뛰기", command=skip_transfer).pack(
            side=tk.LEFT
        )

        # 창 중앙 정렬
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (popup.winfo_width() // 2)
        y = (popup.winfo_screenheight() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")

        # 팝업을 최상위로 표시
        popup.lift()
        popup.focus_force()

    def _transfer_incomplete_tasks_to_today(self, previous_date, incomplete_tasks):
        """미완료 작업을 오늘 날짜로 이전합니다."""
        try:
            today_str = datetime.now().date().strftime("%Y-%m-%d")
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 이미 이전된 작업인지 확인
            transferred_count = 0
            for task in incomplete_tasks:
                # 동일한 이름과 시간의 작업이 오늘 이미 존재하는지 확인
                cursor.execute(
                    "SELECT COUNT(*) FROM tasks WHERE task_date = ? AND name = ? AND start_time = ? AND end_time = ?",
                    (today_str, task["name"], task["start_time"].strftime("%H:%M:%S"), task["end_time"].strftime("%H:%M:%S"))
                )
                
                if cursor.fetchone()[0] == 0:  # 중복되지 않는 경우에만 이전
                    cursor.execute(
                        "INSERT INTO tasks (id, task_date, name, start_time, end_time, status) VALUES (?, ?, ?, ?, ?, ?)",
                        (
                            self.next_task_id,
                            today_str,
                            task["name"],
                            task["start_time"].strftime("%H:%M:%S"),
                            task["end_time"].strftime("%H:%M:%S"),
                            "pending",  # 상태를 pending으로 초기화
                        ),
                    )
                    self.next_task_id += 1
                    transferred_count += 1

            conn.commit()
            conn.close()
            
            if transferred_count > 0:
                # 오늘 작업 목록 새로고침
                self._load_today_tasks()

        except Exception as e:
            print(f"작업 이전 오류: {e}")
            raise

    def _check_and_update_task_statuses(self):
        now_dt = datetime.now()
        for task_id, task in list(
            self.displayed_tasks_data.items()
        ):  # Use displayed_tasks_data
            if task["is_complete"].get():
                continue
            end_dt = datetime.combine(self.selected_date, task["end_time"])
            if now_dt > end_dt:
                start_dt = datetime.combine(self.selected_date, task["start_time"])
                scheduled_duration = end_dt - start_dt
                if scheduled_duration.total_seconds() <= 0:
                    continue
                delay = now_dt - end_dt
                delay_percentage = (
                    delay.total_seconds() / scheduled_duration.total_seconds()
                ) * 100
                new_status = task["status"]  # Keep current status as base
                if delay_percentage > 25:
                    new_status = "failed"
                elif (
                    task["status"] != "failed"
                ):  # Only set to delayed if not already failed
                    new_status = "delayed"

                # Update status if it has changed
                if task["status"] != new_status:
                    task["status"] = new_status
                    self._draw_tasks_on_calendar()  # Update calendar on status change

                # Update delay_info if status is delayed
                if new_status == "delayed":
                    task["delay_info"] = f"{delay_percentage:.1f}% 지연"
                else:  # Clear delay_info if not delayed
                    task["delay_info"] = None

                # Always update display for the task if its status or delay_info might have changed
                self._update_task_list_item_display(task_id)

    def _toggle_pomodoro_state(self):
        if self.pomodoro_state == "work":  # Only work can be paused
            self.paused_from_state = self.pomodoro_state
            self.pomodoro_state = "paused"
            self.pause_seconds_left = self.pause_duration
        elif self.pomodoro_state == "paused":
            self.pomodoro_state = self.paused_from_state
            self.paused_from_state = None
        elif self.pomodoro_state == "stopped":  # This is for initial start
            # When starting from 'stopped', it's always 'work'
            self.pomodoro_state = "work"
            self.seconds_left = self.work_duration
        # If pomodoro_state is 'break', this function should do nothing (no pause)
        # The button will be handled by _update_pomodoro_button
        self._update_pomodoro_button()
        self._update_timer_display()
        
        # 타이머가 계속 작동하도록 보장
        if not self._timer_id:
            self._start_timer()

    def _reset_pomodoro(self):
        # 알람이 울리고 있는 상태에서 리셋 시 실패 처리
        alarm_was_on = self.alarm_on
        if self.alarm_on:
            # 사용자에게 명확한 메시지 제공
            if self.pomodoro_state == "work":
                messagebox.showinfo(
                    "세션 실패",
                    "휴식 알람을 끄지 않고 리셋한 세션이 실패로 처리되었습니다.\n\n"
                    "더 나은 집중을 위해 휴식 시간을 제대로 활용해주세요.",
                )
            self.today_stats["failure"] += 1
            # 알람만 종료 (중복 실패 처리 방지)
            self.alarm_on = False
            if self._alarm_after_id:
                self.root.after_cancel(self._alarm_after_id)
                self._alarm_after_id = None

        # 기존 리셋 로직 (알람이 켜진 상태에서 리셋한 경우는 제외)
        if not alarm_was_on and (
            self.pomodoro_state == "work"
            or (self.pomodoro_state == "paused" and self.paused_from_state == "work")
        ):
            if self.seconds_left < self.work_duration:
                self.today_stats["failure"] += 1

        # 휴식 상태에서 리셋할 때 동기부여 메시지 표시
        if (
            self.pomodoro_state == "break"
            and not alarm_was_on
            and self.consecutive_completions > 0
        ):
            self._show_motivation_message()

        # 모든 리셋 상황에서 연속 완료 카운트 리셋 (사용자 의도적 중단)
        self.consecutive_completions = 0

        # 연속 달성 횟수도 리셋 (사용자가 의도적으로 중단한 경우)
        self.current_streak = 0
        self._save_streak_data()

        self.pomodoro_state = "stopped"
        self.paused_from_state = None
        self.seconds_left = self.work_duration
        self._update_pomodoro_button()
        self._update_timer_display()
        if self.selected_date == datetime.now().date():
            self._update_stats_display()
        self._save_data()
        
        # 타이머 재시작
        self._start_timer()

    def _handle_session_end(self):
        self._play_notification_sound()
        if self.pomodoro_state == "work":
            self.today_stats["success"] += 1
            self.today_stats["completed_pomodoros"] += 1
            self.consecutive_completions += 1  # 연속 완료 카운트 증가

            # 연속 달성 업데이트
            self._update_streak()

            self.pomodoro_state = "break"  # Transition to break
            self.seconds_left = self.break_duration
            self._start_alarm()  # Start alarm when transitioning to break
        elif self.pomodoro_state == "break":
            # 휴식시간 종료 시: 정상적으로 작업 상태로 전환
            self.pomodoro_state = "work"  # Transition to work
            self.seconds_left = self.work_duration

        self._update_pomodoro_button()
        self._update_timer_display()  # Update timer display immediately
        if self.selected_date == datetime.now().date():
            self._update_stats_display()
        self._save_data()
        
        # 타이머가 계속 작동하도록 보장
        if not self._timer_id:
            self._start_timer()

    def _update_timer_display(self):
        if self.pomodoro_state == "paused":
            mins, secs = divmod(self.pause_seconds_left, 60)
            self.time_label.config(
                text=f"{int(mins):02d}:{int(secs):02d}", style="Paused.Timer.TLabel"
            )
        else:
            mins, secs = divmod(self.seconds_left, 60)
            self.time_label.config(
                text=f"{int(mins):02d}:{int(secs):02d}", style="Timer.TLabel"
            )

    def _update_pomodoro_button(self):
        if self.pomodoro_state == "stopped":
            self.start_pause_button.config(
                text="집중 시작", command=self._toggle_pomodoro_state, state=tk.NORMAL
            )
            self.seconds_left = self.work_duration  # Ensure work duration is set
            self._update_timer_display()
        elif self.pomodoro_state == "work":
            if self.alarm_on:  # 작업 상태에서도 알람이 울리고 있는 경우
                self.start_pause_button.config(
                    text="알람 끄기", command=self.alarm_stop_, state=tk.NORMAL
                )
            else:  # 알람이 꺼진 경우
                self.start_pause_button.config(
                    text="일시 정지",
                    command=self._toggle_pomodoro_state,
                    state=tk.NORMAL,
                )
        elif self.pomodoro_state == "break":
            if self.alarm_on:  # Alarm is still ringing
                self.start_pause_button.config(
                    text="알람 끄기", command=self.alarm_stop_, state=tk.NORMAL
                )
            else:  # Alarm has been turned off, or never started (e.g., if break_duration is 0)
                self.start_pause_button.config(
                    text="휴식 시간",
                    command=None,
                    state=tk.DISABLED,  # Make it unclickable
                )
        elif self.pomodoro_state == "paused":
            self.start_pause_button.config(
                text="계속하기", command=self._toggle_pomodoro_state, state=tk.NORMAL
            )

    def _update_stats_display(self):
        s = self.displayed_stats
        total_sessions = s.get("success", 0) + s.get("failure", 0)
        success_rate = (
            (s.get("success", 0) / total_sessions * 100) if total_sessions > 0 else 0
        )
        total_focus_seconds = s.get("total_focus_seconds", 0)
        h, rem = divmod(total_focus_seconds, 3600)
        m, s_rem = divmod(rem, 60)
        total_focus_time_str = f"{int(h):02d}:{int(m):02d}:{int(s_rem):02d}"

        total_tasks = len(self.displayed_tasks_data)  # Use displayed_tasks_data
        weighted_score = 0
        for task in self.displayed_tasks_data.values():  # Use displayed_tasks_data
            if task["status"] == "on-time":
                weighted_score += 1
            elif task["status"] == "delayed":
                weighted_score += 0.5
        task_completion_rate = (
            (weighted_score / total_tasks * 100) if total_tasks > 0 else 0
        )

        self.stats_labels["completed"].config(
            text=f"완료한 뽀모도로: {s.get('completed_pomodoros', 0)}회"
        )
        self.stats_labels["success_rate"].config(
            text=f"뽀모도로 성공률: {success_rate:.1f}% ({s.get('success',0)}/{total_sessions})"
        )
        self.stats_labels["focus_time"].config(
            text=f"총 집중 시간: {total_focus_time_str}"
        )
        self.stats_labels["task_completion"].config(
            text=f"작업 달성도: {task_completion_rate:.1f}%"
        )

        # 연속 달성 정보 표시
        if self.longest_streak > 0:
            streak_text = (
                f"🔥연속 달성: {self.current_streak}회 (최장: {self.longest_streak}회)"
            )
        else:
            streak_text = f"🔥 연속 달성: {self.current_streak}회"
        self.stats_labels["streak"].config(text=streak_text)

    def _start_timer(self):
        """타이머를 시작합니다."""
        if not self._timer_id:
            self._timer_id = self.root.after(1000, self._update_clocks)

    def _stop_timer(self):
        """타이머를 중지합니다."""
        if self._timer_id:
            self.root.after_cancel(self._timer_id)
            self._timer_id = None

    def _quit_app(self):
        self._save_data()
        if messagebox.askokcancel(
            "Juns Enterprise - 종료",
            "정말로 Juns Enterprise Pomodoro Suite를 종료하시겠습니까?\n\n"
            "진행 중인 작업과 통계가 자동으로 저장됩니다.",
        ):
            self._stop_timer()
            print(
                """
╔══════════════════════════════════════════════════════════════════════════════╗
║                           SESSION TERMINATED                                 ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Thank you for using Juns Enterprise Pomodoro Suite!                       ║
║                                                                              ║
║  Session Summary:                                                            ║
║  • Total Focus Time: {0} minutes                    ║
║  • Completed Pomodoros: {1} sessions                       ║
║  • Success Rate: {2:.1f}% ║
║                                                                              ║
║  For support and licensing inquiries:                                        ║
║  • Email: enterprise@juns-corp.com                                          ║
║  • Website: https://www.juns-corp.com                                       ║
║                                                                              ║
║  Copyright © 2025 Juns Corporation. All Rights Reserved.                    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""".format(
                    self.today_stats.get("total_focus_seconds", 0) // 60,
                    self.today_stats.get("completed_pomodoros", 0),
                    (
                        self.today_stats.get("success", 0)
                        / max(
                            1,
                            self.today_stats.get("success", 0)
                            + self.today_stats.get("failure", 0),
                        )
                        * 100
                    ),
                )
            )
            self.root.destroy()

    def _start_alarm(self):
        # 휴식 상태로 전환할 때 기존 알람이 울리는 상태라면 규칙 위반
        if self.pomodoro_state == "break" and self.alarm_on:
            # 휴식 알람이 울리는 상태에서 다시 휴식에 진입 시도 → 규칙 위반
            self.today_stats["failure"] += 1
            self.consecutive_completions = 0  # 연속 완료 카운트 리셋
            messagebox.showwarning(
                "규칙 위반, 자리비움",
                "2개 세션 무효화, 휴식 알람을 끄지 않고 다시 휴식에 진입하려 했습니다.\n\n"
                "포모도로 기법의 효과를 위해서 절차를 준수해주세요.",
            )
            # 타이머 정지 및 리셋
            self.pomodoro_state = "stopped"
            self.seconds_left = self.work_duration
            self.alarm_on = False
            if self._alarm_after_id:
                self.root.after_cancel(self._alarm_after_id)
                self._alarm_after_id = None
            self._update_pomodoro_button()
            self._update_timer_display()
            if self.selected_date == datetime.now().date():
                self._update_stats_display()
            self._save_data()
            return

        # 정상적인 알람 시작
        if not self.alarm_on:
            self.alarm_on = True
            self._ring_bell_repeatedly()

    def _ring_bell_repeatedly(self):
        if self.alarm_on:
            self._play_notification_sound()
            self._alarm_after_id = self.root.after(
                1000, self._ring_bell_repeatedly
            )  # Ring every second

    def alarm_stop_(self):
        if self.alarm_on:
            # 휴식 상태에서 알람을 끄는 경우: 기존의 정상적인 흐름 그대로
            if self.pomodoro_state == "break":
                self.alarm_on = False
                if self._alarm_after_id:
                    self.root.after_cancel(self._alarm_after_id)
                    self._alarm_after_id = None
                # 기존 로직: _update_pomodoro_button()에서 "휴식 시간" 버튼으로 변경
                self._update_pomodoro_button()
                return

            # 작업 상태에서 알람을 끄는 경우: 확인 메시지 후 실패 처리 및 리셋
            elif self.pomodoro_state == "work":
                result = messagebox.askyesno(
                    "알람 끄기 확인",
                    "휴식 알람을 끄고 포모도로 세션을 실패로 처리하시겠습니까?\n\n"
                    "이 작업은 현재 세션을 실패로 기록하고 타이머를 리셋합니다.",
                )
                if result:
                    # 사용자가 확인한 경우 실패 처리 및 리셋
                    self.today_stats["failure"] += 1
                    self.consecutive_completions = 0  # 실패 시 연속 완료 카운트 리셋
                    self.alarm_on = False
                    if self._alarm_after_id:
                        self.root.after_cancel(self._alarm_after_id)
                        self._alarm_after_id = None

                    # 타이머 리셋
                    self.pomodoro_state = "stopped"
                    self.seconds_left = self.work_duration
                    self._update_pomodoro_button()
                    self._update_timer_display()
                    if self.selected_date == datetime.now().date():
                        self._update_stats_display()
                    self._save_data()
                    return
                else:
                    # 사용자가 취소한 경우 알람 계속 울림
                    return

            # 기타 상태에서 알람을 끄는 경우
            self.alarm_on = False
            if self._alarm_after_id:
                self.root.after_cancel(self._alarm_after_id)
                self._alarm_after_id = None
            self._update_pomodoro_button()  # Update button state immediately

    def _continue_from_break(self):
        self.alarm_stop_()

    def _show_motivation_message(self):
        """연속 완료 카운트에 따른 동기부여 메시지를 표시합니다."""
        consecutive = self.consecutive_completions

        if consecutive == 1:
            message = "🎉 첫 번째 포모도로 완료!\n\n잘하셨습니다! 이제 다음 세션을 시작해보세요."
        elif consecutive == 2:
            message = "🔥 두 번째 연속 완료!\n\n훌륭한 집중력입니다! 계속해서 좋은 페이스를 유지해보세요."
        elif consecutive == 3:
            message = "⚡ 세 번째 연속 완료!\n\n정말 대단합니다! 당신의 집중력이 점점 더 강해지고 있어요."
        elif consecutive == 4:
            message = "🚀 네 번째 연속 완료!\n\n놀라운 성과입니다! 이제 포모도로의 진정한 힘을 경험하고 계세요."
        elif consecutive == 5:
            message = "💎 다섯 번째 연속 완료!\n\n완벽한 집중력! 당신은 진정한 생산성 마스터입니다!"
        elif consecutive <= 10:
            message = f"🌟 {consecutive}번째 연속 완료!\n\n믿을 수 없는 집중력입니다! 계속해서 이 놀라운 페이스를 유지해보세요."
        else:
            message = f"🏆 {consecutive}번째 연속 완료!\n\n전설적인 집중력! 당신은 포모도로의 진정한 달인입니다!"

        messagebox.showinfo("🎯 연속 완료 축하!", message)

    def _bind_mouse_wheel_scroll(self, widget):
        """마우스 휠 스크롤을 특정 위젯(Canvas, Text 등)에 바인딩합니다."""

        def _on_mousewheel(event):
            try:
                # Linux
                if event.num == 4:
                    widget.yview_scroll(-1, "units")
                elif event.num == 5:
                    widget.yview_scroll(1, "units")
                # Windows/macOS
                else:
                    widget.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except Exception as e:
                print(f"마우스 휠 스크롤 오류: {e}")

        # 플랫폼에 맞는 바인딩 처리
        widget.bind("<MouseWheel>", _on_mousewheel)
        widget.bind("<Button-4>", _on_mousewheel)
        widget.bind("<Button-5>", _on_mousewheel)

        # 추가적인 스크롤 이벤트 바인딩
        widget.bind("<KeyPress-Up>", lambda e: widget.yview_scroll(-1, "units"))
        widget.bind("<KeyPress-Down>", lambda e: widget.yview_scroll(1, "units"))
        widget.bind("<KeyPress-Page_Up>", lambda e: widget.yview_scroll(-10, "units"))
        widget.bind("<KeyPress-Page_Down>", lambda e: widget.yview_scroll(10, "units"))

    def _on_stats_frame_enter(self):
        """통계 프레임에 마우스가 들어올 때 호출됩니다."""
        # 통계 프레임 포커스 설정
        self.stats_frame.focus_set()

    def _on_stats_frame_leave(self):
        """통계 프레임에서 마우스가 나갈 때 호출됩니다."""
        # 포커스 해제
        self.stats_frame.focus_set()

    def _on_diagnosis_window_resize(self, event):
        """진단 창 크기 변경 시 호출되는 이벤트 핸들러"""
        if (
            hasattr(self, "diag_win")
            and self.diag_win
            and event.widget == self.diag_win
        ):
            # 창 크기 변경 시 텍스트 위젯과 스크롤바 재조정
            self.diag_win.update_idletasks()

    def _start_calendar_scroll_drag(self, event):
        """캘린더 캔버스에서 마우스 드래그 스크롤을 시작합니다."""
        self.calendar_canvas.scan_mark(0, event.y)
        self.calendar_dragging = True

    def _on_calendar_scroll_drag(self, event):
        """캘린더 캔버스에서 마우스 드래그 스크롤을 처리합니다."""
        if hasattr(self, "calendar_dragging") and self.calendar_dragging:
            self.calendar_canvas.scan_dragto(0, event.y, gain=1)

    def _stop_calendar_scroll_drag(self, event):
        """캘린더 캔버스에서 마우스 드래그 스크롤을 종료합니다."""
        if hasattr(self, "calendar_dragging"):
            self.calendar_dragging = False

    def _confirm_data_deletion(self, settings_window):
        """데이터 삭제 확인 대화상자를 표시합니다."""
        # 첫 번째 확인: 정말 삭제할지 묻기
        first_confirm = messagebox.askyesno(
            "⚠️ 데이터 삭제 확인",
            "정말로 모든 데이터를 삭제하시겠습니까?\n\n"
            "이 작업은 되돌릴 수 없으며 다음 데이터들이 삭제됩니다:\n"
            "• 모든 뽀모도로 기록\n"
            "• 모든 작업 데이터\n"
            "• 통계 데이터\n"
            "• 연속 달성 기록\n\n"
            "계속하시겠습니까?",
            icon="warning",
        )

        if not first_confirm:
            return

        # 두 번째 확인: 최종 확인
        final_confirm = messagebox.askyesno(
            "🚨 최종 확인",
            "마지막 경고입니다!\n\n"
            "모든 데이터가 영구적으로 삭제됩니다.\n"
            "정말로 진행하시겠습니까?",
            icon="error",
        )

        if final_confirm:
            self._delete_all_data()
            settings_window.destroy()
            messagebox.showinfo(
                "✅ 완료",
                "모든 데이터가 성공적으로 삭제되었습니다.\n"
                "애플리케이션이 초기 상태로 돌아갑니다.",
            )




    def _check_and_suggest_task_transfer(self):
        """가장 최근의 미완료 작업을 확인하고 오늘로 이전할지 제안합니다."""
        try:
            # 오늘 날짜가 아니면 작업 이전 제안하지 않음
            if self.selected_date != datetime.now().date():
                return
                
            # 이미 오늘 이전 제안을 했다면 다시 제안하지 않음
            if self.transfer_suggested_today:
                return
                
            # 가장 최근에 미완료 작업이 있는 날짜 찾기
            recent_incomplete_date = self._find_recent_date_with_incomplete_tasks()
            
            if recent_incomplete_date:
                # 해당 날짜의 미완료 작업 조회
                incomplete_tasks = self._get_incomplete_tasks_from_date(recent_incomplete_date)
                
                if incomplete_tasks:
                    # 사용자에게 이전할지 묻는 팝업 표시
                    self._show_incomplete_tasks_popup(recent_incomplete_date, incomplete_tasks)
                    
                    # 오늘 이전 제안 완료 플래그 설정
                    self.transfer_suggested_today = True
                    self.last_transfer_suggested_date = recent_incomplete_date
                
        except Exception as e:
            print(f"작업 이전 확인 중 오류: {e}")
            import traceback
            traceback.print_exc()
    
    def _find_recent_date_with_incomplete_tasks(self):
        """가장 최근에 미완료 작업이 있는 날짜를 찾습니다."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 오늘 이전 날짜 중 pending 상태 작업이 있는 가장 최근 날짜 찾기
            today = datetime.now().date()
            cursor.execute("""
                SELECT DISTINCT task_date 
                FROM tasks 
                WHERE task_date < ? AND status = 'pending'
                ORDER BY task_date DESC 
                LIMIT 1
            """, (today.strftime("%Y-%m-%d"),))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return datetime.strptime(result[0], "%Y-%m-%d").date()
            else:
                return None
                
        except Exception as e:
            print(f"최근 미완료 작업 날짜 찾기 오류: {e}")
            return None


if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroPlannerApp(root)
    root.mainloop()

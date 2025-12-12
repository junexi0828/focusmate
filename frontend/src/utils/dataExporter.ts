import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";
import { format } from "date-fns";
import { ko } from "date-fns/locale";

interface ExportData {
  sessions: Array<{
    date: string;
    duration: number;
    type: string;
    roomName?: string;
  }>;
  stats: {
    totalFocusTime: number;
    totalSessions: number;
    averageSession: number;
  };
}

export class DataExporter {
  static exportToCSV(data: ExportData, filename: string = "focus-stats") {
    const headers = ["날짜", "세션 유형", "집중 시간 (분)", "방 이름"];
    const rows = data.sessions.map((session) => [
      session.date,
      session.type === "work" ? "집중" : "휴식",
      session.duration.toString(),
      session.roomName || "-",
    ]);

    // Add summary row
    rows.push([]);
    rows.push(["총 통계", "", "", ""]);
    rows.push([
      "총 집중 시간",
      "",
      `${data.stats.totalFocusTime}분`,
      "",
    ]);
    rows.push([
      "총 세션 수",
      "",
      data.stats.totalSessions.toString(),
      "",
    ]);
    rows.push([
      "평균 세션 시간",
      "",
      `${data.stats.averageSession}분`,
      "",
    ]);

    const csvContent = [
      headers.join(","),
      ...rows.map((row) => row.map((cell) => `"${cell}"`).join(",")),
    ].join("\n");

    const blob = new Blob(["\uFEFF" + csvContent], {
      type: "text/csv;charset=utf-8;",
    });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);

    link.setAttribute("href", url);
    link.setAttribute(
      "download",
      `${filename}_${format(new Date(), "yyyy-MM-dd")}.csv`
    );
    link.style.visibility = "hidden";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  static exportToPDF(data: ExportData, filename: string = "focus-stats") {
    const doc = new jsPDF();

    // Title
    doc.setFontSize(20);
    doc.text("Focus Mate 통계 리포트", 14, 20);

    // Date
    doc.setFontSize(10);
    doc.text(
      `생성일: ${format(new Date(), "PPP", { locale: ko })}`,
      14,
      30
    );

    // Summary Statistics
    doc.setFontSize(14);
    doc.text("요약 통계", 14, 45);

    const summaryData = [
      ["총 집중 시간", `${Math.floor(data.stats.totalFocusTime / 60)}시간 ${data.stats.totalFocusTime % 60}분`],
      ["총 세션 수", `${data.stats.totalSessions}회`],
      ["평균 세션 시간", `${data.stats.averageSession}분`],
    ];

    autoTable(doc, {
      startY: 50,
      head: [["항목", "값"]],
      body: summaryData,
      theme: "grid",
      headStyles: { fillColor: [79, 70, 229] }, // Primary color
    });

    // Session Details
    doc.setFontSize(14);
    const finalY = (doc as any).lastAutoTable.finalY || 50;
    doc.text("세션 상세", 14, finalY + 15);

    const sessionData = data.sessions.map((session) => [
      session.date,
      session.type === "work" ? "집중" : "휴식",
      `${session.duration}분`,
      session.roomName || "-",
    ]);

    autoTable(doc, {
      startY: finalY + 20,
      head: [["날짜", "유형", "시간", "방 이름"]],
      body: sessionData,
      theme: "striped",
      headStyles: { fillColor: [79, 70, 229] },
    });

    // Save
    doc.save(`${filename}_${format(new Date(), "yyyy-MM-dd")}.pdf`);
  }
}

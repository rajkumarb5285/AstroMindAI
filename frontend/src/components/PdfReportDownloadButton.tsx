"use client";

import React, { useState } from "react";
import { Download, Loader2, FileCheck, AlertCircle } from "lucide-react";
import { ReportJobResponse } from "@/types/astrology";
import { getApiUrl } from "@/lib/api";

interface PdfReportDownloadButtonProps {
  chartId: string;
  chartName: string;
}

export function PdfReportDownloadButton({ chartId, chartName }: PdfReportDownloadButtonProps) {
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleDownload = async () => {
    setDownloading(true);
    setError(null);
    setSuccess(false);

    try {
      const token = localStorage.getItem("astromind_token") || "test-token-usr_golden_001";

      // 1. Trigger report generation
      const genRes = await fetch(getApiUrl(`/api/v1/charts/${chartId}/reports`), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          title: `Kundli Report — ${chartName}`,
        }),
      });

      if (!genRes.ok) {
        throw new Error(`Report generation returned ${genRes.status}`);
      }

      const reportJob: ReportJobResponse = await genRes.json();

      // 2. Fetch binary PDF using token or presigned S3 URL
      const isS3Presigned = reportJob.download_url.startsWith("http://") || reportJob.download_url.startsWith("https://");
      const downloadTarget = isS3Presigned ? reportJob.download_url : getApiUrl(reportJob.download_url);
      const downloadHeaders: Record<string, string> = isS3Presigned ? {} : { Authorization: `Bearer ${token}` };

      const dlRes = await fetch(downloadTarget, {
        headers: downloadHeaders,
      });

      if (!dlRes.ok) {
        throw new Error(`Report download returned ${dlRes.status}`);
      }

      const blob = await dlRes.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `AstroMind_Kundli_${chartName.replace(/\s+/g, "_")}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      setSuccess(true);
      setTimeout(() => setSuccess(false), 4000);
    } catch (err: any) {
      setError(err.message || "Failed to download PDF report.");
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="inline-flex flex-col items-start gap-1">
      <button
        onClick={handleDownload}
        disabled={downloading}
        className="px-4 py-2 rounded-xl bg-surface-card hover:bg-gold-500/10 border border-surface-border hover:border-gold-500/40 text-xs font-medium text-slate-200 hover:text-gold-200 flex items-center gap-2 transition-all shadow-sm active:scale-95 disabled:opacity-50"
      >
        {downloading ? (
          <Loader2 className="w-4 h-4 text-gold-400 animate-spin" />
        ) : success ? (
          <FileCheck className="w-4 h-4 text-emerald-400" />
        ) : (
          <Download className="w-4 h-4 text-gold-400" />
        )}
        <span>{downloading ? "Generating PDF..." : success ? "Downloaded!" : "Export Kundli PDF"}</span>
      </button>

      {error && (
        <span className="text-[10px] text-rose-400 flex items-center gap-1 mt-0.5">
          <AlertCircle className="w-3 h-3" />
          {error}
        </span>
      )}
    </div>
  );
}

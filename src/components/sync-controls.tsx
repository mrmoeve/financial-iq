"use client";

import { RefreshCcw } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState, useTransition } from "react";

export function SyncControls() {
  const router = useRouter();
  const [message, setMessage] = useState<string>("");
  const [pending, startTransition] = useTransition();
  const [reportPending, setReportPending] = useState(false);

  return (
    <div className="button-row">
      <button
        className="primary-button"
        type="button"
        onClick={() =>
          startTransition(async () => {
            setMessage("Syncing Gmail activity...");
            const response = await fetch("/api/sync", { method: "POST" });
            const result = (await response.json()) as { createdActivities?: number; error?: string };
            setMessage(result.error ? result.error : `Sync complete. Added ${result.createdActivities ?? 0} new activities.`);
            router.refresh();
          })
        }
      >
        <RefreshCcw size={16} style={{ verticalAlign: "text-bottom" }} /> {pending ? "Syncing..." : "Sync Gmail"}
      </button>
      <button
        className="secondary-button"
        type="button"
        onClick={async () => {
          setReportPending(true);
          window.location.href = "/api/report";
          setTimeout(() => setReportPending(false), 1200);
        }}
      >
        {reportPending ? "Preparing PDF..." : "Generate NYS Work Search Report"}
      </button>
      {message ? <span className="muted">{message}</span> : null}
    </div>
  );
}

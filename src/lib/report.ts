import { PDFDocument, StandardFonts, rgb } from "pdf-lib";

import { formatCompactDate } from "@/src/lib/utils";

type ReportRow = {
  activityType: string;
  eventDate: string;
  companyName: string;
  jobTitle: string | null;
  recruiterName: string | null;
  interviewDate: string | null;
  sourceSystem: string | null;
  notes: string | null;
};

function labelForActivity(activityType: string) {
  switch (activityType) {
    case "interview_invitation":
      return "Interview scheduled";
    case "recruiter_outreach":
      return "Recruiter contact";
    case "application_confirmation":
      return "Application confirmation";
    default:
      return "Applied online";
  }
}

export async function buildNysWorkSearchPdf(userName: string, userEmail: string, rows: ReportRow[]) {
  const pdf = await PDFDocument.create();
  let page = pdf.addPage([612, 792]);
  const regular = await pdf.embedFont(StandardFonts.Helvetica);
  const bold = await pdf.embedFont(StandardFonts.HelveticaBold);

  let y = 748;
  const left = 42;

  page.drawText("NYS Work Search Report", {
    x: left,
    y,
    size: 20,
    font: bold,
    color: rgb(0.08, 0.14, 0.23),
  });

  y -= 26;
  page.drawText(`Prepared for: ${userName || userEmail}`, {
    x: left,
    y,
    size: 11,
    font: regular,
    color: rgb(0.25, 0.3, 0.36),
  });

  y -= 16;
  page.drawText(`Email: ${userEmail}`, {
    x: left,
    y,
    size: 11,
    font: regular,
    color: rgb(0.25, 0.3, 0.36),
  });

  y -= 16;
  page.drawText(`Generated: ${formatCompactDate(new Date())}`, {
    x: left,
    y,
    size: 11,
    font: regular,
    color: rgb(0.25, 0.3, 0.36),
  });

  y -= 28;
  const headers = ["Date", "Employer", "Position", "Activity", "Contact / Result"];
  const widths = [70, 110, 120, 115, 115];
  let x = left;

  for (let index = 0; index < headers.length; index += 1) {
    page.drawRectangle({
      x,
      y: y - 16,
      width: widths[index],
      height: 18,
      color: rgb(0.08, 0.14, 0.23),
    });
    page.drawText(headers[index], {
      x: x + 4,
      y: y - 11,
      size: 9,
      font: bold,
      color: rgb(1, 1, 1),
    });
    x += widths[index];
  }

  y -= 28;

  for (const row of rows) {
    if (y < 72) {
      y = 748;
      page = pdf.addPage([612, 792]);
    }

    const values = [
      formatCompactDate(row.eventDate),
      row.companyName,
      row.jobTitle ?? "Unknown role",
      labelForActivity(row.activityType),
      [row.recruiterName, row.sourceSystem, row.interviewDate ? `Interview: ${formatCompactDate(row.interviewDate)}` : null]
        .filter(Boolean)
        .join(" • ") || row.notes || "",
    ];

    x = left;
    for (let index = 0; index < values.length; index += 1) {
      page.drawRectangle({
        x,
        y: y - 28,
        width: widths[index],
        height: 30,
        borderColor: rgb(0.83, 0.86, 0.9),
        borderWidth: 1,
      });
      page.drawText(values[index].slice(0, 52), {
        x: x + 4,
        y: y - 18,
        size: 8.5,
        font: regular,
        color: rgb(0.15, 0.2, 0.25),
        maxWidth: widths[index] - 8,
      });
      x += widths[index];
    }

    y -= 32;
  }

  return Buffer.from(await pdf.save());
}

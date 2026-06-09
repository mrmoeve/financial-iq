import type { NextApiRequest, NextApiResponse } from "next";

import { getAuthSession } from "@/src/lib/auth";
import { getReportRows, getUserById } from "@/src/lib/repository";
import { buildNysWorkSearchPdf } from "@/src/lib/report";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== "GET") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  const session = await getAuthSession(req, res);
  if (!session?.user?.id) {
    return res.status(401).json({ error: "Unauthorized" });
  }

  const user = await getUserById(session.user.id);
  if (!user) {
    return res.status(404).json({ error: "User not found" });
  }

  const pdf = await buildNysWorkSearchPdf(user.name ?? "", user.email, await getReportRows(user.id));
  res.setHeader("Content-Type", "application/pdf");
  res.setHeader("Content-Disposition", 'attachment; filename="nys-work-search-report.pdf"');
  res.status(200).send(pdf);
}

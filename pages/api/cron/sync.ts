import type { NextApiRequest, NextApiResponse } from "next";

import { syncUserMailbox } from "@/src/lib/gmail";
import { listUsersWithTokens } from "@/src/lib/repository";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== "GET") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  if (req.headers.authorization !== `Bearer ${process.env.CRON_SECRET}`) {
    return res.status(401).json({ error: "Unauthorized" });
  }

  const users = await listUsersWithTokens();
  const results = [];

  for (const user of users) {
    try {
      const sync = await syncUserMailbox(user.id);
      results.push({ userId: user.id, email: user.email, ...sync });
    } catch (error) {
      results.push({
        userId: user.id,
        email: user.email,
        ok: false,
        error: error instanceof Error ? error.message : "Sync failed",
      });
    }
  }

  return res.status(200).json({ results });
}

import type { NextApiRequest, NextApiResponse } from "next";

import { getAuthSession } from "@/src/lib/auth";
import { syncUserMailbox } from "@/src/lib/gmail";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  const session = await getAuthSession(req, res);
  if (!session?.user?.id) {
    return res.status(401).json({ error: "Unauthorized" });
  }

  try {
    const result = await syncUserMailbox(session.user.id);
    return res.status(200).json(result);
  } catch (error) {
    return res.status(500).json({
      error: error instanceof Error ? error.message : "Unable to sync Gmail right now.",
    });
  }
}

import { google } from "googleapis";

import { extractJobActivity } from "@/src/lib/extract";
import {
  createMessage,
  getMessageByGmailId,
  getUserById,
  updateUserTokens,
  upsertActivity,
} from "@/src/lib/repository";
import type { UserRecord } from "@/src/lib/types";
import { decodeBase64Url } from "@/src/lib/utils";

const GMAIL_SCOPE = "https://www.googleapis.com/auth/gmail.readonly";

function getOAuthClient(user: UserRecord) {
  const client = new google.auth.OAuth2(process.env.AUTH_GOOGLE_ID, process.env.AUTH_GOOGLE_SECRET);
  client.setCredentials({
    access_token: user.accessToken ?? undefined,
    refresh_token: user.refreshToken ?? undefined,
    expiry_date: user.tokenExpiresAt ?? undefined,
  });

  client.on("tokens", (tokens) => {
    updateUserTokens(user.id, {
      accessToken: tokens.access_token,
      refreshToken: tokens.refresh_token,
      tokenExpiresAt: tokens.expiry_date ?? null,
    });
  });

  return client;
}

function decodeBody(parts?: Array<{ mimeType?: string | null; body?: { data?: string | null } | null; parts?: unknown[] }>, bodyData?: string | null): string {
  if (bodyData) {
    return decodeBase64Url(bodyData);
  }

  if (!parts) {
    return "";
  }

  for (const part of parts) {
    if (part.mimeType === "text/plain" && part.body?.data) {
      return decodeBase64Url(part.body.data);
    }
    if (part.mimeType === "text/html" && part.body?.data) {
      return decodeBase64Url(part.body.data).replace(/<[^>]+>/g, " ");
    }
    if (part.parts) {
      const nested = decodeBody(part.parts as never, null);
      if (nested) {
        return nested;
      }
    }
  }

  return "";
}

function getHeader(headers: Array<{ name?: string | null; value?: string | null }> | undefined, name: string) {
  return headers?.find((entry) => entry.name?.toLowerCase() === name.toLowerCase())?.value ?? "";
}

function parseFromHeader(fromValue: string) {
  const match = fromValue.match(/^(.*?)(?:\s*<([^>]+)>)?$/);
  return {
    fromName: match?.[1]?.replace(/"/g, "").trim() || "",
    fromEmail: match?.[2]?.trim() || fromValue.trim(),
  };
}

export async function syncUserMailbox(userId: string) {
  const user = await getUserById(userId);
  if (!user?.accessToken) {
    throw new Error("Missing Google access token for mailbox sync.");
  }

  const auth = getOAuthClient(user);
  const gmail = google.gmail({ version: "v1", auth });
  const lookbackDays = Number(process.env.GMAIL_SYNC_LOOKBACK_DAYS ?? "30");
  const query =
    `newer_than:${lookbackDays}d (` +
    [
      "from:linkedin.com",
      "from:linkedinmail.com",
      "from:greenhouse.io",
      "from:lever.co",
      "from:workday.com",
      "from:ashbyhq.com",
      "from:smartrecruiters.com",
      "recruiter",
      "interview",
      '"thank you for applying"',
    ].join(" OR ") +
    ")";

  const list = await gmail.users.messages.list({
    userId: "me",
    maxResults: 100,
    q: query,
  });

  const messages = list.data.messages ?? [];
  let createdActivities = 0;

  for (const message of messages) {
    if (!message.id || (await getMessageByGmailId(message.id))) {
      continue;
    }

    const full = await gmail.users.messages.get({
      userId: "me",
      id: message.id,
      format: "full",
    });

    const payload = full.data.payload;
    const subject = getHeader(payload?.headers, "Subject");
    const dateHeader = getHeader(payload?.headers, "Date");
    const fromHeader = getHeader(payload?.headers, "From");
    const { fromEmail, fromName } = parseFromHeader(fromHeader);
    const body = decodeBody(payload?.parts, payload?.body?.data ?? null);
    const receivedAt = dateHeader ? new Date(dateHeader).toISOString() : new Date().toISOString();

    const storedMessage = await createMessage({
      userId,
      gmailMessageId: message.id,
      threadId: full.data.threadId ?? null,
      fromEmail,
      fromName,
      subject: subject || null,
      snippet: full.data.snippet ?? null,
      receivedAt,
      rawPayload: JSON.stringify(full.data),
    });

    const extracted = extractJobActivity({
      subject,
      snippet: full.data.snippet ?? "",
      body,
      fromEmail,
      fromName,
      receivedAt,
    });

    if (extracted) {
      await upsertActivity(userId, storedMessage.id, extracted);
      createdActivities += 1;
    }
  }

  return {
    ok: true,
    scope: GMAIL_SCOPE,
    scannedMessages: messages.length,
    createdActivities,
  };
}

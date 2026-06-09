import { randomUUID } from "node:crypto";

import { getDb, persistDb } from "@/src/lib/db";
import type { ActivityRecord, ExtractedActivity, MessageRecord, UserRecord } from "@/src/lib/types";
import { startOfWeek, toIsoDate } from "@/src/lib/utils";

function nowIso() {
  return new Date().toISOString();
}

function normalizeRow<T>(value: unknown): T | undefined {
  return (value as T | undefined) ?? undefined;
}

async function getOne<T extends object>(sql: string, params: Array<string | number | null> = []) {
  const db = await getDb();
  const statement = db.prepare(sql);
  try {
    statement.bind(params);
    if (!statement.step()) {
      return undefined;
    }
    return normalizeRow<T>(statement.getAsObject());
  } finally {
    statement.free();
  }
}

async function getAll<T extends object>(sql: string, params: Array<string | number | null> = []) {
  const db = await getDb();
  const statement = db.prepare(sql);
  const rows: T[] = [];

  try {
    statement.bind(params);
    while (statement.step()) {
      rows.push(statement.getAsObject() as T);
    }
  } finally {
    statement.free();
  }

  return rows;
}

async function run(sql: string, params: Array<string | number | null> = []) {
  const db = await getDb();
  db.run(sql, params);
  await persistDb();
}

export async function upsertUser(input: {
  id: string;
  email: string;
  name?: string | null;
  image?: string | null;
  accessToken?: string | null;
  refreshToken?: string | null;
  tokenExpiresAt?: number | null;
}) {
  const existing = await getUserByEmail(input.email);
  const timestamp = nowIso();

  if (existing) {
    await run(
      `
        UPDATE users
        SET
          id = ?,
          name = ?,
          image = ?,
          access_token = COALESCE(?, access_token),
          refresh_token = COALESCE(?, refresh_token),
          token_expires_at = COALESCE(?, token_expires_at),
          updated_at = ?
        WHERE email = ?
      `,
      [
        input.id,
        input.name ?? null,
        input.image ?? null,
        input.accessToken ?? null,
        input.refreshToken ?? null,
        input.tokenExpiresAt ?? null,
        timestamp,
        input.email,
      ],
    );
  } else {
    await run(
      `
        INSERT INTO users (
          id, email, name, image, access_token, refresh_token, token_expires_at, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
      `,
      [
        input.id,
        input.email,
        input.name ?? null,
        input.image ?? null,
        input.accessToken ?? null,
        input.refreshToken ?? null,
        input.tokenExpiresAt ?? null,
        timestamp,
        timestamp,
      ],
    );
  }

  return getUserByEmail(input.email);
}

export async function updateUserTokens(
  userId: string,
  tokens: { accessToken?: string | null; refreshToken?: string | null; tokenExpiresAt?: number | null },
) {
  await run(
    `
      UPDATE users
      SET
        access_token = COALESCE(?, access_token),
        refresh_token = COALESCE(?, refresh_token),
        token_expires_at = COALESCE(?, token_expires_at),
        updated_at = ?
      WHERE id = ?
    `,
    [tokens.accessToken ?? null, tokens.refreshToken ?? null, tokens.tokenExpiresAt ?? null, nowIso(), userId],
  );
}

export async function getUserByEmail(email: string) {
  return getOne<UserRecord>(
    `
      SELECT
        id,
        email,
        name,
        image,
        access_token as accessToken,
        refresh_token as refreshToken,
        token_expires_at as tokenExpiresAt,
        created_at as createdAt,
        updated_at as updatedAt
      FROM users
      WHERE email = ?
    `,
    [email],
  );
}

export async function getUserById(id: string) {
  return getOne<UserRecord>(
    `
      SELECT
        id,
        email,
        name,
        image,
        access_token as accessToken,
        refresh_token as refreshToken,
        token_expires_at as tokenExpiresAt,
        created_at as createdAt,
        updated_at as updatedAt
      FROM users
      WHERE id = ?
    `,
    [id],
  );
}

export async function listUsersWithTokens() {
  return getAll<UserRecord>(
    `
      SELECT
        id,
        email,
        name,
        image,
        access_token as accessToken,
        refresh_token as refreshToken,
        token_expires_at as tokenExpiresAt,
        created_at as createdAt,
        updated_at as updatedAt
      FROM users
      WHERE access_token IS NOT NULL
    `,
  );
}

export async function getMessageByGmailId(gmailMessageId: string) {
  return getOne<MessageRecord>(
    `
      SELECT
        id,
        user_id as userId,
        gmail_message_id as gmailMessageId,
        thread_id as threadId,
        from_email as fromEmail,
        from_name as fromName,
        subject,
        snippet,
        received_at as receivedAt,
        raw_payload as rawPayload,
        created_at as createdAt
      FROM gmail_messages
      WHERE gmail_message_id = ?
    `,
    [gmailMessageId],
  );
}

export async function createMessage(input: Omit<MessageRecord, "id" | "createdAt">) {
  const id = randomUUID();
  const createdAt = nowIso();

  await run(
    `
      INSERT INTO gmail_messages (
        id, user_id, gmail_message_id, thread_id, from_email, from_name, subject, snippet, received_at, raw_payload, created_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `,
    [
      id,
      input.userId,
      input.gmailMessageId,
      input.threadId,
      input.fromEmail,
      input.fromName,
      input.subject,
      input.snippet,
      input.receivedAt,
      input.rawPayload,
      createdAt,
    ],
  );

  return { id, createdAt, ...input } satisfies MessageRecord;
}

export async function upsertActivity(userId: string, messageId: string, extracted: ExtractedActivity) {
  const existing = await getOne<ActivityRecord>(
    `
      SELECT
        id,
        user_id as userId,
        message_id as messageId,
        activity_type as activityType,
        event_date as eventDate,
        company_name as companyName,
        job_title as jobTitle,
        recruiter_name as recruiterName,
        interview_date as interviewDate,
        source_system as sourceSystem,
        confidence,
        notes,
        created_at as createdAt
      FROM job_activities
      WHERE message_id = ?
    `,
    [messageId],
  );

  if (existing) {
    await run(
      `
        UPDATE job_activities
        SET
          activity_type = ?,
          event_date = ?,
          company_name = ?,
          job_title = ?,
          recruiter_name = ?,
          interview_date = ?,
          source_system = ?,
          confidence = ?,
          notes = ?
        WHERE message_id = ?
      `,
      [
        extracted.activityType,
        extracted.eventDate,
        extracted.companyName,
        extracted.jobTitle,
        extracted.recruiterName,
        extracted.interviewDate,
        extracted.sourceSystem,
        extracted.confidence,
        extracted.notes,
        messageId,
      ],
    );

    return { ...existing, ...extracted };
  }

  const id = randomUUID();
  const createdAt = nowIso();

  await run(
    `
      INSERT INTO job_activities (
        id, user_id, message_id, activity_type, event_date, company_name, job_title, recruiter_name, interview_date, source_system, confidence, notes, created_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `,
    [
      id,
      userId,
      messageId,
      extracted.activityType,
      extracted.eventDate,
      extracted.companyName,
      extracted.jobTitle,
      extracted.recruiterName,
      extracted.interviewDate,
      extracted.sourceSystem,
      extracted.confidence,
      extracted.notes,
      createdAt,
    ],
  );

  return {
    id,
    userId,
    messageId,
    createdAt,
    ...extracted,
  } satisfies ActivityRecord;
}

export async function getDashboardData(userId: string) {
  const activities = await getAll<ActivityRecord>(
    `
      SELECT
        id,
        user_id as userId,
        message_id as messageId,
        activity_type as activityType,
        event_date as eventDate,
        company_name as companyName,
        job_title as jobTitle,
        recruiter_name as recruiterName,
        interview_date as interviewDate,
        source_system as sourceSystem,
        confidence,
        notes,
        created_at as createdAt
      FROM job_activities
      WHERE user_id = ?
      ORDER BY event_date DESC, created_at DESC
    `,
    [userId],
  );

  const applications = activities.filter((item) =>
    item.activityType === "job_application" || item.activityType === "application_confirmation",
  );
  const interviews = activities.filter((item) => item.activityType === "interview_invitation");
  const recruiterContacts = activities.filter((item) => item.activityType === "recruiter_outreach");
  const companies = Array.from(new Set(applications.map((item) => item.companyName))).sort();

  const weeklyMap = new Map<string, number>();
  for (const activity of applications) {
    const key = toIsoDate(startOfWeek(new Date(activity.eventDate)));
    weeklyMap.set(key, (weeklyMap.get(key) ?? 0) + 1);
  }

  const applicationsByWeek = Array.from(weeklyMap.entries())
    .sort(([left], [right]) => left.localeCompare(right))
    .map(([weekStart, count]) => ({ weekStart, count }));

  return {
    activities,
    totals: {
      applications: applications.length,
      interviews: interviews.length,
      recruiterContacts: recruiterContacts.length,
      companies: companies.length,
    },
    interviews,
    recruiterContacts,
    companies,
    applicationsByWeek,
  };
}

export async function getReportRows(userId: string) {
  return getAll<{
    activityType: string;
    eventDate: string;
    companyName: string;
    jobTitle: string | null;
    recruiterName: string | null;
    interviewDate: string | null;
    sourceSystem: string | null;
    notes: string | null;
  }>(
    `
      SELECT
        activity_type as activityType,
        event_date as eventDate,
        company_name as companyName,
        job_title as jobTitle,
        recruiter_name as recruiterName,
        interview_date as interviewDate,
        source_system as sourceSystem,
        notes
      FROM job_activities
      WHERE user_id = ?
      ORDER BY event_date DESC, created_at DESC
    `,
    [userId],
  );
}

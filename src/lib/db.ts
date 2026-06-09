import fs from "node:fs/promises";
import path from "node:path";

import initSqlJs, { type Database } from "sql.js";

const databasePath = path.join(process.cwd(), "job-tracker.db");

declare global {
  var __jobTrackerDb: Promise<Database> | undefined;
}

async function createDatabase() {
  const SQL = await initSqlJs({
    locateFile: (file) => path.join(process.cwd(), "node_modules", "sql.js", "dist", file),
  });

  let db: Database;
  try {
    const bytes = await fs.readFile(databasePath);
    db = new SQL.Database(bytes);
  } catch {
    db = new SQL.Database();
  }

  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY,
      email TEXT NOT NULL UNIQUE,
      name TEXT,
      image TEXT,
      access_token TEXT,
      refresh_token TEXT,
      token_expires_at INTEGER,
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS gmail_messages (
      id TEXT PRIMARY KEY,
      user_id TEXT NOT NULL,
      gmail_message_id TEXT NOT NULL UNIQUE,
      thread_id TEXT,
      from_email TEXT,
      from_name TEXT,
      subject TEXT,
      snippet TEXT,
      received_at TEXT NOT NULL,
      raw_payload TEXT NOT NULL,
      created_at TEXT NOT NULL,
      FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS job_activities (
      id TEXT PRIMARY KEY,
      user_id TEXT NOT NULL,
      message_id TEXT NOT NULL UNIQUE,
      activity_type TEXT NOT NULL,
      event_date TEXT NOT NULL,
      company_name TEXT NOT NULL,
      job_title TEXT,
      recruiter_name TEXT,
      interview_date TEXT,
      source_system TEXT,
      confidence REAL NOT NULL,
      notes TEXT,
      created_at TEXT NOT NULL,
      FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
      FOREIGN KEY (message_id) REFERENCES gmail_messages(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_job_activities_user_event_date
    ON job_activities(user_id, event_date DESC);

    CREATE INDEX IF NOT EXISTS idx_gmail_messages_user_received_at
    ON gmail_messages(user_id, received_at DESC);
  `);

  return db;
}

export async function getDb() {
  if (!global.__jobTrackerDb) {
    global.__jobTrackerDb = createDatabase();
  }

  return global.__jobTrackerDb;
}

export async function persistDb() {
  const db = await getDb();
  const data = db.export();
  await fs.writeFile(databasePath, Buffer.from(data));
}

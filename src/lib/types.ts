export type ActivityType =
  | "job_application"
  | "application_confirmation"
  | "interview_invitation"
  | "recruiter_outreach";

export type UserRecord = {
  id: string;
  email: string;
  name: string | null;
  image: string | null;
  accessToken: string | null;
  refreshToken: string | null;
  tokenExpiresAt: number | null;
  createdAt: string;
  updatedAt: string;
};

export type MessageRecord = {
  id: string;
  userId: string;
  gmailMessageId: string;
  threadId: string | null;
  fromEmail: string | null;
  fromName: string | null;
  subject: string | null;
  snippet: string | null;
  receivedAt: string;
  rawPayload: string;
  createdAt: string;
};

export type ActivityRecord = {
  id: string;
  userId: string;
  messageId: string;
  activityType: ActivityType;
  eventDate: string;
  companyName: string;
  jobTitle: string | null;
  recruiterName: string | null;
  interviewDate: string | null;
  sourceSystem: string | null;
  confidence: number;
  notes: string | null;
  createdAt: string;
};

export type ExtractedActivity = {
  activityType: ActivityType;
  eventDate: string;
  companyName: string;
  jobTitle: string | null;
  recruiterName: string | null;
  interviewDate: string | null;
  sourceSystem: string | null;
  confidence: number;
  notes: string | null;
};

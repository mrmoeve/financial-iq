import type { ActivityType, ExtractedActivity } from "@/src/lib/types";

type MessageInput = {
  subject: string;
  snippet: string;
  body: string;
  fromEmail: string;
  fromName: string;
  receivedAt: string;
};

const systemMatchers: Array<{ label: string; pattern: RegExp }> = [
  { label: "LinkedIn", pattern: /linkedin/i },
  { label: "Greenhouse", pattern: /greenhouse/i },
  { label: "Lever", pattern: /lever/i },
  { label: "Workday", pattern: /workday/i },
  { label: "Ashby", pattern: /ashby/i },
  { label: "iCIMS", pattern: /icims/i },
  { label: "SmartRecruiters", pattern: /smartrecruiters/i },
];

const typeMatchers: Array<{ type: ActivityType; patterns: RegExp[]; confidence: number }> = [
  {
    type: "interview_invitation",
    patterns: [/interview/i, /schedule/i, /meet with/i, /availability/i],
    confidence: 0.94,
  },
  {
    type: "recruiter_outreach",
    patterns: [/recruiter/i, /talent acquisition/i, /sourcing/i, /opportunity/i, /your background/i],
    confidence: 0.82,
  },
  {
    type: "application_confirmation",
    patterns: [/application received/i, /thank you for applying/i, /we received your application/i],
    confidence: 0.9,
  },
  {
    type: "job_application",
    patterns: [/applied/i, /application submitted/i, /your application/i, /job application/i],
    confidence: 0.78,
  },
];

function firstMatch(text: string, patterns: RegExp[]) {
  return patterns.every((pattern) => pattern.test(text));
}

function findSourceSystem(text: string) {
  return systemMatchers.find((entry) => entry.pattern.test(text))?.label ?? null;
}

function normalizeWhitespace(value: string) {
  return value.replace(/\s+/g, " ").trim();
}

function extractCompany(subject: string, body: string) {
  const text = `${subject}\n${body}`;
  const patterns = [
    /at\s+([A-Z][A-Za-z0-9&'. -]{1,60})/i,
    /with\s+([A-Z][A-Za-z0-9&'. -]{1,60})/i,
    /from\s+([A-Z][A-Za-z0-9&'. -]{1,60})/i,
    /team at\s+([A-Z][A-Za-z0-9&'. -]{1,60})/i,
  ];

  for (const pattern of patterns) {
    const match = text.match(pattern);
    if (match?.[1]) {
      return normalizeWhitespace(match[1].replace(/[.,:;!?]+$/, ""));
    }
  }

  const bySignature = body.match(/\n([A-Z][A-Za-z0-9&'. -]{1,60})\n(?:Hiring Team|Recruiting Team|Talent Acquisition)/i);
  if (bySignature?.[1]) {
    return normalizeWhitespace(bySignature[1]);
  }

  return "Unknown Company";
}

function extractJobTitle(subject: string, body: string) {
  const text = `${subject}\n${body}`;
  const patterns = [
    /(?:for|as|role of)\s+([A-Z][A-Za-z0-9/,&()' -]{2,80})/i,
    /position[:\s]+([A-Z][A-Za-z0-9/,&()' -]{2,80})/i,
    /job title[:\s]+([A-Z][A-Za-z0-9/,&()' -]{2,80})/i,
  ];

  for (const pattern of patterns) {
    const match = text.match(pattern);
    if (match?.[1]) {
      return normalizeWhitespace(match[1].replace(/[.,:;!?]+$/, ""));
    }
  }

  return null;
}

function extractRecruiterName(body: string, fromName: string) {
  if (fromName && !/no[-\s]?reply/i.test(fromName)) {
    return normalizeWhitespace(fromName);
  }

  const signature = body.match(/(?:Thanks|Regards|Best|Sincerely),?\s+([A-Z][A-Za-z'. -]{2,60})/i);
  return signature?.[1] ? normalizeWhitespace(signature[1]) : null;
}

function extractInterviewDate(body: string, receivedAt: string) {
  const dateMatch = body.match(
    /\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)?\.?,?\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}(?:,\s+\d{4})?(?:\s+at\s+\d{1,2}(?::\d{2})?\s*(?:AM|PM))?/i,
  );
  if (dateMatch?.[0]) {
    const parsed = new Date(dateMatch[0]);
    if (!Number.isNaN(parsed.getTime())) {
      return parsed.toISOString();
    }
  }

  const fallback = body.match(/\b\d{1,2}\/\d{1,2}\/\d{2,4}\b/);
  if (fallback?.[0]) {
    const parsed = new Date(fallback[0]);
    if (!Number.isNaN(parsed.getTime())) {
      return parsed.toISOString();
    }
  }

  const received = new Date(receivedAt);
  return Number.isNaN(received.getTime()) ? null : received.toISOString();
}

export function extractJobActivity(input: MessageInput): ExtractedActivity | null {
  const subject = normalizeWhitespace(input.subject);
  const snippet = normalizeWhitespace(input.snippet);
  const body = normalizeWhitespace(input.body);
  const text = `${subject}\n${snippet}\n${body}\n${input.fromEmail}\n${input.fromName}`;

  const sourceSystem = findSourceSystem(text);
  if (!sourceSystem && !/(recruit|talent|hiring|application|interview)/i.test(text)) {
    return null;
  }

  const matchedType = typeMatchers.find((entry) => firstMatch(text, entry.patterns));
  const activityType = matchedType?.type ?? "job_application";
  const companyName = extractCompany(subject, body);
  const jobTitle = extractJobTitle(subject, body);
  const recruiterName = extractRecruiterName(body, input.fromName);

  return {
    activityType,
    eventDate: new Date(input.receivedAt).toISOString(),
    companyName,
    jobTitle,
    recruiterName,
    interviewDate: activityType === "interview_invitation" ? extractInterviewDate(body, input.receivedAt) : null,
    sourceSystem,
    confidence: matchedType?.confidence ?? 0.7,
    notes: snippet || null,
  };
}

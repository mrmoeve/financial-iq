import type { GetServerSidePropsContext, InferGetServerSidePropsType } from "next";
import { getServerSession } from "next-auth/next";

import { SignOutButton } from "@/src/components/auth-buttons";
import { SyncControls } from "@/src/components/sync-controls";
import { authOptions } from "@/src/lib/auth";
import { getDashboardData } from "@/src/lib/repository";
import { formatCompactDate } from "@/src/lib/utils";

function ActivityLabel({ type }: { type: string }) {
  const labels: Record<string, string> = {
    job_application: "Application logged",
    application_confirmation: "Confirmation received",
    interview_invitation: "Interview scheduled",
    recruiter_outreach: "Recruiter outreach",
  };

  return <span className="pill">{labels[type] ?? type}</span>;
}

export default function DashboardPage({ data }: InferGetServerSidePropsType<typeof getServerSideProps>) {
  const maxWeekCount = Math.max(...data.applicationsByWeek.map((item) => item.count), 1);

  return (
    <main className="shell">
      <section className="hero panel">
        <div className="hero-grid">
          <div>
            <span className="eyebrow">Dashboard</span>
            <h1>Track every application, callback, and interview from your inbox.</h1>
            <p>
              Gmail sync watches LinkedIn and major recruiting systems, extracts the details you need, and turns them
              into a simple record you can actually use for follow-up and compliance reporting.
            </p>
          </div>
          <div style={{ display: "grid", gap: 16, justifyItems: "start" }}>
            <SyncControls />
            <SignOutButton />
          </div>
        </div>

        <div className="stats-grid">
          <article className="stat-card panel">
            <span className="eyebrow">Applications</span>
            <div className="metric">{data.totals.applications}</div>
            <div className="submetric">Applications and confirmations found in Gmail</div>
          </article>
          <article className="stat-card panel">
            <span className="eyebrow">Interviews</span>
            <div className="metric">{data.totals.interviews}</div>
            <div className="submetric">Interview invites currently logged</div>
          </article>
          <article className="stat-card panel">
            <span className="eyebrow">Recruiters</span>
            <div className="metric">{data.totals.recruiterContacts}</div>
            <div className="submetric">Recruiter outreach messages classified</div>
          </article>
          <article className="stat-card panel">
            <span className="eyebrow">Companies</span>
            <div className="metric">{data.totals.companies}</div>
            <div className="submetric">Unique employers you applied to</div>
          </article>
        </div>
      </section>

      <section className="detail-grid">
        <article className="chart-card panel">
          <span className="eyebrow">Applications By Week</span>
          <div className="mini-bars" style={{ marginTop: 20 }}>
            {data.applicationsByWeek.length ? (
              data.applicationsByWeek.map((item) => (
                <div className="bar-row" key={item.weekStart}>
                  <span className="muted">{formatCompactDate(item.weekStart)}</span>
                  <div className="bar-track">
                    <div className="bar-fill" style={{ width: `${(item.count / maxWeekCount) * 100}%` }} />
                  </div>
                  <strong>{item.count}</strong>
                </div>
              ))
            ) : (
              <p className="muted">Run your first Gmail sync to populate weekly application totals.</p>
            )}
          </div>
        </article>

        <article className="list-card panel">
          <span className="eyebrow">Companies Applied To</span>
          <ul className="list" style={{ marginTop: 20 }}>
            {data.companies.length ? (
              data.companies.map((company) => (
                <li className="list-item" key={company}>
                  <strong>{company}</strong>
                </li>
              ))
            ) : (
              <li className="list-item">
                <span className="muted">No companies logged yet.</span>
              </li>
            )}
          </ul>
        </article>
      </section>

      <section className="detail-grid">
        <article className="list-card panel">
          <span className="eyebrow">Interviews Scheduled</span>
          <ul className="list" style={{ marginTop: 20 }}>
            {data.interviews.length ? (
              data.interviews.map((item) => (
                <li className="list-item" key={item.id}>
                  <ActivityLabel type={item.activityType} />
                  <strong>{item.companyName}</strong>
                  <span>{item.jobTitle ?? "Unknown role"}</span>
                  <span className="muted">
                    {item.interviewDate ? `Interview on ${formatCompactDate(item.interviewDate)}` : "Date not parsed"}
                  </span>
                </li>
              ))
            ) : (
              <li className="list-item">
                <span className="muted">No interview invitations detected yet.</span>
              </li>
            )}
          </ul>
        </article>

        <article className="list-card panel">
          <span className="eyebrow">Recruiter Contacts</span>
          <ul className="list" style={{ marginTop: 20 }}>
            {data.recruiterContacts.length ? (
              data.recruiterContacts.map((item) => (
                <li className="list-item" key={item.id}>
                  <ActivityLabel type={item.activityType} />
                  <strong>{item.recruiterName ?? item.companyName}</strong>
                  <span>{item.companyName}</span>
                  <span className="muted">{item.jobTitle ?? "Role not extracted"}</span>
                </li>
              ))
            ) : (
              <li className="list-item">
                <span className="muted">No recruiter outreach detected yet.</span>
              </li>
            )}
          </ul>
        </article>
      </section>

      <section style={{ marginTop: 24 }}>
        <article className="list-card panel">
          <span className="eyebrow">Recent Activity</span>
          <ul className="list" style={{ marginTop: 20 }}>
            {data.activities.length ? (
              data.activities.slice(0, 12).map((item) => (
                <li className="list-item" key={item.id}>
                  <ActivityLabel type={item.activityType} />
                  <strong>{item.companyName}</strong>
                  <span>
                    {item.jobTitle ?? "Unknown role"} {item.recruiterName ? `• ${item.recruiterName}` : ""}
                  </span>
                  <span className="muted">{formatCompactDate(item.eventDate)}</span>
                </li>
              ))
            ) : (
              <li className="list-item">
                <span className="muted">No activity found yet. Connect Google and run Gmail sync to get started.</span>
              </li>
            )}
          </ul>
        </article>
      </section>
    </main>
  );
}

export async function getServerSideProps(context: GetServerSidePropsContext) {
  const session = await getServerSession(context.req, context.res, authOptions);
  if (!session?.user?.id) {
    return {
      redirect: {
        destination: "/signin",
        permanent: false,
      },
    };
  }

  return {
    props: {
      data: await getDashboardData(session.user.id),
    },
  };
}

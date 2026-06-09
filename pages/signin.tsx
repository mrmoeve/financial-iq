import type { GetServerSidePropsContext } from "next";
import { getServerSession } from "next-auth/next";

import { GoogleSignInButton } from "@/src/components/auth-buttons";
import { authOptions } from "@/src/lib/auth";

export default function SignInPage() {
  return (
    <main className="signin-shell">
      <section className="signin-card panel">
        <span className="eyebrow">LinkedIn Job Search Tracker</span>
        <h1>Turn your Gmail job-search trail into a clean weekly work-search log.</h1>
        <p>
          Connect Google once, monitor LinkedIn and recruiting-system emails, and keep applications, interviews,
          recruiter outreach, and confirmations in one place with an NYS-ready PDF export.
        </p>
        <div className="button-row" style={{ marginTop: 24 }}>
          <GoogleSignInButton />
        </div>
        <p className="footer-note">
          The app requests Gmail read-only access so it can detect job-search activity without modifying your mailbox.
        </p>
      </section>
    </main>
  );
}

export async function getServerSideProps(context: GetServerSidePropsContext) {
  const session = await getServerSession(context.req, context.res, authOptions);
  if (session?.user?.id) {
    return {
      redirect: {
        destination: "/",
        permanent: false,
      },
    };
  }

  return {
    props: {},
  };
}

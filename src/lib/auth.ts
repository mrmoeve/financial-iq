import type { NextApiRequest, NextApiResponse } from "next";
import type { Account, NextAuthOptions, Profile, Session, User } from "next-auth";
import { getServerSession } from "next-auth/next";
import type { JWT } from "next-auth/jwt";
import GoogleProvider from "next-auth/providers/google";

import { getUserByEmail, upsertUser } from "@/src/lib/repository";

export const authOptions: NextAuthOptions = {
  session: {
    strategy: "jwt",
  },
  pages: {
    signIn: "/signin",
  },
  providers: [
    GoogleProvider({
      clientId: process.env.AUTH_GOOGLE_ID ?? "",
      clientSecret: process.env.AUTH_GOOGLE_SECRET ?? "",
      authorization: {
        params: {
          access_type: "offline",
          prompt: "consent",
          scope: "openid email profile https://www.googleapis.com/auth/gmail.readonly",
        },
      },
    }),
  ],
  callbacks: {
    async signIn({ user, account }: { user: User; account: Account | null; profile?: Profile }) {
      if (!user.email) {
        return false;
      }

      await upsertUser({
        id: user.id ?? user.email,
        email: user.email,
        name: user.name,
        image: user.image,
        accessToken: account?.access_token ?? null,
        refreshToken: account?.refresh_token ?? null,
        tokenExpiresAt: account?.expires_at ? account.expires_at * 1000 : null,
      });

      return true;
    },
    async jwt({ token, user, account }: { token: JWT; user?: User; account?: Account | null }) {
      const email = user?.email ?? token.email;
      if (email) {
        const record = await getUserByEmail(email);
        if (record) {
          token.userId = record.id;
          token.picture = record.image ?? token.picture;
          token.name = record.name ?? token.name;
          token.email = record.email;
        }
      }

      if (account?.access_token) {
        token.accessToken = account.access_token;
      }

      return token;
    },
    async session({ session, token }: { session: Session; token: JWT }) {
      if (session.user) {
        session.user.id = String(token.userId ?? "");
      }

      return session;
    },
  },
};

export function getAuthSession(req: NextApiRequest, res: NextApiResponse) {
  return getServerSession(req, res, authOptions);
}

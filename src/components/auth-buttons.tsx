"use client";

import { LoaderCircle, LogOut, MailCheck } from "lucide-react";
import { signIn, signOut } from "next-auth/react";
import { useState, useTransition } from "react";

export function GoogleSignInButton() {
  const [pending, startTransition] = useTransition();

  return (
    <button
      className="primary-button"
      onClick={() =>
        startTransition(() => {
          void signIn("google", { callbackUrl: "/" });
        })
      }
      type="button"
    >
      {pending ? <LoaderCircle size={16} style={{ verticalAlign: "text-bottom" }} /> : <MailCheck size={16} style={{ verticalAlign: "text-bottom" }} />}{" "}
      Sign in with Google
    </button>
  );
}

export function SignOutButton() {
  const [pending, setPending] = useState(false);

  return (
    <button
      className="secondary-button"
      onClick={async () => {
        setPending(true);
        await signOut({ callbackUrl: "/signin" });
      }}
      type="button"
    >
      {pending ? <LoaderCircle size={16} style={{ verticalAlign: "text-bottom" }} /> : <LogOut size={16} style={{ verticalAlign: "text-bottom" }} />}{" "}
      Sign out
    </button>
  );
}

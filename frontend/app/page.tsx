import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { TopBar } from "@/components/TopBar";
import { Workspace } from "@/components/Workspace";
import { ApiError, listDocuments, type LeaseDocument } from "@/lib/api";
import { EMAIL_COOKIE, TOKEN_COOKIE, initialsFromEmail } from "@/lib/session";

export default async function Home() {
  const cookieStore = await cookies();
  const token = cookieStore.get(TOKEN_COOKIE)?.value;
  if (!token) redirect("/login");

  let documents: LeaseDocument[];
  try {
    documents = await listDocuments(token);
  } catch (e) {
    if (e instanceof ApiError && e.status === 401) redirect("/login");
    throw e;
  }

  const email = cookieStore.get(EMAIL_COOKIE)?.value ?? "";

  return (
    <div className="flex h-dvh flex-col">
      <TopBar initials={initialsFromEmail(email)} />
      <Workspace documents={documents} />
    </div>
  );
}

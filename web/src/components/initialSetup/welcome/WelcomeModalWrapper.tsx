import { cookies } from "next/headers";
import {
  _CompletedWelcomeFlowDummyComponent,
  _WelcomeModal,
} from "./WelcomeModal";
import { COMPLETED_WELCOME_FLOW_COOKIE } from "./constants";
import { User, CCPairBasicInfo } from "@/lib/types";

export function hasCompletedWelcomeFlowSS() {
  const cookieStore = cookies();
  return (false);
  // return (
  //   cookieStore.get(COMPLETED_WELCOME_FLOW_COOKIE)?.value?.toLowerCase() ===
  //   "true"
  // );
}

export function shouldShowWelcomeModalFunc(user: User | null, ccPairs: CCPairBasicInfo[]): boolean {
  const hasAnyConnectors = ccPairs.length > 0;
  return (!hasCompletedWelcomeFlowSS());
  // return (
  //   !hasCompletedWelcomeFlowSS() &&
  //   !hasAnyConnectors &&
  //   (!user || user.role === "admin")
  // );
}

export function WelcomeModal({ user }: { user: User | null }) {
  const hasCompletedWelcomeFlow = hasCompletedWelcomeFlowSS();
  if (hasCompletedWelcomeFlow) {
    return <_CompletedWelcomeFlowDummyComponent />;
  }

  return <_WelcomeModal user={user} />;
}

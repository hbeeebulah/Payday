"use client";

import { useEffect } from "react";
import { hydrateAuth } from "@/lib/auth";
import { hydrate } from "@/lib/store";

/** Loads persisted store and auth state from localStorage once, after mount. */
export function StoreHydrator() {
  useEffect(() => {
    hydrateAuth();
    hydrate();
  }, []);
  return null;
}

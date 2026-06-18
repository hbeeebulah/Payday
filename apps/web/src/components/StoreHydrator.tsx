"use client";

import { useEffect } from "react";
import { hydrate } from "@/lib/store";

/** Loads persisted store state from localStorage once, after mount. */
export function StoreHydrator() {
  useEffect(() => {
    hydrate();
  }, []);
  return null;
}

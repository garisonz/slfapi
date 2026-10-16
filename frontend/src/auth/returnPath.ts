export function getReturnPath(state: unknown): string {
  const from = state && typeof state === "object" && "from" in state ? state.from : null;
  return typeof from === "string" && from.startsWith("/") && !from.startsWith("//")
    ? from
    : "/dashboard";
}

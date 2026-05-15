export function statusBadge(status: string): string {
  const styles: Record<string, string> = {
    created: "bg-blue-100 text-blue-700",
    running: "bg-yellow-100 text-yellow-700",
    complete: "bg-green-100 text-green-700",
    completed: "bg-green-100 text-green-700",
    cancelled: "bg-red-100 text-red-700",
    failed: "bg-red-100 text-red-700",
    interrupted: "bg-orange-100 text-orange-700",
  };
  return styles[status] || "bg-gray-100 text-gray-600";
}

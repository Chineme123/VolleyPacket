interface StatCardProps {
  title: string;
  value: number | string;
  subtitle?: string;
  highlighted?: boolean;
}

export default function StatCard({ title, value, subtitle, highlighted = false }: StatCardProps) {
  return (
    <div
      className={`rounded-2xl p-5 flex flex-col justify-between min-h-[140px] transition-shadow ${
        highlighted
          ? "bg-green-800 text-white shadow-lg shadow-green-800/20"
          : "bg-white text-gray-900 shadow-sm border border-gray-100"
      }`}
    >
      <div className="flex items-center justify-between">
        <p className={`text-sm font-medium ${highlighted ? "text-green-200" : "text-gray-500"}`}>
          {title}
        </p>
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${highlighted ? "bg-green-700" : "bg-gray-100"}`}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={highlighted ? "white" : "#6b7280"} strokeWidth="2.5">
            <path d="M7 17l9.2-9.2M17 17V7H7" />
          </svg>
        </div>
      </div>
      <p className="text-4xl font-bold mt-2">{value}</p>
      {subtitle && (
        <p className={`text-xs mt-2 ${highlighted ? "text-green-300" : "text-gray-400"}`}>
          {subtitle}
        </p>
      )}
    </div>
  );
}

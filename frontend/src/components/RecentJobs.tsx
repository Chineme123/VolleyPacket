import { Job } from "@/lib/api";
import { statusBadge } from "@/lib/status";
import Link from "next/link";

interface RecentJobsProps {
  jobs: Job[];
}

export default function RecentJobs({ jobs }: RecentJobsProps) {
  if (jobs.length === 0) {
    return (
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Recent Jobs</h2>
        </div>
        <div className="flex flex-col items-center justify-center py-12 text-gray-400">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <rect x="3" y="3" width="18" height="18" rx="2" />
            <path d="M12 8v8M8 12h8" />
          </svg>
          <p className="mt-3 text-sm">No jobs yet</p>
          <p className="text-xs mt-1">Create your first job to get started</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Recent Jobs</h2>
        <Link href="/jobs" className="text-sm text-green-700 font-medium hover:text-green-800">
          View All
        </Link>
      </div>

      <div className="space-y-3">
        {jobs.slice(0, 5).map((job) => (
          <Link
            key={job.job_id}
            href={`/jobs/${job.job_id}`}
            className="flex items-center justify-between p-3 rounded-xl hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-green-50 flex items-center justify-center">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#047857" strokeWidth="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z" />
                  <path d="M14 2v6h6" />
                </svg>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">{job.candidate_file || "Untitled Job"}</p>
                <p className="text-xs text-gray-500">{job.candidate_count} candidates</p>
              </div>
            </div>
            <span className={`text-xs font-medium px-2.5 py-1 rounded-lg capitalize ${statusBadge(job.status)}`}>
              {job.status}
            </span>
          </Link>
        ))}
      </div>
    </div>
  );
}

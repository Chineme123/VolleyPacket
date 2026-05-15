"use client";

import { useState } from "react";
import { Template } from "@/lib/api";
import PdfPreviewModal from "./PdfPreviewModal";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface TemplateCardProps {
  template: Template;
}

export default function TemplateCard({ template }: TemplateCardProps) {
  const [showPreview, setShowPreview] = useState(false);

  return (
    <>
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden hover:shadow-md transition-shadow">
        <div className="h-40 bg-gradient-to-br from-green-50 to-green-100 flex items-center justify-center relative">
          <div className="w-20 h-28 bg-white rounded-lg shadow-md flex flex-col items-center justify-center gap-2 border border-gray-200">
            <div className="w-10 h-1.5 bg-green-700 rounded-full" />
            <div className="w-12 h-1 bg-gray-200 rounded-full" />
            <div className="w-12 h-1 bg-gray-200 rounded-full" />
            <div className="w-8 h-1 bg-gray-200 rounded-full" />
            <div className="w-10 h-3 bg-green-100 rounded mt-1" />
          </div>
        </div>

        <div className="p-4">
          <h3 className="font-semibold text-gray-900 text-sm">{template.name}</h3>
          <p className="text-xs text-gray-500 mt-1 line-clamp-2">{template.description}</p>
          <div className="flex items-center gap-2 mt-3">
            <button
              onClick={() => setShowPreview(true)}
              className="flex-1 text-center text-xs font-medium py-2 rounded-xl bg-green-50 text-green-800 hover:bg-green-100 transition-colors"
            >
              Preview
            </button>
            <button className="flex-1 text-center text-xs font-medium py-2 rounded-xl bg-green-800 text-white hover:bg-green-900 transition-colors">
              Use Template
            </button>
          </div>
        </div>
      </div>

      {showPreview && (
        <PdfPreviewModal
          url={`${API_BASE}/templates/${template.id}/preview`}
          title={template.name}
          onClose={() => setShowPreview(false)}
        />
      )}
    </>
  );
}

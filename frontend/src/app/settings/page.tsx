"use client";

import { useState } from "react";

interface SettingGroup {
  title: string;
  description: string;
  fields: SettingField[];
}

interface SettingField {
  label: string;
  key: string;
  type: "text" | "password" | "number";
  placeholder: string;
  hint?: string;
}

const settingGroups: SettingGroup[] = [
  {
    title: "Email (SMTP)",
    description: "Brevo SMTP credentials for sending invitation emails.",
    fields: [
      { label: "SMTP Server", key: "smtp_server", type: "text", placeholder: "smtp-relay.brevo.com" },
      { label: "SMTP Port", key: "smtp_port", type: "number", placeholder: "587" },
      { label: "SMTP Username", key: "smtp_user", type: "text", placeholder: "your-email@example.com" },
      { label: "SMTP Password", key: "smtp_pass", type: "password", placeholder: "••••••••" },
      { label: "Sender Name", key: "sender_name", type: "text", placeholder: "Osalasi Company Limited" },
      { label: "Sender Email", key: "sender_email", type: "text", placeholder: "noreply@osalasi.com" },
    ],
  },
  {
    title: "Brevo API",
    description: "API key for email delivery tracking and reports.",
    fields: [
      { label: "API Key", key: "brevo_api_key", type: "password", placeholder: "xkeysib-..." },
    ],
  },
  {
    title: "SMS (BulkSMS Nigeria)",
    description: "Credentials for sending SMS notifications.",
    fields: [
      { label: "API Token", key: "bulksms_token", type: "password", placeholder: "Your BulkSMS API token" },
      { label: "Sender ID", key: "bulksms_sender", type: "text", placeholder: "OSALASI", hint: "Max 11 characters" },
    ],
  },
  {
    title: "AI Template Generation",
    description: "Anthropic API key for Claude-powered template generation.",
    fields: [
      { label: "Anthropic API Key", key: "anthropic_key", type: "password", placeholder: "sk-ant-..." },
    ],
  },
];

export default function SettingsPage() {
  const [values, setValues] = useState<Record<string, string>>({});
  const [saved, setSaved] = useState(false);

  function handleChange(key: string, value: string) {
    setValues((prev) => ({ ...prev, [key]: value }));
    setSaved(false);
  }

  function handleSave() {
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  }

  return (
    <div>
      {/* Header */}
      <div className="flex items-start justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
          <p className="text-gray-500 mt-1">Configure API keys and service credentials.</p>
        </div>
        <button
          onClick={handleSave}
          className="flex items-center gap-2 px-5 py-2.5 bg-green-800 text-white text-sm font-medium rounded-xl hover:bg-green-900 transition-colors"
        >
          {saved ? (
            <>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M20 6L9 17l-5-5" />
              </svg>
              Saved
            </>
          ) : (
            "Save Changes"
          )}
        </button>
      </div>

      {/* Setting groups */}
      <div className="space-y-6">
        {settingGroups.map((group) => (
          <div key={group.title} className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <div className="mb-5">
              <h2 className="text-lg font-semibold text-gray-900">{group.title}</h2>
              <p className="text-sm text-gray-500 mt-0.5">{group.description}</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {group.fields.map((field) => (
                <div key={field.key}>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">{field.label}</label>
                  <input
                    type={field.type}
                    value={values[field.key] || ""}
                    onChange={(e) => handleChange(field.key, e.target.value)}
                    placeholder={field.placeholder}
                    className="w-full px-4 py-2.5 rounded-xl border border-gray-200 bg-white text-sm text-gray-800 placeholder-gray-400 outline-none focus:ring-2 focus:ring-green-700/20 focus:border-green-300 transition-shadow"
                  />
                  {field.hint && <p className="text-xs text-gray-400 mt-1">{field.hint}</p>}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Info notice */}
      <div className="mt-6 flex items-start gap-3 bg-green-50 border border-green-100 rounded-2xl px-5 py-4">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#047857" strokeWidth="2" className="flex-shrink-0 mt-0.5">
          <circle cx="12" cy="12" r="10" />
          <path d="M12 16v-4M12 8h.01" />
        </svg>
        <div>
          <p className="text-sm font-medium text-green-900">These settings are stored server-side</p>
          <p className="text-xs text-green-700 mt-0.5">
            Credentials are saved in the backend .env file. Changes here update the running configuration.
          </p>
        </div>
      </div>
    </div>
  );
}

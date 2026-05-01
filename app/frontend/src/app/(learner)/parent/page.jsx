"use client";

import React from "react";
import { useLearner } from "../../../context/LearnerContext";
import { Card } from "../../../components/ui/Card";
import { Button } from "../../../components/ui/Button";

export default function ParentPortalPage() {
  const { learner } = useLearner();

  return (
    <div className="max-w-4xl mx-auto p-4 md:p-8">
      <header className="mb-12">
        <h1 className="text-4xl font-['Baloo_2'] font-bold text-[var(--text)] mb-2">
          👨‍👩‍👧 Parent & Guardian Portal
        </h1>
        <p className="text-[var(--muted)] font-medium">
          Manage your learning privacy and share progress with your family.
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <Card className="p-8 border-none bg-white shadow-xl flex flex-col items-center text-center">
          <div className="w-20 h-20 bg-blue-50 text-blue-500 rounded-3xl flex items-center justify-center text-4xl mb-6 shadow-inner">
            🆔
          </div>
          <h2 className="text-2xl font-bold mb-4 text-gray-800">Your Learner ID</h2>
          <p className="text-gray-500 mb-8 text-sm leading-relaxed">
            Share this unique ID with your parent or guardian so they can see your progress reports and achievements.
          </p>
          <div className="w-full bg-gray-50 p-4 rounded-xl border-2 border-dashed border-gray-200 font-mono text-blue-600 font-bold break-all mb-8">
            {learner.learner_id}
          </div>
          <Button variant="secondary" className="w-full py-4" onClick={() => {
            navigator.clipboard.writeText(learner.learner_id);
            alert("ID copied to clipboard! 📋");
          }}>
            📋 Copy ID to Share
          </Button>
        </Card>

        <Card className="p-8 border-none bg-gradient-to-br from-green-500 to-emerald-600 text-white shadow-xl">
          <div className="w-20 h-20 bg-white/20 backdrop-blur-md rounded-3xl flex items-center justify-center text-4xl mb-6 border border-white/30">
            🔒
          </div>
          <h2 className="text-2xl font-bold mb-4">Privacy & POPIA</h2>
          <p className="text-emerald-50 mb-8 text-sm leading-relaxed">
            EduBoost SA is fully compliant with the Protection of Personal Information Act. Your data is encrypted and only shared with verified guardians.
          </p>
          <ul className="text-left space-y-3 mb-8">
            <li className="flex items-start gap-3 text-sm">
              <span className="bg-white/20 rounded-full p-1 text-[8px]">✓</span>
              <span>Encrypted personal data</span>
            </li>
            <li className="flex items-start gap-3 text-sm">
              <span className="bg-white/20 rounded-full p-1 text-[8px]">✓</span>
              <span>Request data deletion anytime</span>
            </li>
            <li className="flex items-start gap-3 text-sm">
              <span className="bg-white/20 rounded-full p-1 text-[8px]">✓</span>
              <span>Verified guardian linkage only</span>
            </li>
          </ul>
          <Button className="w-full bg-white text-green-600 hover:bg-green-50">
            Read Privacy Policy
          </Button>
        </Card>
      </div>

      <section className="mt-12">
        <Card className="p-8 border-none bg-blue-50/50 border border-blue-100 flex flex-col md:flex-row items-center gap-8">
          <div className="text-6xl">📊</div>
          <div className="flex-1 text-center md:text-left">
            <h3 className="text-xl font-bold text-blue-800 mb-2">Request a Progress Report</h3>
            <p className="text-blue-600 text-sm">
              Want to see a summary of your performance across all subjects? We can generate a PDF report for you to share.
            </p>
          </div>
          <Button className="whitespace-nowrap px-8">Generate PDF Report</Button>
        </Card>
      </section>
    </div>
  );
}

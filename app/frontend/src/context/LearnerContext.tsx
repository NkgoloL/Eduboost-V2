"use client";

import React, { createContext, useCallback, useContext, useEffect, useState } from "react";
import { LearnerService } from "../lib/api/services";
import type { ActiveLearner, GamificationProfile, MasteryEntry } from "../lib/api/types";

interface LearnerContextValue {
  learner: ActiveLearner | null;
  setLearner: React.Dispatch<React.SetStateAction<ActiveLearner | null>>;
  masteryData: Record<string, number>;
  setMasteryData: React.Dispatch<React.SetStateAction<Record<string, number>>>;
  gamification: GamificationProfile | null;
  setGamification: React.Dispatch<React.SetStateAction<GamificationProfile | null>>;
  refreshState: () => Promise<void>;
  badge: string | null;
  setBadge: React.Dispatch<React.SetStateAction<string | null>>;
  loading: boolean;
}

const LearnerContext = createContext<LearnerContextValue | undefined>(undefined);

export function LearnerProvider({ children }: { children: React.ReactNode }) {
  const [learner, setLearner] = useState<ActiveLearner | null>(null);
  const [masteryData, setMasteryData] = useState<Record<string, number>>({});
  const [gamification, setGamification] = useState<GamificationProfile | null>(null);
  const [badge, setBadge] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Load learner from localStorage on initial mount
  useEffect(() => {
    const saved = localStorage.getItem("eb_active_learner");
    if (saved) {
      try {
        setLearner(JSON.parse(saved));
      } catch (e) {
        console.error("Failed to parse saved learner", e);
      }
    }
    setLoading(false);
  }, []);

  const refreshState = useCallback(async () => {
    if (!learner?.learner_id) return;
    try {
      const [masteryRes, gamificationRes] = await Promise.all([
        LearnerService.getMastery(learner.learner_id),
        LearnerService.getGamificationProfile(learner.learner_id),
      ]);

      const masteryRows = (masteryRes as { mastery?: MasteryEntry[] } | null)?.mastery;
      if (masteryRows) {
        const newMastery: Record<string, number> = {};
        masteryRows.forEach((m) => {
          newMastery[m.subject_code] = Math.round(m.mastery_score * 100);
        });
        setMasteryData(newMastery);
      }
      setGamification((gamificationRes as GamificationProfile) || null);
    } catch (err) {
      console.error("Failed to refresh learner state:", err);
    }
  }, [learner?.learner_id]);

  // Save learner to localStorage whenever it changes
  useEffect(() => {
    if (learner) {
      localStorage.setItem("eb_active_learner", JSON.stringify(learner));
      refreshState();
    } else {
      localStorage.removeItem("eb_active_learner");
      setMasteryData({});
      setGamification(null);
    }
  }, [learner, refreshState]);

  return (
    <LearnerContext.Provider
      value={{
        learner,
        setLearner,
        masteryData,
        setMasteryData,
        gamification,
        setGamification,
        refreshState,
        badge,
        setBadge,
        loading,
      }}
    >
      {children}
    </LearnerContext.Provider>
  );
}

export function useLearner() {
  const context = useContext(LearnerContext);
  if (!context) {
    throw new Error("useLearner must be used within a LearnerProvider");
  }
  return context;
}

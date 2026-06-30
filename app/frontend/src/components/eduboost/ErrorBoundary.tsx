"use client";

import React from "react";
import { ErrorMessage } from "../ui/ErrorMessage";

interface State {
  hasError: boolean;
  message: string;
}

export class ErrorBoundary extends React.Component<{ children: React.ReactNode; title?: string }, State> {
  override state: State = { hasError: false, message: "" };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, message: error.message };
  }

  override componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error("Frontend route boundary caught an error", error, info.componentStack);
  }

  override render() {
    if (this.state.hasError) {
      return (
        <main id="main-content" className="min-h-screen flex items-center justify-center p-6">
          <ErrorMessage
            title={this.props.title || "This screen could not load."}
            message={this.state.message || "Refresh the page or return to the dashboard."}
            onRetry={() => this.setState({ hasError: false, message: "" })}
          />
        </main>
      );
    }
    return this.props.children;
  }
}

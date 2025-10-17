import { Component } from "react";

export class ErrorBoundary extends Component {
  state = { hasError: false, error: null };
  static getDerivedStateFromError(error) { return { hasError: true, error }; }
  componentDidCatch(error, info) { console.error("UI error:", error, info); }
  render() {
    if (this.state.hasError) return <div>Something went wrong rendering the message.</div>;
    return this.props.children;
  }
}

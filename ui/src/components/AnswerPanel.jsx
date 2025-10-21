import React, { useMemo } from "react";
import CitationLink from "./CitationLink";
import SourceCard from "./SourceCard";
import { extractSections, linkifyCitations } from "../lib/format";

export default function AnswerPanel({ content, references, answerId }) {
  const { insights, examples, takeaway } = useMemo(() => extractSections(content), [content]);
  const htmlInsights = useMemo(
    () => insights.map(line => linkifyCitations(line)), [insights]
  );
  const htmlExamples = useMemo(
    () => examples.map(line => linkifyCitations(line)), [examples]
  );
  const htmlTakeaway = useMemo(
    () => linkifyCitations(takeaway || ""), [takeaway]
  );


  return (
    <div className="answerCard">
      {htmlInsights.length > 0 && (
        <section>
          <h3>Insights</h3>
          <ul className="bullets">
            {htmlInsights.map((h, i) => (
              <li key={i}><CitationLink html={h} answerId={answerId} /></li>
            ))}
          </ul>
        </section>
      )}

      {htmlExamples.length > 0 && (
        <section>
          <h3>Examples</h3>
          <ul className="bullets">
            {htmlExamples.map((h, i) => (
              <li key={i}><CitationLink html={h} answerId={answerId} /></li>
            ))}
          </ul>
        </section>
      )}

      {htmlTakeaway && htmlTakeaway.trim() && (
        <section>
          <h3>Takeaway</h3>
          <ul className="bullets">
            <li><CitationLink html={htmlTakeaway} answerId={answerId} /></li>
          </ul>
        </section>
      )}


      {/* Fallback: show raw content if no structured sections found */}
      {htmlInsights.length === 0 && htmlExamples.length === 0 && !htmlTakeaway && (
        <section>
          <div className="bullets">
            <div><CitationLink html={linkifyCitations(content)} answerId={answerId} /></div>
          </div>
        </section>
      )}

      <div className="divider" />

      <section>
        <h4>Sources</h4>
        <div className="grid">
          {(references || []).map((r, i) => (
            <SourceCard key={r.url || r.title || i} refItem={r} index={i} />
          ))}
        </div>
      </section>
    </div>
  );
}

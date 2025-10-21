import React from "react";
export default function SkeletonAnswer() {
  return (
    <div className="answerCard skeleton">
      <div className="sk h24 w160" />
      <div className="sk h12 w560" />
      <div className="sk h12 w520" />
      <div className="sk h12 w480" />
      <div className="divider" />
      <div className="sk h20 w180" />
      <div className="grid">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="sourceCard skCard">
            <div className="sk h12 w120" />
            <div className="sk h12 w200" />
          </div>
        ))}
      </div>
    </div>
  );
}

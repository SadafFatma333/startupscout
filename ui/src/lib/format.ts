// Simple helpers for formatting the LLM answer and references
export type Sectioned = { insights: string[]; examples: string[]; takeaway: string };

export function extractSections(raw: string): Sectioned {
  if (!raw) return { insights: [], examples: [], takeaway: "" };
  
  const lines = raw.split('\n').map(l => l.trim()).filter(Boolean);
  const insights: string[] = [];
  const examples: string[] = [];
  let takeaway = "";
  
  let currentSection = "";
  
  for (const line of lines) {
    const lower = line.toLowerCase();
    
    // Detect section headers
    if (lower.includes('insights')) {
      currentSection = 'insights';
      continue;
    }
    if (lower.includes('examples')) {
      currentSection = 'examples';
      continue;
    }
    if (lower.includes('takeaway')) {
      currentSection = 'takeaway';
      // Extract takeaway content from the same line if it exists
      const takeawayContent = line.replace(/^.*?takeaway\s*:?\s*/i, '').trim();
      if (takeawayContent && !takeawayContent.toLowerCase().includes('takeaway')) {
        takeaway = takeawayContent.replace(/\*\*/g, '');
      }
      continue;
    }
    
    // Process content based on current section
    if (line.match(/^[-•]\s/)) {
      const content = line.replace(/^[-•]\s*/, '').trim();
      if (!content) continue;
      
      if (currentSection === 'examples') {
        examples.push(content);
      } else if (currentSection === 'takeaway') {
        takeaway += (takeaway ? " " : "") + content.replace(/\*\*/g, '');
      } else {
        insights.push(content);
      }
    } else if (currentSection === 'takeaway' && line) {
      // For takeaway section, also process non-bullet content
      takeaway += (takeaway ? " " : "") + line.replace(/\*\*/g, '');
    }
  }
  
  return { insights, examples, takeaway: takeaway.trim() };
}

export function linkifyCitations(text: string) {
  // Turn [1] into <a href="#ref-1">[1]</a>
  return text.replace(/\[(\d+)]/g, (_m, g1) => `<a class="cite" href="#ref-${g1}">[${g1}]</a>`);
}

export function byDomain(url?: string) {
  try { return url ? new URL(url).hostname.replace(/^www\./, "") : ""; } catch { return ""; }
}

export function formatSimilarity(v?: number) {
  if (v == null) return "";
  return `sim ${v.toFixed(2)}`;
}
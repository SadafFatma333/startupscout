// JS runtime version of normalize helpers (for Vercel build resolution)

export const toTagList = (tags) => {
  if (Array.isArray(tags)) return tags.filter(Boolean).map(String).map((s) => s.trim());
  if (typeof tags === "string") return tags.split(",").map((s) => s.trim()).filter(Boolean);
  return [];
};

export const normalizeAsk = (data = {}) => {
  const refsIn = Array.isArray(data.references) ? data.references : [];
  const refs = refsIn.map((r) => {
    if (Array.isArray(r)) {
      const [title] = r;
      return { title: String(title ?? "(untitled)"), url: null, source: null, stage: null, tags: [] };
    }
    return {
      id: r && r.id != null ? r.id : null,
      title: (r && r.title) || "(untitled)",
      url: (r && r.url) || null,
      source: (r && r.source) || null,
      stage: (r && r.stage) || null,
      tags: toTagList(r && r.tags),
      similarity:
        typeof (r && r.similarity) === "number"
          ? r.similarity
          : typeof (r && r.similarity) === "string"
          ? Number(r.similarity)
          : null,
    };
  });
  return {
    question: data.question || "",
    answer: data.answer || "",
    references: refs,
  };
};



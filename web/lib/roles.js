export const ROLE_DESCRIPTIONS = {
  ai_engineer: "Builds user-facing AI products with LLMs, APIs, and retrieval systems.",
  ml_engineer: "Ships classical and deep learning systems into production.",
  llm_engineer: "Focuses on prompting, RAG, evaluation, and model integration.",
  data_scientist: "Drives experimentation, modeling, and insight generation from data.",
  mlops_engineer: "Owns deployment, orchestration, monitoring, and reliability for ML systems.",
  data_engineer: "Builds data pipelines, transformations, and platform foundations.",
  analytics_engineer: "Turns warehouse data into trusted business-ready models and reporting layers.",
  computer_vision_engineer: "Develops perception systems for image and video workloads.",
  nlp_engineer: "Builds language understanding and generation systems.",
  applied_scientist: "Combines experimentation, research, and product modeling on high-value problems.",
  all: "Blended view of the tracked AI and data market."
};

export function humanizeRole(roleKey) {
  if (!roleKey) {
    return "Unknown Role";
  }
  return roleKey
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export function describeRole(roleKey) {
  return ROLE_DESCRIPTIONS[roleKey] || "Tracked role in the current AI hiring snapshot.";
}

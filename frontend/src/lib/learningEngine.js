export function generateLearningExperience(skillData) {
  const { skill, proficiency, importance, confidence } = skillData;

  let resources = {
    videos: [],
    docs: [],
    practice: []
  };

  let next_action = "";

  // 🎯 Resource selection
  if (proficiency < 0.4) {
    resources.videos.push(`${skill} beginner tutorial`);
    resources.practice.push(`Basic ${skill} exercises`);
    next_action = `Start learning ${skill} from basics`;
  } else if (proficiency < 0.7) {
    resources.docs.push(`${skill} official documentation`);
    resources.practice.push(`Intermediate ${skill} problems`);
    next_action = `Strengthen your ${skill} concepts`;
  } else {
    resources.practice.push(`Advanced ${skill} projects`);
    next_action = `Apply ${skill} in real-world projects`;
  }

  // 🎯 Always include practice
  if (resources.practice.length === 0) {
    resources.practice.push(`${skill} exercises`);
  }

  // 🎯 Explanation
  let mentor_explanation = `${skill} is important for your role.`;

  if (confidence < 0.4) {
    mentor_explanation += ` Your confidence is low, so focus more on this skill.`;
  }

  if (importance > 0.7) {
    mentor_explanation += ` This skill is highly required for your job.`;
  }

  return {
    skill,
    resources,
    next_action,
    mentor_explanation
  };
}
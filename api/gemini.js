import fs from 'fs';
import path from 'path';

// Load the roles_skills.json data
const rolesSkillsPath = path.join(__dirname, 'roles_skills.json');
const rolesSkills = JSON.parse(fs.readFileSync(rolesSkillsPath, 'utf8'));

export default async function handler(req, res) {
  if (req.method === 'POST') {
    try {
      const { student_profile } = req.body;
      const studentSkills = new Set(student_profile.skills.map(s => s.toLowerCase()));

      let recommendations = [];
      for (const role of rolesSkills) {
        const roleSkills = new Set(role.skills.map(s => s.toLowerCase()));
        const matchingSkills = [...studentSkills].filter(skill => roleSkills.has(skill));

        if (matchingSkills.length > 0) {
          recommendations.push({
            role_id: role.id,
            title: role.title,
            match_score: matchingSkills.length,
            known_skills: matchingSkills
          });
        }
      }

      recommendations.sort((a, b) => b.match_score - a.match_score);

      res.status(200).json({
        student_id: student_profile.student_id,
        recommendations: recommendations
      });
    } catch (error) {
      console.error("Error in API function:", error);
      res.status(500).json({ error: "Failed to process request." });
    }
  } else {
    res.status(405).json({ message: "Method Not Allowed" });
  }
}

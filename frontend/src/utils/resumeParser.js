/**
 * Resume Parser - Extracts structured sections from resume text
 */

const SECTION_KEYWORDS = {
  summary: ['summary', 'objective', 'profile', 'about'],
  experience: ['experience', 'work history', 'employment', 'work experience', 'professional experience'],
  projects: ['projects', 'key projects', 'selected projects'],
  skills: ['skills', 'technical skills', 'technologies', 'expertise', 'competencies'],
  education: ['education', 'academic', 'qualifications'],
  certifications: ['certifications', 'certificates', 'licenses']
};

const EMAIL_REGEX = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/;
const PHONE_REGEX = /(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}/;
const URL_REGEX = /(https?:\/\/[^\s]+)|(linkedin\.com\/[^\s]+)|(github\.com\/[^\s]+)/gi;

/**
 * Parse resume text into structured sections
 */
export function parseResume(text) {
  if (!text || typeof text !== 'string') {
    return createEmptyResume();
  }

  const lines = text.split('\n').map(l => l.trim()).filter(l => l);
  
  // Extract header (first 10 lines)
  const header = extractHeader(lines.slice(0, 10).join('\n'));
  
  // Find section boundaries
  const sections = extractSections(lines);
  
  return {
    header,
    sections,
    rawText: text
  };
}

/**
 * Extract header information (name, contact, links)
 */
function extractHeader(headerText) {
  const lines = headerText.split('\n').map(l => l.trim());
  
  const header = {
    name: '',
    email: '',
    phone: '',
    location: '',
    links: []
  };
  
  // First non-empty line is usually the name (if it's not too long)
  if (lines[0] && lines[0].length < 50 && !lines[0].includes('@')) {
    header.name = lines[0];
  }
  
  // Extract email
  const emailMatch = headerText.match(EMAIL_REGEX);
  if (emailMatch) header.email = emailMatch[0];
  
  // Extract phone
  const phoneMatch = headerText.match(PHONE_REGEX);
  if (phoneMatch) header.phone = phoneMatch[0];
  
  // Extract URLs
  const urlMatches = headerText.matchAll(URL_REGEX);
  for (const match of urlMatches) {
    header.links.push(match[0]);
  }
  
  // Try to find location (look for city, state patterns)
  const locationLine = lines.find(l => 
    /[A-Z][a-z]+,\s*[A-Z]{2}/.test(l) && 
    !l.includes('@') && 
    l.length < 50
  );
  if (locationLine) header.location = locationLine;
  
  return header;
}

/**
 * Extract sections from resume text
 */
function extractSections(lines) {
  const sections = [];
  let currentSection = null;
  let currentContent = [];
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const sectionType = detectSectionHeader(line);
    
    if (sectionType) {
      // Save previous section
      if (currentSection) {
        sections.push(parseSection(currentSection, currentContent));
      }
      
      // Start new section
      currentSection = sectionType;
      currentContent = [];
    } else if (currentSection) {
      currentContent.push(line);
    }
  }
  
  // Save last section
  if (currentSection) {
    sections.push(parseSection(currentSection, currentContent));
  }
  
  return sections;
}

/**
 * Detect if a line is a section header
 */
function detectSectionHeader(line) {
  const lower = line.toLowerCase();
  
  // Check if line is all caps or has special formatting
  const isHeader = line === line.toUpperCase() || 
                   line.startsWith('===') || 
                   line.startsWith('---') ||
                   /^[A-Z\s]+$/.test(line);
  
  if (!isHeader && line.length > 30) return null;
  
  for (const [type, keywords] of Object.entries(SECTION_KEYWORDS)) {
    if (keywords.some(kw => lower.includes(kw))) {
      return type;
    }
  }
  
  return null;
}

/**
 * Parse section content based on type
 */
function parseSection(type, contentLines) {
  const section = { type, content: '' };
  
  switch (type) {
    case 'summary':
      section.content = contentLines.join(' ');
      break;
      
    case 'experience':
      section.items = parseExperienceItems(contentLines);
      break;
      
    case 'projects':
      section.items = parseProjectItems(contentLines);
      break;
      
    case 'skills':
      section.groups = parseSkillsGroups(contentLines);
      break;
      
    case 'education':
      section.items = parseEducationItems(contentLines);
      break;
      
    default:
      section.content = contentLines.join('\n');
  }
  
  return section;
}

/**
 * Parse experience items
 */
function parseExperienceItems(lines) {
  const items = [];
  let current = null;
  
  for (const line of lines) {
    // Check if this is a new job entry (company/title line)
    if (isJobHeader(line)) {
      if (current) items.push(current);
      current = {
        title: '',
        company: '',
        dates: '',
        location: '',
        bullets: []
      };
      
      // Try to parse the header line
      const parsed = parseJobHeader(line);
      Object.assign(current, parsed);
    } else if (current) {
      // Check if it's a bullet point
      if (isBullet(line)) {
        current.bullets.push(cleanBullet(line));
      } else if (line.length < 100 && !current.dates && containsDateRange(line)) {
        current.dates = line;
      } else if (line.length < 80 && !current.location && looksLikeLocation(line)) {
        current.location = line;
      } else if (line.length < 150) {
        // Might be additional header info
        if (!current.title) current.title = line;
      }
    }
  }
  
  if (current) items.push(current);
  return items;
}

/**
 * Parse project items
 */
function parseProjectItems(lines) {
  const items = [];
  let current = null;
  
  for (const line of lines) {
    if (isProjectHeader(line)) {
      if (current) items.push(current);
      current = {
        name: line,
        bullets: []
      };
    } else if (current && isBullet(line)) {
      current.bullets.push(cleanBullet(line));
    }
  }
  
  if (current) items.push(current);
  return items;
}

/**
 * Parse skills groups
 */
function parseSkillsGroups(lines) {
  const groups = [];
  
  for (const line of lines) {
    // Check if line has a category (e.g., "Languages: Python, Java")
    if (line.includes(':')) {
      const [name, skillsStr] = line.split(':').map(s => s.trim());
      const skills = skillsStr.split(/[,;|]/).map(s => s.trim()).filter(s => s);
      groups.push({ name, skills });
    } else {
      // Treat as a single group
      const skills = line.split(/[,;|]/).map(s => s.trim()).filter(s => s);
      if (skills.length > 0) {
        groups.push({ name: 'Skills', skills });
      }
    }
  }
  
  return groups.length > 0 ? groups : [{ name: 'Skills', skills: [lines.join(', ')] }];
}

/**
 * Parse education items
 */
function parseEducationItems(lines) {
  const items = [];
  let current = null;
  
  for (const line of lines) {
    if (looksLikeSchoolName(line)) {
      if (current) items.push(current);
      current = {
        school: line,
        degree: '',
        dates: ''
      };
    } else if (current) {
      if (!current.degree && looksLikeDegree(line)) {
        current.degree = line;
      } else if (!current.dates && containsDateRange(line)) {
        current.dates = line;
      }
    }
  }
  
  if (current) items.push(current);
  return items;
}

// Helper functions

function isJobHeader(line) {
  // Look for patterns like "Company Name" or "Job Title at Company"
  return line.length < 100 && 
         (line.includes('|') || 
          /^[A-Z]/.test(line) && !isBullet(line));
}

function parseJobHeader(line) {
  const parts = line.split('|').map(s => s.trim());
  if (parts.length >= 2) {
    return {
      title: parts[0],
      company: parts[1],
      dates: parts[2] || '',
      location: parts[3] || ''
    };
  }
  
  // Try to extract from free-form text
  const atMatch = line.match(/(.+?)\s+at\s+(.+)/i);
  if (atMatch) {
    return { title: atMatch[1], company: atMatch[2] };
  }
  
  return { title: line };
}

function isProjectHeader(line) {
  return line.length < 80 && !isBullet(line) && /^[A-Z]/.test(line);
}

function isBullet(line) {
  return /^[\-•\*\+]\s+/.test(line) || /^\d+[\.\)]\s+/.test(line);
}

function cleanBullet(line) {
  return line.replace(/^[\-•\*\+]\s+/, '').replace(/^\d+[\.\)]\s+/, '').trim();
}

function containsDateRange(line) {
  return /\d{4}/.test(line) || 
         /\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)/i.test(line) ||
         /Present|Current/i.test(line);
}

function looksLikeLocation(line) {
  return /[A-Z][a-z]+,\s*[A-Z]{2}/.test(line) || 
         /[A-Z][a-z]+,\s*[A-Z][a-z]+/.test(line);
}

function looksLikeSchoolName(line) {
  return /University|College|Institute|School/i.test(line) || 
         (/^[A-Z]/.test(line) && line.length < 80);
}

function looksLikeDegree(line) {
  return /Bachelor|Master|PhD|B\.S\.|M\.S\.|B\.A\.|M\.A\.|Associate/i.test(line);
}

function createEmptyResume() {
  return {
    header: {
      name: '',
      email: '',
      phone: '',
      location: '',
      links: []
    },
    sections: [],
    rawText: ''
  };
}

/**
 * Generate suggestions for resume improvements
 */
export function generateBulletSuggestions(resumeData, analysisText) {
  // Parse suggestions from analysis text
  const suggestions = [];
  
  if (!analysisText) return suggestions;
  
  // Look for bullet point suggestions in the analysis
  const lines = analysisText.split('\n');
  let currentSuggestion = null;
  
  for (const line of lines) {
    const trimmed = line.trim();
    
    // Look for "Before:" or "Change:" patterns
    if (/^(Before|Original|Current):/i.test(trimmed)) {
      if (currentSuggestion) suggestions.push(currentSuggestion);
      currentSuggestion = {
        type: 'bullet',
        before: trimmed.split(':')[1]?.trim() || '',
        after: '',
        reason: ''
      };
    } else if (currentSuggestion && /^(After|Improved|Suggested):/i.test(trimmed)) {
      currentSuggestion.after = trimmed.split(':')[1]?.trim() || '';
    } else if (currentSuggestion && /^(Reason|Why|Impact):/i.test(trimmed)) {
      currentSuggestion.reason = trimmed.split(':')[1]?.trim() || '';
    }
  }
  
  if (currentSuggestion) suggestions.push(currentSuggestion);
  
  return suggestions;
}

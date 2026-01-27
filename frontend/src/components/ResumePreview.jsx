import { useState } from 'react';

/**
 * ResumePreview - Renders resume in a professional template layout
 */
export default function ResumePreview({ resumeData, onBulletClick }) {
  const [selectedBullet, setSelectedBullet] = useState(null);
  
  if (!resumeData || !resumeData.sections) {
    return (
      <div style={styles.container}>
        <div style={styles.emptyState}>
          <p style={{ color: '#999', fontSize: 14 }}>Upload a resume to see preview</p>
        </div>
      </div>
    );
  }
  
  const { header, sections } = resumeData;
  
  return (
    <div style={styles.container}>
      <div style={styles.page}>
        {/* Header */}
        <header style={styles.header}>
          {header.name && <h1 style={styles.name}>{header.name}</h1>}
          <div style={styles.contactRow}>
            {header.email && <span style={styles.contactItem}>{header.email}</span>}
            {header.phone && <span style={styles.contactItem}>{header.phone}</span>}
            {header.location && <span style={styles.contactItem}>{header.location}</span>}
          </div>
          {header.links && header.links.length > 0 && (
            <div style={styles.linksRow}>
              {header.links.map((link, idx) => (
                <a 
                  key={idx} 
                  href={link.startsWith('http') ? link : `https://${link}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={styles.link}
                >
                  {link}
                </a>
              ))}
            </div>
          )}
        </header>
        
        {/* Sections */}
        <div style={styles.sections}>
          {sections.map((section, idx) => (
            <Section 
              key={idx} 
              section={section} 
              selectedBullet={selectedBullet}
              onBulletClick={(bulletId) => {
                setSelectedBullet(bulletId);
                if (onBulletClick) onBulletClick(bulletId);
              }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

function Section({ section, selectedBullet, onBulletClick }) {
  const sectionTitles = {
    summary: 'Professional Summary',
    experience: 'Experience',
    projects: 'Projects',
    skills: 'Skills',
    education: 'Education',
    certifications: 'Certifications'
  };
  
  return (
    <section style={styles.section}>
      <h2 style={styles.sectionTitle}>
        {sectionTitles[section.type] || section.type.toUpperCase()}
      </h2>
      <div style={styles.sectionContent}>
        {section.type === 'summary' && <p style={styles.summaryText}>{section.content}</p>}
        
        {section.type === 'experience' && section.items && (
          <div>
            {section.items.map((exp, idx) => (
              <ExperienceItem 
                key={idx} 
                item={exp} 
                itemId={`exp-${idx}`}
                selectedBullet={selectedBullet}
                onBulletClick={onBulletClick}
              />
            ))}
          </div>
        )}
        
        {section.type === 'projects' && section.items && (
          <div>
            {section.items.map((proj, idx) => (
              <ProjectItem 
                key={idx} 
                item={proj} 
                itemId={`proj-${idx}`}
                selectedBullet={selectedBullet}
                onBulletClick={onBulletClick}
              />
            ))}
          </div>
        )}
        
        {section.type === 'skills' && section.groups && (
          <div style={styles.skillsContainer}>
            {section.groups.map((group, idx) => (
              <div key={idx} style={styles.skillGroup}>
                {group.name && group.name !== 'Skills' && (
                  <strong style={styles.skillGroupName}>{group.name}: </strong>
                )}
                <span style={styles.skillsList}>{group.skills.join(', ')}</span>
              </div>
            ))}
          </div>
        )}
        
        {section.type === 'education' && section.items && (
          <div>
            {section.items.map((edu, idx) => (
              <EducationItem key={idx} item={edu} />
            ))}
          </div>
        )}
        
        {section.content && section.type !== 'summary' && (
          <p style={styles.plainContent}>{section.content}</p>
        )}
      </div>
    </section>
  );
}

function ExperienceItem({ item, itemId, selectedBullet, onBulletClick }) {
  return (
    <div style={styles.experienceItem}>
      <div style={styles.experienceHeader}>
        <div>
          <div style={styles.jobTitle}>{item.title}</div>
          <div style={styles.company}>{item.company}</div>
        </div>
        <div style={styles.dates}>{item.dates}</div>
      </div>
      {item.location && <div style={styles.location}>{item.location}</div>}
      {item.bullets && item.bullets.length > 0 && (
        <ul style={styles.bulletList}>
          {item.bullets.map((bullet, idx) => {
            const bulletId = `${itemId}-${idx}`;
            const isSelected = selectedBullet === bulletId;
            
            return (
              <li 
                key={idx} 
                style={{
                  ...styles.bullet,
                  background: isSelected ? '#fff3cd' : 'transparent',
                  cursor: 'pointer',
                  padding: '4px 8px',
                  margin: '4px 0',
                  borderRadius: 4,
                  transition: 'background 0.2s'
                }}
                onClick={() => onBulletClick(bulletId)}
                onMouseEnter={(e) => {
                  if (!isSelected) e.currentTarget.style.background = '#f8f9fa';
                }}
                onMouseLeave={(e) => {
                  if (!isSelected) e.currentTarget.style.background = 'transparent';
                }}
              >
                {bullet}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

function ProjectItem({ item, itemId, selectedBullet, onBulletClick }) {
  return (
    <div style={styles.projectItem}>
      <div style={styles.projectName}>{item.name}</div>
      {item.bullets && item.bullets.length > 0 && (
        <ul style={styles.bulletList}>
          {item.bullets.map((bullet, idx) => {
            const bulletId = `${itemId}-${idx}`;
            const isSelected = selectedBullet === bulletId;
            
            return (
              <li 
                key={idx} 
                style={{
                  ...styles.bullet,
                  background: isSelected ? '#fff3cd' : 'transparent',
                  cursor: 'pointer',
                  padding: '4px 8px',
                  margin: '4px 0',
                  borderRadius: 4,
                  transition: 'background 0.2s'
                }}
                onClick={() => onBulletClick(bulletId)}
                onMouseEnter={(e) => {
                  if (!isSelected) e.currentTarget.style.background = '#f8f9fa';
                }}
                onMouseLeave={(e) => {
                  if (!isSelected) e.currentTarget.style.background = 'transparent';
                }}
              >
                {bullet}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

function EducationItem({ item }) {
  return (
    <div style={styles.educationItem}>
      <div style={styles.educationHeader}>
        <div>
          <div style={styles.schoolName}>{item.school}</div>
          {item.degree && <div style={styles.degree}>{item.degree}</div>}
        </div>
        {item.dates && <div style={styles.dates}>{item.dates}</div>}
      </div>
    </div>
  );
}

const styles = {
  container: {
    height: '100%',
    overflow: 'auto',
    background: '#e9ecef',
    padding: 16
  },
  emptyState: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
    minHeight: 400
  },
  page: {
    maxWidth: 850,
    margin: '0 auto',
    background: 'white',
    padding: '48px 56px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
    borderRadius: 8,
    minHeight: '11in',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
  },
  header: {
    borderBottom: '2px solid #333',
    paddingBottom: 16,
    marginBottom: 24
  },
  name: {
    fontSize: 32,
    fontWeight: 700,
    margin: 0,
    marginBottom: 8,
    color: '#1a1a1a'
  },
  contactRow: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: 16,
    fontSize: 13,
    color: '#555',
    marginBottom: 6
  },
  contactItem: {
    display: 'flex',
    alignItems: 'center'
  },
  linksRow: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: 16,
    fontSize: 13,
    marginTop: 6
  },
  link: {
    color: '#0066cc',
    textDecoration: 'none'
  },
  sections: {
    display: 'flex',
    flexDirection: 'column',
    gap: 20
  },
  section: {
    marginBottom: 8
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 700,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    color: '#1a1a1a',
    borderBottom: '1px solid #ddd',
    paddingBottom: 6,
    marginBottom: 12,
    marginTop: 0
  },
  sectionContent: {
    fontSize: 14,
    lineHeight: 1.6,
    color: '#333'
  },
  summaryText: {
    margin: 0,
    textAlign: 'justify'
  },
  experienceItem: {
    marginBottom: 16
  },
  experienceHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 4
  },
  jobTitle: {
    fontSize: 15,
    fontWeight: 600,
    color: '#1a1a1a'
  },
  company: {
    fontSize: 14,
    fontWeight: 500,
    color: '#555',
    marginTop: 2
  },
  dates: {
    fontSize: 13,
    color: '#777',
    fontStyle: 'italic',
    whiteSpace: 'nowrap'
  },
  location: {
    fontSize: 13,
    color: '#777',
    marginBottom: 8
  },
  bulletList: {
    margin: '8px 0',
    paddingLeft: 20
  },
  bullet: {
    marginBottom: 6,
    lineHeight: 1.5
  },
  projectItem: {
    marginBottom: 14
  },
  projectName: {
    fontSize: 15,
    fontWeight: 600,
    color: '#1a1a1a',
    marginBottom: 6
  },
  skillsContainer: {
    display: 'flex',
    flexDirection: 'column',
    gap: 8
  },
  skillGroup: {
    fontSize: 14,
    lineHeight: 1.6
  },
  skillGroupName: {
    color: '#555'
  },
  skillsList: {
    color: '#333'
  },
  educationItem: {
    marginBottom: 12
  },
  educationHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start'
  },
  schoolName: {
    fontSize: 15,
    fontWeight: 600,
    color: '#1a1a1a'
  },
  degree: {
    fontSize: 14,
    color: '#555',
    marginTop: 2
  },
  plainContent: {
    margin: 0,
    whiteSpace: 'pre-wrap'
  }
};

"""
Professional Resume PDF Generator
Generates beautifully formatted resume PDFs from structured data.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from io import BytesIO


def generate_professional_resume_pdf(resume_data):
    """
    Generate a professional resume PDF from structured data.
    
    Args:
        resume_data: dict with structure:
            {
                "header": {
                    "name": str,
                    "email": str,
                    "phone": str,
                    "location": str,
                    "links": [str]
                },
                "sections": [
                    {
                        "type": "summary"|"experience"|"projects"|"skills"|"education"|"certifications",
                        "content": str (for summary),
                        "items": [...] (for experience/projects/education),
                        "groups": [...] (for skills)
                    }
                ]
            }
    
    Returns:
        BytesIO: PDF file buffer
    """
    buffer = BytesIO()
    
    # Create PDF with margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    name_style = ParagraphStyle(
        'CustomName',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    contact_style = ParagraphStyle(
        'Contact',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#555555'),
        alignment=TA_CENTER,
        spaceAfter=4
    )
    
    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=8,
        spaceBefore=12,
        fontName='Helvetica-Bold',
        borderWidth=1,
        borderColor=colors.HexColor('#dddddd'),
        borderPadding=4,
        borderRadius=0,
        leftIndent=0,
        textTransform='uppercase',
        letterSpacing=0.5
    )
    
    job_title_style = ParagraphStyle(
        'JobTitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#1a1a1a'),
        fontName='Helvetica-Bold',
        spaceAfter=2
    )
    
    company_style = ParagraphStyle(
        'Company',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#555555'),
        fontName='Helvetica',
        spaceAfter=2
    )
    
    date_style = ParagraphStyle(
        'Date',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#777777'),
        fontName='Helvetica-Oblique',
        spaceAfter=4
    )
    
    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        leftIndent=20,
        spaceAfter=4,
        leading=14
    )
    
    summary_style = ParagraphStyle(
        'Summary',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        alignment=TA_LEFT,
        leading=14,
        spaceAfter=8
    )
    
    # Build document
    story = []
    
    # Header
    header = resume_data.get('header', {})
    
    # Name
    if header.get('name'):
        story.append(Paragraph(header['name'], name_style))
        story.append(Spacer(1, 0.1*inch))
    
    # Contact info
    contact_parts = []
    if header.get('email'):
        contact_parts.append(header['email'])
    if header.get('phone'):
        contact_parts.append(header['phone'])
    if header.get('location'):
        contact_parts.append(header['location'])
    
    if contact_parts:
        contact_text = ' • '.join(contact_parts)
        story.append(Paragraph(contact_text, contact_style))
    
    # Links
    if header.get('links') and len(header['links']) > 0:
        links_text = ' • '.join([f'<link href="{link}">{link}</link>' for link in header['links']])
        story.append(Paragraph(links_text, contact_style))
    
    story.append(Spacer(1, 0.15*inch))
    
    # Add horizontal line under header
    story.append(Table([['']], colWidths=[6.5*inch], style=[
        ('LINEABOVE', (0,0), (-1,-1), 2, colors.HexColor('#333333')),
    ]))
    story.append(Spacer(1, 0.15*inch))
    
    # Sections
    sections = resume_data.get('sections', [])
    
    for section in sections:
        section_type = section.get('type', 'unknown')
        
        # Section title
        section_titles = {
            'summary': 'PROFESSIONAL SUMMARY',
            'experience': 'EXPERIENCE',
            'projects': 'PROJECTS',
            'skills': 'SKILLS',
            'education': 'EDUCATION',
            'certifications': 'CERTIFICATIONS'
        }
        title_text = section_titles.get(section_type, section_type.upper())
        story.append(Paragraph(title_text, section_title_style))
        story.append(Spacer(1, 0.05*inch))
        
        # Summary section
        if section_type == 'summary' and section.get('content'):
            story.append(Paragraph(section['content'], summary_style))
            story.append(Spacer(1, 0.1*inch))
        
        # Experience section
        elif section_type == 'experience' and section.get('items'):
            for exp in section['items']:
                # Job title and company in table for alignment
                title_cell = Paragraph(exp.get('title', ''), job_title_style)
                dates_cell = Paragraph(exp.get('dates', ''), date_style)
                
                story.append(Table(
                    [[title_cell, dates_cell]],
                    colWidths=[4.5*inch, 2*inch],
                    style=[
                        ('VALIGN', (0,0), (-1,-1), 'TOP'),
                        ('ALIGN', (1,0), (1,0), 'RIGHT'),
                    ]
                ))
                
                if exp.get('company'):
                    story.append(Paragraph(exp['company'], company_style))
                
                if exp.get('location'):
                    story.append(Paragraph(exp['location'], date_style))
                
                # Bullets
                if exp.get('bullets'):
                    for bullet in exp['bullets']:
                        bullet_text = f'• {bullet}'
                        story.append(Paragraph(bullet_text, bullet_style))
                
                story.append(Spacer(1, 0.12*inch))
        
        # Projects section
        elif section_type == 'projects' and section.get('items'):
            for proj in section['items']:
                story.append(Paragraph(f"<b>{proj.get('name', 'Project')}</b>", job_title_style))
                
                if proj.get('bullets'):
                    for bullet in proj['bullets']:
                        bullet_text = f'• {bullet}'
                        story.append(Paragraph(bullet_text, bullet_style))
                
                story.append(Spacer(1, 0.12*inch))
        
        # Skills section
        elif section_type == 'skills' and section.get('groups'):
            for group in section['groups']:
                if group.get('name') and group['name'] != 'Skills':
                    skill_line = f"<b>{group['name']}:</b> {', '.join(group.get('skills', []))}"
                else:
                    skill_line = ', '.join(group.get('skills', []))
                story.append(Paragraph(skill_line, summary_style))
            
            story.append(Spacer(1, 0.1*inch))
        
        # Education section
        elif section_type == 'education' and section.get('items'):
            for edu in section['items']:
                # School and dates
                school_cell = Paragraph(f"<b>{edu.get('school', '')}</b>", job_title_style)
                dates_cell = Paragraph(edu.get('dates', ''), date_style)
                
                story.append(Table(
                    [[school_cell, dates_cell]],
                    colWidths=[4.5*inch, 2*inch],
                    style=[
                        ('VALIGN', (0,0), (-1,-1), 'TOP'),
                        ('ALIGN', (1,0), (1,0), 'RIGHT'),
                    ]
                ))
                
                if edu.get('degree'):
                    story.append(Paragraph(edu['degree'], company_style))
                
                story.append(Spacer(1, 0.12*inch))
        
        # Generic content section
        elif section.get('content') and section_type != 'summary':
            story.append(Paragraph(section['content'], summary_style))
            story.append(Spacer(1, 0.1*inch))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    
    return buffer


def generate_simple_pdf_from_text(title, text_content):
    """
    Legacy function: Generate simple text-based PDF.
    Kept for backward compatibility.
    """
    buffer = BytesIO()
    
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#1a1a1a')
    )
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Content
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        spaceAfter=6
    )
    
    for paragraph in text_content.split('\n\n'):
        if paragraph.strip():
            story.append(Paragraph(paragraph.replace('\n', '<br/>'), normal_style))
            story.append(Spacer(1, 0.1*inch))
    
    doc.build(story)
    buffer.seek(0)
    
    return buffer

import {
  AlignmentType,
  Document,
  HeadingLevel,
  Packer,
  Paragraph,
  TextRun,
} from 'docx'
import { saveAs } from 'file-saver'

function splitLines(text) {
  return (text || '')
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)
}

function sectionHeading(title) {
  return new Paragraph({
    children: [
      new TextRun({
        text: title,
        bold: true,
        size: 26,
      }),
    ],
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 280, after: 120 },
  })
}

function toParagraphs(text, { bullet = false } = {}) {
  const lines = splitLines(text)

  if (lines.length === 0) {
    return [
      new Paragraph({
        children: [new TextRun({ text: 'N/A', italics: true })],
        spacing: { after: 140 },
      }),
    ]
  }

  return lines.map((line) => {
    if (bullet) {
      const cleaned = line.replace(/^[-*•]\s*/, '')
      return new Paragraph({
        text: cleaned,
        bullet: { level: 0 },
        spacing: { after: 80 },
      })
    }

    return new Paragraph({
      text: line,
      spacing: { after: 120 },
    })
  })
}

function toSkillBullets(text) {
  const raw = text || ''
  const candidates = raw.includes(',') ? raw.split(',') : raw.split('\n')
  const skills = candidates
    .map((value) => value.trim())
    .filter(Boolean)

  if (skills.length === 0) {
    return toParagraphs('', { bullet: true })
  }

  return skills.map((skill) =>
    new Paragraph({
      text: skill,
      bullet: { level: 0 },
      spacing: { after: 80 },
    })
  )
}

export async function exportToDocx(sections, filename = 'resume.docx') {
  const safeSections = sections || {}

  const doc = new Document({
    sections: [
      {
        properties: {},
        children: [
          new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [
              new TextRun({
                text: 'RESUME',
                bold: true,
                size: 32,
              }),
            ],
            spacing: { after: 220 },
          }),

          sectionHeading('Summary'),
          ...toParagraphs(safeSections.summary?.original || ''),

          sectionHeading('Experience'),
          ...toParagraphs(safeSections.experience?.original || ''),

          sectionHeading('Projects'),
          ...toParagraphs(safeSections.projects?.original || '', { bullet: true }),

          sectionHeading('Skills'),
          ...toSkillBullets(safeSections.skills?.original || ''),
        ],
      },
    ],
  })

  const blob = await Packer.toBlob(doc)
  saveAs(blob, filename)
}

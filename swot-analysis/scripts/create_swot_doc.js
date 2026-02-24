#!/usr/bin/env node

/**
 * SWOT分析报告Word文档生成脚本（完整版 - 包含战略分析）
 *
 * 使用方法:
 *   node create_swot_doc.js '{"companyName":"企业名称","date":"2026-02-24","strengths":[...],"weaknesses":[...],"opportunities":[...],"threats":[...],"strategicAnalysis":{...}}'
 */

const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        AlignmentType, BorderStyle, WidthType, ShadingType, VerticalAlign } = require('docx');
const fs = require('fs');
const path = require('path');

// 颜色定义
const COLORS = {
  STRENGTH: 'FBE4D5',     // 浅橙色 - 优势
  WEAKNESS: 'DEEAF6',     // 浅蓝色 - 劣势
  OPPORTUNITY: 'E2EFDA',  // 浅绿色 - 机遇
  THREAT: 'F2F2F2'        // 浅灰色 - 挑战
};

// 字体定义
const FONTS = {
  CHAPTER_TITLE: '黑体',      // 章标题
  SECTION_TITLE: '楷体_GB2312', // 节标题
  BODY: '仿宋_GB2312',        // 正文
  TABLE: '新宋体'             // 表格
};

// 边框样式
const BORDER_OUTER = { style: BorderStyle.SINGLE, size: 12, color: '000000' };
const BORDER_INNER = { style: BorderStyle.SINGLE, size: 6, color: '000000' };

/**
 * 创建章标题段落
 */
function createChapterTitle(text) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: {
      beforeLines: 50,
      before: 156,
      afterLines: 50,
      after: 156,
      line: 560,
      lineRule: 'exact'
    },
    children: [
      new TextRun({
        text: text,
        font: {
          ascii: FONTS.CHAPTER_TITLE,
          eastAsia: FONTS.CHAPTER_TITLE,
          hAnsi: FONTS.CHAPTER_TITLE
        },
        size: 32,
        bold: true
      })
    ]
  });
}

/**
 * 创建节标题段落
 */
function createSectionTitle(text) {
  return new Paragraph({
    spacing: {
      line: 560,
      lineRule: 'exact'
    },
    indent: {
      firstLineChars: 200,
      firstLine: 643
    },
    children: [
      new TextRun({
        text: text,
        font: {
          ascii: FONTS.SECTION_TITLE,
          eastAsia: FONTS.SECTION_TITLE,
          hAnsi: FONTS.SECTION_TITLE
        },
        size: 32,
        bold: true
      })
    ]
  });
}

/**
 * 创建小节标题（用于第五、六节）
 */
function createSubSectionTitle(text) {
  return new Paragraph({
    spacing: {
      line: 360,
      lineRule: 'exact'
    },
    indent: {
      firstLineChars: 200,
      firstLine: 428
    },
    children: [
      new TextRun({
        text: text,
        font: {
          ascii: FONTS.BODY,
          eastAsia: FONTS.BODY,
          hAnsi: '宋体'
        },
        size: 30,
        bold: true
      })
    ]
  });
}

/**
 * 创建正文段落
 */
function createBodyParagraph(text, boldTitle = true) {
  const match = text.match(/^([A-Z]\d+-.+?[。：:])(.*)$/s);
  let titleText = '';
  let bodyText = text;

  if (match) {
    titleText = match[1];
    bodyText = match[2];
  }

  const children = [];

  if (titleText && boldTitle) {
    children.push(new TextRun({
      text: titleText,
      font: {
        ascii: FONTS.BODY,
        eastAsia: FONTS.BODY,
        hAnsi: '宋体'
      },
      size: 32,
      bold: true
    }));
  }

  children.push(new TextRun({
    text: bodyText,
    font: {
      ascii: FONTS.BODY,
      eastAsia: FONTS.BODY,
      hAnsi: '宋体'
    },
    size: 32
  }));

  return new Paragraph({
    spacing: {
      line: 560,
      lineRule: 'exact'
    },
    indent: {
      firstLineChars: 200,
      firstLine: 643
    },
    children: children
  });
}

/**
 * 创建战略分析正文段落（无编号）
 */
function createStrategicParagraph(text) {
  return new Paragraph({
    spacing: {
      line: 480,
      lineRule: 'exact'
    },
    indent: {
      firstLineChars: 200,
      firstLine: 643
    },
    children: [
      new TextRun({
        text: text,
        font: {
          ascii: FONTS.BODY,
          eastAsia: FONTS.BODY,
          hAnsi: '宋体'
        },
        size: 32
      })
    ]
  });
}

/**
 * 创建表格标题段落
 */
function createTableCaption(text) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: {
      line: 560,
      lineRule: 'exact'
    },
    children: [
      new TextRun({
        text: text,
        font: {
          ascii: '宋体',
          eastAsia: '宋体',
          hAnsi: '宋体'
        },
        size: 28,
        color: '000000'
      })
    ]
  });
}

/**
 * 创建表格单元格
 */
function createTableCell(text, fillColor, isHeader = false) {
  const borders = {
    top: BORDER_INNER,
    bottom: BORDER_INNER,
    left: BORDER_INNER,
    right: BORDER_INNER
  };

  return new TableCell({
    borders: borders,
    shading: {
      fill: fillColor,
      type: ShadingType.CLEAR
    },
    verticalAlign: VerticalAlign.CENTER,
    margins: {
      top: 80,
      bottom: 80,
      left: 120,
      right: 120
    },
    children: [
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [
          new TextRun({
            text: text,
            font: {
              ascii: FONTS.TABLE,
              eastAsia: FONTS.TABLE,
              hAnsi: FONTS.TABLE
            },
            size: 22,
            bold: isHeader,
            color: '000000'
          })
        ]
      })
    ]
  });
}

/**
 * 创建内容单元格（多行内容）
 */
function createContentCell(items, fillColor) {
  const borders = {
    top: BORDER_INNER,
    bottom: BORDER_INNER,
    left: BORDER_INNER,
    right: BORDER_INNER
  };

  const paragraphs = items.map(item => {
    return new Paragraph({
      children: [
        new TextRun({
          text: item,
          font: {
            ascii: FONTS.TABLE,
            eastAsia: FONTS.TABLE,
            hAnsi: FONTS.TABLE
          },
          size: 22,
          color: '000000'
        })
      ]
    });
  });

  return new TableCell({
    borders: borders,
    shading: {
      fill: fillColor,
      type: ShadingType.CLEAR
    },
    verticalAlign: VerticalAlign.TOP,
    margins: {
      top: 80,
      bottom: 80,
      left: 120,
      right: 120
    },
    children: paragraphs
  });
}

/**
 * 创建SWOT矩阵表格
 */
function createSWOTMatrix(strengths, weaknesses, opportunities, threats) {
  const extractShortTitles = (items) => {
    return items.map(item => {
      const match = item.match(/^([A-Z]\d+-.+?)(?=[。：:]|[\s])/);
      return match ? match[1] : item.substring(0, 30);
    });
  };

  const sTitles = extractShortTitles(strengths);
  const wTitles = extractShortTitles(weaknesses);
  const oTitles = extractShortTitles(opportunities);
  const tTitles = extractShortTitles(threats);

  return new Table({
    width: { size: 8356, type: WidthType.DXA },
    columnWidths: [4178, 4178],
    rows: [
      new TableRow({
        children: [
          createTableCell('优势 - S', COLORS.STRENGTH, true),
          createTableCell('劣势 - W', COLORS.WEAKNESS, true)
        ]
      }),
      new TableRow({
        children: [
          createContentCell(sTitles, 'FFFFFF'),
          createContentCell(wTitles, 'FFFFFF')
        ]
      }),
      new TableRow({
        children: [
          createTableCell('机遇 - O', COLORS.OPPORTUNITY, true),
          createTableCell('挑战 - T', COLORS.THREAT, true)
        ]
      }),
      new TableRow({
        children: [
          createContentCell(oTitles, 'FFFFFF'),
          createContentCell(tTitles, 'FFFFFF')
        ]
      })
    ]
  });
}

/**
 * 创建战略开发矩阵表格（第六节）
 */
function createStrategyMatrix(strategicAnalysis) {
  const { wo = [], so = [], st = [], wt = [] } = strategicAnalysis || {};

  const createStrategyCell = (strategies, bgColor) => {
    const items = strategies.map(s => `• ${s}`);
    return createContentCell(items.length > 0 ? items : ['（暂无）'], bgColor);
  };

  return new Table({
    width: { size: 8356, type: WidthType.DXA },
    columnWidths: [4178, 4178],
    rows: [
      new TableRow({
        children: [
          createTableCell('WO战略（扭转型）', 'FFE699', true),
          createTableCell('SO战略（增长型）', 'C6E0B4', true)
        ]
      }),
      new TableRow({
        children: [
          createStrategyCell(wo, 'FFFFFF'),
          createStrategyCell(so, 'FFFFFF')
        ]
      }),
      new TableRow({
        children: [
          createTableCell('ST战略（多元化）', 'BDD7EE', true),
          createTableCell('WT战略（防御型）', 'F2F2F2', true)
        ]
      }),
      new TableRow({
        children: [
          createStrategyCell(st, 'FFFFFF'),
          createStrategyCell(wt, 'FFFFFF')
        ]
      })
    ]
  });
}

/**
 * 创建SWOT分析文档（完整版）
 */
async function createSWOTDocument(data) {
  const {
    companyName = '企业',
    date = new Date().toISOString().split('T')[0],
    strengths = [],
    weaknesses = [],
    opportunities = [],
    threats = [],
    strategicAnalysis = {}
  } = data;

  const children = [];

  // 第一章标题
  children.push(createChapterTitle('第一章 SWOT分析'));

  // 第一节：核心优势分析
  children.push(createSectionTitle('第一节 核心优势分析'));
  strengths.forEach(item => {
    children.push(createBodyParagraph(item));
  });

  // 第二节：核心劣势分析
  children.push(createSectionTitle('第二节 核心劣势分析'));
  weaknesses.forEach(item => {
    children.push(createBodyParagraph(item));
  });

  // 第三节：核心机遇分析
  children.push(createSectionTitle('第三节 核心机遇分析'));
  opportunities.forEach(item => {
    children.push(createBodyParagraph(item));
  });

  // 第四节：核心挑战分析
  children.push(createSectionTitle('第四节 核心挑战分析'));
  threats.forEach(item => {
    children.push(createBodyParagraph(item));
  });

  // 第五节：战略定位矩阵分析
  if (strategicAnalysis.strategicDiagnosis) {
    children.push(createSectionTitle('第五节 战略定位矩阵分析'));
    children.push(createSubSectionTitle('1. 战略定位诊断'));
    children.push(createStrategicParagraph(strategicAnalysis.strategicDiagnosis));

    if (strategicAnalysis.strategicConclusion) {
      children.push(createSubSectionTitle('2. 战略定位结论'));
      children.push(createStrategicParagraph(strategicAnalysis.strategicConclusion));
    }
  }

  // 第六节：战略开发矩阵分析
  if (strategicAnalysis.wo || strategicAnalysis.so || strategicAnalysis.st || strategicAnalysis.wt) {
    children.push(createSectionTitle('第六节 战略开发矩阵分析'));

    if (strategicAnalysis.wo && strategicAnalysis.wo.length > 0) {
      children.push(createSubSectionTitle('1. 主导战略（WO-扭转型）'));
      strategicAnalysis.wo.forEach(item => {
        children.push(createStrategicParagraph(item));
      });
    }

    if (strategicAnalysis.so && strategicAnalysis.so.length > 0) {
      children.push(createSubSectionTitle('2. 辅助战略（SO-增长型）'));
      strategicAnalysis.so.forEach(item => {
        children.push(createStrategicParagraph(item));
      });
    }

    if (strategicAnalysis.st && strategicAnalysis.st.length > 0) {
      children.push(createSubSectionTitle('3. 保障战略（ST-多元化）'));
      strategicAnalysis.st.forEach(item => {
        children.push(createStrategicParagraph(item));
      });
    }

    if (strategicAnalysis.wt && strategicAnalysis.wt.length > 0) {
      children.push(createSubSectionTitle('4. 底线战略（WT-防御型）'));
      strategicAnalysis.wt.forEach(item => {
        children.push(createStrategicParagraph(item));
      });
    }

    // SWOT战略开发矩阵表格
    children.push(createTableCaption('表1.2 SWOT战略开发矩阵'));
    children.push(createStrategyMatrix(strategicAnalysis));
  }

  // SWOT矩阵表格
  children.push(createTableCaption('表1.1 SWOT分析矩阵'));
  children.push(createSWOTMatrix(strengths, weaknesses, opportunities, threats));

  const doc = new Document({
    sections: [{
      properties: {
        page: {
          size: {
            width: 12240,
            height: 15840
          },
          margin: {
            top: 1440,
            right: 1440,
            bottom: 1440,
            left: 1440
          }
        }
      },
      children: children
    }]
  });

  return doc;
}

/**
 * 主函数
 */
async function main() {
  let inputData;

  if (process.argv[2] === '-') {
    const chunks = [];
    for await (const chunk of process.stdin) {
      chunks.push(chunk);
    }
    inputData = JSON.parse(Buffer.concat(chunks).toString());
  } else if (process.argv[2]) {
    inputData = JSON.parse(process.argv[2]);
  } else {
    console.error('用法: node create_swot_doc.js \'<json>\' 或 echo \'<json>\' | node create_swot_doc.js -');
    process.exit(1);
  }

  const doc = await createSWOTDocument(inputData);
  const buffer = await Packer.toBuffer(doc);

  const companyName = inputData.companyName || '企业';
  const date = inputData.date || new Date().toISOString().split('T')[0];
  const filename = `${companyName}SWOT分析_${date}.docx`;
  const outputPath = path.join(process.env.HOME, 'Desktop', filename);

  fs.writeFileSync(outputPath, buffer);

  console.log(JSON.stringify({
    success: true,
    path: outputPath,
    filename: filename
  }));
}

main().catch(err => {
  console.error(JSON.stringify({
    success: false,
    error: err.message
  }));
  process.exit(1);
});

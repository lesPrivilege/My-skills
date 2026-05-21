#!/usr/bin/env node
/**
 * exam-prep-bank-fix (local version)
 * 本地修复 questions.json 中答案缺失的题目
 * 不依赖外部 API，使用规则推断 + 知识库补全
 *
 * Usage:
 *   node fix.js --subject computer-organization [--dry-run] [--verbose]
 */

const fs = require('fs')
const path = require('path')

const BANK_DIR = path.join(__dirname, '..', '..', '..', 'Projects', 'exam-prep', 'bank')

// 答案知识库：id -> { answer, explanation }
const ANSWER_KB = {
  // ch01 计算机系统概述
  'ch01-计算机系-003': { answer: 'C', explanation: '冯诺依曼机的基本工作方式是按地址访问指令并自动按序执行程序。' },
  'ch01-计算机系-004': { answer: 'A', explanation: '运算器(ALU)不仅完成算术运算，还完成逻辑运算，A选项说法错误。' },
  'ch01-计算机系-007': { answer: 'C', explanation: '解释程序翻译一条执行一条，运行速度较慢，不是较快。' },

  // ch02 数据的表示和运算
  'ch02-数据的表-014': { answer: 'B', explanation: '-66的补码：-66 = -01000010B，取反加1 = 10111110B = BEH。' },
  'ch02-数据的表-018': { answer: 'B', explanation: '11111111在补码中表示-1（符号位为1，取反加1得-1）。' },
  'ch02-数据的表-037': { answer: 'C', explanation: '小端方式，short x1占2020FE00-01，int x2对齐到2020FE04-07，34H在第2字节即2020FE05。' },

  // ch03 存储系统
  'ch03-存储系统-019': { answer: 'A', explanation: '地址引脚增加1根，可寻址空间翻倍，容量至少提高到原来的2倍。' },
  'ch03-存储系统-000': { answer: 'A', explanation: '2路组相联LRU，需模拟访问过程，命中1次。' },

  // ch04 指令系统
  'ch04-指令系统-013': { answer: 'A', explanation: '三地址指令29条需5位编码，二地址指令用剩余前缀扩展，每个地址6位，指令字长至少24位。' },
  'ch04-指令系统-014': { answer: 'B', explanation: 'ISA规定指令格式/类型(I)和通用寄存器(III)，不规定时钟周期(II)和进位方式(IV)。' },

  // ch05 中央处理器
  'ch05-中央处理-003': { answer: 'A', explanation: '指令寄存器(IR)保存当前正在执行的指令。' },
  'ch05-中央处理-006': { answer: 'C', explanation: '指令寄存器(IR)对汇编语言程序员完全透明，不可直接访问。' },
  'ch05-中央处理-007': { answer: 'A', explanation: '指令总是根据程序计数器(PC)从主存储器读出。' },
  'ch05-中央处理-008': { answer: 'B', explanation: '程序计数器(PC)属于控制器的部件。' },
  'ch05-中央处理-015': { answer: 'D', explanation: '程序状态字寄存器(PSW)表示程序和机器运行状态。' },
  'ch05-中央处理-020': { answer: 'A', explanation: 'I正确(CPU不含地址译码器)，II错误(PC存指令地址非操作数地址)，III正确(PC决定执行顺序)，IV错误(状态寄存器对用户不透明)。' },
  'ch05-中央处理-021': { answer: 'B', explanation: '间址周期结束，MDR中内容为操作数地址（从内存读出的有效地址）。' },

  // ch06 总线和输入/输出系统
  'ch06-总线和输-004': { answer: 'C', explanation: '总线结构减少信息传输线的条数，便于增减外设。' },
  'ch06-总线和输-012': { answer: 'C', explanation: '32位×33MHz = 4B×33M = 132MB/s。' },
  'ch06-总线和输-016': { answer: 'B', explanation: '4字节/2时钟周期×10MHz = 20MB/s。' },
}

// OCR 严重损坏、无法修复的题目
const UNFIXABLE = [
  'ch01-计算机系-028',  // "28ms"，完全碎片
  'ch02-数据的表-043',  // OCR 污染严重，题干不可读
  'ch04-指令系统-005',  // 大题，OCR 碎片化
]

async function main() {
  const args = process.argv.slice(2)
  const subject = args.find(a => !a.startsWith('--')) || args[args.indexOf('--subject') + 1]
  const dryRun = args.includes('--dry-run')
  const verbose = args.includes('--verbose')

  if (!subject) {
    console.error('Usage: node fix.js --subject <subject> [--dry-run] [--verbose]')
    process.exit(1)
  }

  const file = path.join(BANK_DIR, subject, 'questions.json')
  if (!fs.existsSync(file)) {
    console.error(`Error: ${file} not found`)
    process.exit(1)
  }

  const questions = JSON.parse(fs.readFileSync(file, 'utf-8'))
  const missing = questions.filter(q => !q.answer?.trim())

  console.log(`Subject: ${subject}`)
  console.log(`Total: ${questions.length}, Missing answer: ${missing.length}`)

  if (missing.length === 0) {
    console.log('No missing answers. Done.')
    return
  }

  let fixed = 0, skipped = 0, unfixable = 0

  for (const q of missing) {
    const kb = ANSWER_KB[q.id]

    if (UNFIXABLE.includes(q.id)) {
      unfixable++
      console.log(`  ${q.id}: UNFIXABLE (OCR too damaged)`)
      continue
    }

    if (kb) {
      if (!dryRun) {
        q.answer = kb.answer
        q.explanation = kb.explanation
      }
      fixed++
      if (verbose) console.log(`  ${q.id}: FIXED → ${kb.answer}`)
    } else {
      skipped++
      console.log(`  ${q.id}: SKIPPED (not in knowledge base)`)
    }
  }

  if (!dryRun && fixed > 0) {
    fs.writeFileSync(file, JSON.stringify(questions, null, 2), 'utf-8')
    console.log(`\nWritten to ${file}`)
  }

  console.log('\n=== 报告 ===')
  console.log(`成功补全: ${fixed}`)
  console.log(`无法修复: ${unfixable}`)
  console.log(`跳过(无知识): ${skipped}`)
}

main().catch(err => {
  console.error('Fatal:', err)
  process.exit(1)
})

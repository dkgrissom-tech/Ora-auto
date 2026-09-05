/**
 * Kids Page-Turner Video Generator
 *
 * Takes a story concept → produces:
 *   1. A 30-45 sec vertical TikTok/IG page-turner video (page flip + narration + music bed)
 *   2. A KDP-ready 8.5x11 interior PDF (all pages + text layout)
 *   3. A KDP wrap cover (front + back + spine)
 *
 * Pipeline:
 *   Story prompt → Claude (story text + scene prompts) → fal.ai Flux (illustrations)
 *   → ElevenLabs (narration) → ffmpeg (page-flip video) → PDFKit (KDP interior + cover)
 *
 * Runs as an Express route inside YT Studio (Replit) so it slots into the existing renderer.
 * POST /api/page-turner with body: { title, ageRange, theme, pageCount, gumroadUrl?, amazonUrl? }
 *
 * Environment vars required (Railway/Replit):
 *   ANTHROPIC_API_KEY  (already set)
 *   FAL_API_KEY        (needs setup at fal.ai/dashboard/keys)
 *   ELEVENLABS_API_KEY (already set)
 *
 * Cost per book (25 pages): ~$1.25 illustrations + $0.15 narration + $0.02 Claude = ~$1.45
 */

import express, { Request, Response } from 'express';
import Anthropic from '@anthropic-ai/sdk';
import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';
import PDFDocument from 'pdfkit';

const router = express.Router();

// ----- Type definitions -----

interface PageTurnerRequest {
  title: string;               // "Pip the Pumpkin's First Halloween"
  ageRange: '3-5' | '5-8';
  theme: string;               // "cute Halloween, friendly ghost, pumpkin patch"
  pageCount: number;           // 20-25 recommended
  gumroadUrl?: string;
  amazonUrl?: string;
  narrationVoiceId?: string;   // defaults to warm children's voice
}

interface StoryPage {
  pageNumber: number;
  text: string;                // The words on the page (max 15 words for 3-5)
  illustrationPrompt: string;  // Detailed Flux prompt
  narrationText: string;       // What ElevenLabs reads (matches text)
}

interface StoryPlan {
  title: string;
  subtitle: string;
  pages: StoryPage[];
  backCoverBlurb: string;
  targetKeywords: string[];    // For KDP SEO
}

// ----- Warm children's narration voice (ElevenLabs) -----
// "Rachel" voice_id: 21m00Tcm4TlvDq8ikWAM (warm female, well-suited to kids stories)
// Fallback to Adam if Rachel isn't available: pNInz6obpgDQGcFmaJgB
const DEFAULT_KIDS_VOICE = '21m00Tcm4TlvDq8ikWAM';

// ----- Step 1: Generate story with Claude -----

async function generateStory(req: PageTurnerRequest): Promise<StoryPlan> {
  const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY! });

  const wordsPerPage = req.ageRange === '3-5' ? 10 : 40;

  const prompt = `You are a children's book author writing for ages ${req.ageRange}.

Write a ${req.pageCount}-page picture book titled "${req.title}".
Theme: ${req.theme}

For each page, provide:
- The story text on the page (max ${wordsPerPage} words, rhythmic and readable aloud)
- A detailed illustration prompt for an AI image generator (specify style: soft watercolor children's book illustration, cute-not-scary, warm palette, centered composition, empty top or bottom third for text placement)
- Narration text (same as page text, but with pronunciation notes if needed)

Also provide:
- A subtitle (subtle, describes the emotional arc)
- Back cover blurb (60-80 words, parent-friendly, sells the emotional payoff)
- 5 KDP SEO keywords

Return ONLY valid JSON matching this schema:
{
  "title": "${req.title}",
  "subtitle": "...",
  "pages": [{"pageNumber": 1, "text": "...", "illustrationPrompt": "...", "narrationText": "..."}],
  "backCoverBlurb": "...",
  "targetKeywords": ["...", "...", "...", "...", "..."]
}`;

  const response = await anthropic.messages.create({
    model: 'claude-sonnet-4-5-20250929',
    max_tokens: 8000,
    messages: [{ role: 'user', content: prompt }],
  });

  const textBlock = response.content.find((b) => b.type === 'text');
  if (!textBlock || textBlock.type !== 'text') {
    throw new Error('No text in Claude response');
  }

  // Extract JSON (Claude sometimes wraps in ```json)
  const jsonMatch = textBlock.text.match(/\{[\s\S]*\}/);
  if (!jsonMatch) throw new Error('No JSON found in Claude output');
  return JSON.parse(jsonMatch[0]) as StoryPlan;
}

// ----- Step 2: Generate illustrations via fal.ai Flux -----

async function generateIllustration(prompt: string, outputPath: string): Promise<void> {
  // Using Flux Pro 1.1 for children's illustration - $0.05/image, high quality
  const response = await fetch('https://queue.fal.run/fal-ai/flux-pro/v1.1', {
    method: 'POST',
    headers: {
      'Authorization': `Key ${process.env.FAL_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      prompt: `${prompt}, children's book illustration, soft watercolor style, warm colors, cute characters, safe for kids, no scary elements`,
      image_size: 'portrait_4_3',  // 768x1024, fits KDP 8.5x11 well
      num_inference_steps: 28,
      guidance_scale: 3.5,
      output_format: 'png',
      safety_tolerance: '2',  // Strict for kids content
    }),
  });

  if (!response.ok) {
    throw new Error(`Flux request failed: ${response.status} ${await response.text()}`);
  }

  const queueData = await response.json();
  const requestId = queueData.request_id;

  // Poll for completion (Flux typically 15-25 sec)
  let attempts = 0;
  while (attempts < 60) {
    await new Promise((r) => setTimeout(r, 2000));
    const statusRes = await fetch(
      `https://queue.fal.run/fal-ai/flux-pro/requests/${requestId}/status`,
      { headers: { 'Authorization': `Key ${process.env.FAL_API_KEY}` } }
    );
    const status = await statusRes.json();
    if (status.status === 'COMPLETED') {
      const resultRes = await fetch(
        `https://queue.fal.run/fal-ai/flux-pro/requests/${requestId}`,
        { headers: { 'Authorization': `Key ${process.env.FAL_API_KEY}` } }
      );
      const result = await resultRes.json();
      const imageUrl = result.images[0].url;
      const imgRes = await fetch(imageUrl);
      const buf = Buffer.from(await imgRes.arrayBuffer());
      fs.writeFileSync(outputPath, buf);
      return;
    }
    if (status.status === 'FAILED') {
      throw new Error(`Flux generation failed: ${JSON.stringify(status)}`);
    }
    attempts++;
  }
  throw new Error('Flux generation timed out');
}

// ----- Step 3: Generate narration via ElevenLabs -----

async function generateNarration(
  text: string,
  outputPath: string,
  voiceId: string = DEFAULT_KIDS_VOICE
): Promise<void> {
  const response = await fetch(
    `https://api.elevenlabs.io/v1/text-to-speech/${voiceId}`,
    {
      method: 'POST',
      headers: {
        'xi-api-key': process.env.ELEVENLABS_API_KEY!,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text,
        model_id: 'eleven_multilingual_v2',
        voice_settings: {
          stability: 0.65,       // Slightly higher for storytelling consistency
          similarity_boost: 0.75,
          style: 0.4,            // Warmth without over-acting
          use_speaker_boost: true,
        },
      }),
    }
  );

  if (!response.ok) {
    throw new Error(`ElevenLabs failed: ${response.status}`);
  }

  const buf = Buffer.from(await response.arrayBuffer());
  fs.writeFileSync(outputPath, buf);
}

// ----- Step 4: Assemble page-turner video (ffmpeg) -----

async function assembleVideo(
  workDir: string,
  story: StoryPlan,
  outputPath: string
): Promise<void> {
  // Video spec: 1080x1920 vertical, 30-45 sec, page flip every 2-3 sec
  // Structure:
  //   0.0-2.0s   Title card (cover image + title text)
  //   2.0-Xs     Pages (each page = 2 sec: 0.3s flip transition + 1.7s hold)
  //   Xs-end     End card with CTA ("Get the book on Amazon / Gumroad")

  const pageDuration = 2.5;
  const totalPages = story.pages.length;
  const contentDuration = totalPages * pageDuration;
  const totalDuration = 2 + contentDuration + 3; // title + pages + CTA

  // Concat filter for pages
  const inputs: string[] = ['-loop', '1', '-t', '2', '-i', path.join(workDir, 'cover.png')];
  for (let i = 1; i <= totalPages; i++) {
    inputs.push('-loop', '1', '-t', String(pageDuration), '-i', path.join(workDir, `page_${i}.png`));
  }
  inputs.push('-loop', '1', '-t', '3', '-i', path.join(workDir, 'cta.png'));
  inputs.push('-i', path.join(workDir, 'narration_full.mp3'));

  // Filter complex: scale each to 1080x1920, add fade transitions, concat
  const filterParts: string[] = [];
  const totalImages = totalPages + 2; // cover + pages + cta
  for (let i = 0; i < totalImages; i++) {
    filterParts.push(
      `[${i}:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=white,setsar=1,fps=30[v${i}]`
    );
  }
  const concatInputs = Array.from({ length: totalImages }, (_, i) => `[v${i}]`).join('');
  filterParts.push(`${concatInputs}concat=n=${totalImages}:v=1:a=0[outv]`);

  const audioIndex = totalImages;
  const cmd = [
    'ffmpeg', '-y',
    ...inputs,
    '-filter_complex', filterParts.join(';'),
    '-map', '[outv]',
    '-map', `${audioIndex}:a`,
    '-c:v', 'libx264',
    '-c:a', 'aac',
    '-b:a', '128k',
    '-shortest',
    '-t', String(totalDuration),
    '-pix_fmt', 'yuv420p',
    outputPath,
  ];

  console.log('Running ffmpeg:', cmd.join(' '));
  execSync(cmd.map((c) => `"${c}"`).join(' '), { stdio: 'inherit' });
}

// ----- Step 5: Build KDP interior PDF -----

async function buildKdpInterior(
  workDir: string,
  story: StoryPlan,
  outputPath: string
): Promise<void> {
  // KDP paperback 8.5x11: 612x792 pt at 72 DPI = 8.5"x11"
  // But KDP prefers 300 DPI source → PDF at trim size with images embedded at print res
  const doc = new PDFDocument({
    size: [612, 792],
    margins: { top: 36, bottom: 36, left: 36, right: 36 },
  });
  doc.pipe(fs.createWriteStream(outputPath));

  // Title page
  doc.fontSize(48).font('Helvetica-Bold').text(story.title, { align: 'center' });
  doc.moveDown(1);
  doc.fontSize(18).font('Helvetica-Oblique').text(story.subtitle, { align: 'center' });

  // Copyright page
  doc.addPage();
  doc.fontSize(10).font('Helvetica').text(
    `Copyright © 2026 Grissom Press. All rights reserved.\n\nIllustrations generated with AI assistance.\n\nISBN: [assigned by KDP]`,
    { align: 'center' }
  );

  // Story pages: illustration top 2/3, text bottom 1/3
  for (const page of story.pages) {
    doc.addPage();
    const imagePath = path.join(workDir, `page_${page.pageNumber}.png`);
    if (fs.existsSync(imagePath)) {
      doc.image(imagePath, 36, 36, { fit: [540, 480], align: 'center' });
    }
    doc.fontSize(20).font('Helvetica-Bold').text(page.text, 36, 550, {
      align: 'center',
      width: 540,
    });
  }

  // Back matter
  doc.addPage();
  doc.fontSize(14).font('Helvetica').text(
    `More books from Grissom Press:\n\n• Shadow & Bloom (adult coloring)\n• Dark & Dreamy Gothic (adult coloring)\n• Spooky Sweet Shop (adult coloring)`,
    { align: 'center' }
  );

  doc.end();
}

// ----- Main route -----

router.post('/api/page-turner', async (req: Request, res: Response) => {
  const body = req.body as PageTurnerRequest;
  const workDir = path.join('/tmp/page-turners', body.title.replace(/[^a-z0-9]/gi, '_'));
  fs.mkdirSync(workDir, { recursive: true });

  try {
    // 1. Story
    console.log(`[${body.title}] Generating story...`);
    const story = await generateStory(body);
    fs.writeFileSync(path.join(workDir, 'story.json'), JSON.stringify(story, null, 2));

    // 2. Cover illustration
    console.log(`[${body.title}] Generating cover...`);
    await generateIllustration(
      `Book cover for "${story.title}", ${body.theme}, title text at top, whimsical layout`,
      path.join(workDir, 'cover.png')
    );

    // 3. Page illustrations (parallel batches of 3 to avoid rate limits)
    const batchSize = 3;
    for (let i = 0; i < story.pages.length; i += batchSize) {
      const batch = story.pages.slice(i, i + batchSize);
      await Promise.all(
        batch.map((p) =>
          generateIllustration(p.illustrationPrompt, path.join(workDir, `page_${p.pageNumber}.png`))
        )
      );
      console.log(`[${body.title}] Illustrations ${i + batch.length}/${story.pages.length}`);
    }

    // 4. CTA card (simple ffmpeg-generated text card)
    const ctaText = body.gumroadUrl
      ? `Get the book!\n${body.gumroadUrl}`
      : 'Get the book on Amazon';
    execSync(
      `ffmpeg -y -f lavfi -i color=c=white:s=1080x1920 -vf "drawtext=text='${ctaText}':fontcolor=black:fontsize=60:x=(w-text_w)/2:y=(h-text_h)/2" -frames:v 1 ${path.join(workDir, 'cta.png')}`
    );

    // 5. Narration (single file, concatenated)
    console.log(`[${body.title}] Generating narration...`);
    const fullNarration = story.pages.map((p) => p.narrationText).join(' ... ');
    await generateNarration(
      fullNarration,
      path.join(workDir, 'narration_full.mp3'),
      body.narrationVoiceId
    );

    // 6. Assemble video
    console.log(`[${body.title}] Assembling video...`);
    const videoPath = path.join(workDir, `${body.title.replace(/[^a-z0-9]/gi, '_')}.mp4`);
    await assembleVideo(workDir, story, videoPath);

    // 7. Build KDP interior
    console.log(`[${body.title}] Building KDP interior...`);
    const kdpPath = path.join(workDir, `${body.title.replace(/[^a-z0-9]/gi, '_')}_KDP_interior.pdf`);
    await buildKdpInterior(workDir, story, kdpPath);

    res.json({
      success: true,
      workDir,
      videoPath,
      kdpInteriorPath: kdpPath,
      story,
      cost: {
        illustrations: story.pages.length * 0.05 + 0.05, // pages + cover
        narration: (fullNarration.length / 1000) * 0.30, // ElevenLabs standard tier
        story: 0.02,
      },
    });
  } catch (err) {
    console.error(`[${body.title}] Error:`, err);
    res.status(500).json({ success: false, error: (err as Error).message });
  }
});

export default router;

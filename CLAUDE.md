# ContentBot - AI Content Creation Studio

**Mission**: Build a complete AI-powered video creation studio for viral TikTok/YouTube Shorts automatically.

**Product Vision**: Enable creators to produce monetizable video content at scale - from idea to final video in under 60 seconds.

**Status**: ✅ Core Pipeline Complete | 🚧 Week 1: Architectural Reorganization (Jan 2026)

---

## Claude Code Optimization (CRITICAL)

**File Management Policy:**
- Update ONLY: `CLAUDE.md`, `PROJECT.md` + max 3 other files per session
- NEVER create new .md files for minor changes
- Everything in local `.claude/` (NEVER `~/.claude/`)

**Subagent Strategy:**
- **Model Selection**: Haiku 4.5 (simple tasks) | Sonnet 4.5 (complex reasoning)
- **Scope Constraints**: Each agent sees ONLY their files (backend: `src/`, `app.py` | frontend: `contentbot-ui/`)
- **Communication**: Agents talk to each other via coordinator, update own docs independently
- **Compact & Clear**: Concise instructions, minimal token usage

**Orchestrator Role (You):**
- DON'T code yourself - use subagents
- ASK before taking action
- Keep high-level docs updated
- Delete obsolete docs immediately

---

## Research Protocol (MANDATORY)

**Before planning or implementing ANY new feature:**

1. **Web Research Required** - Use WebSearch tool to research:
   - GitHub repositories: `"github <technology> best practices 2025"`
   - Reddit discussions: r/webdev, r/Python, r/reactjs, r/moviepy
   - Official documentation wikis
   - Stack Overflow recent solutions
   - Tech blogs (Medium, Dev.to, platform-specific)

2. **Research Synthesis:**
   - Identify 3+ different approaches
   - Compare trade-offs (performance, maintainability, complexity)
   - Check for 2025 updates (APIs change fast)
   - Validate against current tech stack

3. **Then Plan:**
   - Create plan file in `.claude/plans/` (NOT `~/.claude/plans/`)
   - Include research findings in plan
   - Present options to user before implementing

**Never implement features based on outdated knowledge. Always validate with current research.**

---

## Super Agentic Orchestration

**Coordinator Role (Main Claude Session):**
- NEVER write code directly
- Spawn specialized agents for all implementation tasks
- Ask user before taking action
- Orchestrate agent communication
- Keep high-level docs updated
- Delete obsolete docs immediately

**Agent Communication Protocol:**

When an agent needs help from another agent:
```
Agent A → Coordinator: "Need frontend changes for backend feature X. Request frontend-specialist to implement Y in Z component."
Coordinator → Agent B: Spawns frontend-specialist with context
Agent B → Coordinator: Reports completion with file paths modified
Coordinator → Agent A: "Frontend ready, continue with backend integration"
```

**Agent Self-Documentation:**
- Each agent MUST update their own `.md` file after discovering new patterns
- Update triggers:
  - New code pattern established (e.g., new MoviePy optimization)
  - New integration pattern (e.g., new API endpoint structure)
  - Performance breakthrough (e.g., render time improvement)
- Format: Agent edits own file, adds to relevant section, commits change

**Model Selection Guidelines:**
- **Haiku 4.5**: UI work, test writing, simple CRUD, config updates
- **Sonnet 4.5**: Complex backend logic, video rendering optimization, AI integration, architectural decisions
- Default: When unsure, start with Haiku, escalate to Sonnet if complexity emerges

---

## Core Principle: Purpose-Driven Development

**Every change must serve the complete studio vision:**
1. Does this help creators make better content?
2. Does this enable automation/scale?
3. Does this improve monetization potential?
4. If NO to all three → don't implement it

**Zero waste policy:**
- No unnecessary comments (code should be self-documenting)
- No placeholder TODOs (implement or don't)
- No "nice to have" features (only essential)
- **No empty directories or non-functional mockups**
- Minimal token usage in all files

**Production-first mindset:**
- Every feature must work end-to-end
- Test immediately after implementation
- No breaking changes to existing pipeline
- Fail fast with clear error messages

---

## Quick Reference

**Tech Stack:**
- Backend: Python 3.11+ | Flask | Groq AI | ElevenLabs | MoviePy 2.x
- Frontend: React + Vite | TailwindCSS | Axios

**Start Commands:**
```bash
python app.py                      # Backend: http://localhost:5000
cd contentbot-ui && npm run dev    # Frontend: http://localhost:5173
pytest tests/                       # Run all tests
```

**Performance Targets:**
- Story generation: <5s
- TTS generation: <8s (or instant if cached)
- Video render: <30s for 60s video
- Total pipeline: <45s end-to-end

---

## Detailed Documentation

For comprehensive guidance, see:

**Development Rules:** `.claude/rules/development.md`
- Code modification workflow
- Testing requirements
- What NOT to do

**Architecture:** `.claude/rules/architecture.md`
- System pipeline
- Tech stack details
- File structure
- Viral optimization settings

**Specialized Agents:** `.claude/agents/`
- `frontend-specialist.md` - React/TailwindCSS (Haiku)
- `backend-specialist.md` - Python/Flask/MoviePy (Sonnet)
- `qa-specialist.md` - pytest/TDD (Haiku)
- `moviepy-video-architect.md` - Video rendering expert (Sonnet)

**API Reference:** See `PROJECT.md` for all endpoints

---

## Current Development Focus (Jan 2026)

### Week 1: Foundation
- ✅ File reorganization (tests/, docs/archive/, .claude/)
- ✅ Claude Code optimization (.claudeignore, pytest.ini)
- ✅ Hierarchical documentation
- ✅ Specialized agent definitions
- 🚧 Pre-commit hooks
- 🚧 Verify tests pass

### Week 2: Effect System Fix
- Two-pass rendering architecture
- MoviePy 2.x compatibility audit
- TDD workflow establishment
- Integration test suite

### Week 3: Multi-Part Stories
- StoryContextManager backend
- Multi-part UI (Generator + StorySeries pages)
- Context preservation

---

## Monetization Strategy (TikTok 2025)

**Requirements:**
- ✅ 60+ second videos (defaults to 75s)
- ✅ Original AI-generated content
- ✅ Human-like quality (anti-AI prompts)
- ⏳ 10,000 followers (consistency required)
- ⏳ 100K views/30 days (2x daily posts)

**Revenue Potential:**
- Conservative: $450/month (600K views @ $0.75 RPM)
- Moderate: $1,200/month (1.2M views @ $1.00 RPM)
- High-retention: $1,800/month (1.2M views @ $1.50 RPM + bonus)

---

## Development Workflow

**For New Features:**
1. Read relevant files first (understand context)
2. Check `.claude/rules/development.md` for guidelines
3. Check `.claude/agents/<specialist>.md` for patterns
4. Write test first (TDD)
5. Implement feature
6. Test: `pytest tests/` + manual verification
7. Commit (pre-commit hooks run automatically)

**For Bug Fixes:**
1. Identify root cause (not symptoms)
2. Read affected files completely
3. Fix and test immediately
4. Verify no regressions

---

## Success Metrics

**Product success = User monetization success**

Track:
- Videos generated per day (goal: 10+)
- Monetizable videos % (60s+, should be 100%)
- Time from idea to final video (goal: <60s)

Don't track (vanity metrics):
- Code coverage percentages
- Number of features
- Lines of code

---

**Last Updated**: January 11, 2026
**System Version**: 2.1 - Architectural Reorganization
**Current Phase**: Week 1 - Foundation & Claude Code Optimization

For full context, refer to hierarchical docs in `.claude/rules/` and `.claude/agents/`

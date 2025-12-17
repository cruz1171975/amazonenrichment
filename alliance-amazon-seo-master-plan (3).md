# Alliance Chemical — Amazon FBM Listing Optimization Master Plan

> **Document Type**: Strategic Planning & System Prompt  
> **Version**: 1.0  
> **Date**: January 2024  
> **For**: Alliance Chemical E-Commerce Team + AI Agents

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Critical Safety & Compliance Rules](#2-critical-safety--compliance-rules)
3. [Forbidden Claims — Complete Blocklist](#3-forbidden-claims--complete-blocklist)
4. [Amazon SEO Fundamentals for Chemical Products](#4-amazon-seo-fundamentals-for-chemical-products)
5. [Listing Optimization Strategy](#5-listing-optimization-strategy)
6. [Content Writing Guidelines](#6-content-writing-guidelines)
7. [Keyword Research Process](#7-keyword-research-process)
8. [Product Title Optimization](#8-product-title-optimization)
9. [Bullet Point Strategy](#9-bullet-point-strategy)
10. [Product Description Best Practices](#10-product-description-best-practices)
11. [Backend Search Terms](#11-backend-search-terms)
12. [A+ Content Strategy](#12-a-content-strategy)
13. [Workflow & Approval Process](#13-workflow--approval-process)
14. [CLI Tool Architecture](#14-cli-tool-architecture)
15. [Facts Card System](#15-facts-card-system)
16. [Examples: Allowed vs Forbidden Wording](#16-examples-allowed-vs-forbidden-wording)
17. [Competitive Analysis Framework](#17-competitive-analysis-framework)
18. [Performance Metrics & KPIs](#18-performance-metrics--kpis)
19. [Troubleshooting Common Issues](#19-troubleshooting-common-issues)
20. [Appendices](#20-appendices)

---

## 1. Executive Summary

### Purpose

This document provides a complete framework for safely optimizing Amazon FBM (Fulfilled by Merchant) listings for Alliance Chemical products. Chemical products face unique regulatory constraints that make standard Amazon SEO advice dangerous to follow blindly.

### Core Philosophy

```
SAFETY FIRST → COMPLIANCE ALWAYS → OPTIMIZATION WITHIN BOUNDS
```

### Key Principles

1. **Read-Only Default**: All automated systems default to read-only mode
2. **Facts-Only Content**: Every claim must trace to a verified facts card
3. **Approval Gates**: No live changes without explicit human approval
4. **Rollback Ready**: Every change must be reversible
5. **Compliance Scanning**: Automated blocklist checking before any publish

### What This Document Covers

- Complete list of forbidden claims (EPA/FDA/FTC regulated)
- Safe SEO strategies for chemical products
- Content templates and examples
- Workflow processes for team and AI agents
- Technical architecture for tooling

---

## 2. Critical Safety & Compliance Rules

### 🚨 NON-NEGOTIABLE RULES

These rules apply to ALL content creation, whether by humans or AI:

#### Rule 0: No Grade Claims Unless Verified in Shopify

**CRITICAL**: Do NOT mention product grades (laboratory grade, technical grade, food grade, ACS grade, reagent grade, pharmaceutical grade, industrial grade, etc.) unless that EXACT grade appears in the product title in Shopify.

**Why**: Grade claims imply certifications and specifications. Making unverified grade claims is misleading and potentially illegal.

**How to verify**: Pull the product from Shopify API → Check the `title` field → Only use grades that appear there.

```
❌ WRONG: Assuming a product is "food grade" because it seems like it could be
✅ RIGHT: Only stating "food grade" if Shopify title contains "Food Grade"
```

#### Rule 0: NO GRADE CLAIMS UNLESS IN SHOPIFY TITLE

**CRITICAL**: Do NOT use grade terminology unless it appears EXACTLY in the Shopify product title.

```
❌ FORBIDDEN (unless in Shopify title):
   - "Laboratory Grade"
   - "Technical Grade" 
   - "Food Grade"
   - "ACS Grade"
   - "Reagent Grade"
   - "Pharmaceutical Grade"
   - "Industrial Grade"
   - "USP Grade"
   - "FCC Grade"
   - "NF Grade"
```

**Why**: Grade claims imply specific certifications and specifications. Using them incorrectly is both a compliance risk and customer trust issue.

**Process**: 
1. Pull product title from Shopify via API
2. Check if grade term exists in title
3. If YES → can use that exact grade term
4. If NO → do not mention any grade

#### Rule 1: No Pesticide/Antimicrobial Claims Without EPA Registration

**Why**: Making claims that a product kills, repels, or prevents microorganisms or pests without EPA registration is a **federal crime** under FIFRA (Federal Insecticide, Fungicide, and Rodenticide Act).

**Penalty**: Up to $20,000 per violation per day; criminal penalties possible.

**Amazon Impact**: Immediate listing removal, potential account suspension.

#### Rule 2: No Drug/Medical Claims Without FDA Approval

**Why**: Claims that a product treats, cures, or prevents disease make it an unapproved drug under the FD&C Act.

**Penalty**: FDA warning letters, seizure, injunction, criminal prosecution.

**Amazon Impact**: Category restrictions, listing removal.

#### Rule 3: No Unsubstantiated Environmental Claims

**Why**: FTC Green Guides require substantiation for environmental marketing claims.

**Penalty**: FTC enforcement action, civil penalties.

**Amazon Impact**: A-to-Z claims, negative reviews, listing flags.

#### Rule 4: No Absolute Safety Claims

**Why**: Claims like "non-toxic" or "completely safe" are almost never true for chemical products and invite liability.

**Risk**: Product liability lawsuits, regulatory action.

### Regulatory Quick Reference

| Agency | What They Regulate | Key Forbidden Claims |
|--------|-------------------|---------------------|
| **EPA** | Pesticides, antimicrobials | Kills/prevents/repels organisms |
| **FDA** | Drugs, medical devices | Treats/cures/prevents disease |
| **FTC** | Advertising claims | Unsubstantiated superiority/environmental claims |
| **CPSC** | Consumer product safety | Misleading safety claims |
| **OSHA** | Workplace safety | Misrepresented hazard info |

---

## 3. Forbidden Claims — Complete Blocklist

### Category A: Antimicrobial Claims (EPA) — HARD BLOCK

These terms trigger EPA pesticide registration requirements:

```
❌ disinfect / disinfectant / disinfecting
❌ sanitize / sanitizer / sanitizing  
❌ antimicrobial
❌ antibacterial
❌ antifungal
❌ antiviral
❌ anti-mold / anti-mildew
❌ germicidal / germicide
❌ bactericidal / bactericide
❌ fungicidal / fungicide
❌ virucidal / virucide
❌ sterilize / sterilizing / sterilant
❌ kills germs / kills bacteria / kills viruses / kills mold / kills fungus
❌ destroys germs / destroys bacteria
❌ eliminates germs / eliminates bacteria
❌ removes germs / removes bacteria
❌ prevents bacterial growth
❌ prevents mold growth
❌ prevents mildew
❌ stops bacteria
❌ germ-free / bacteria-free / virus-free
❌ 99.9% of germs (or any percentage + organism)
❌ hospital-grade (when implying antimicrobial)
❌ medical-grade disinfection
```

### Category B: Pesticide Claims (EPA) — HARD BLOCK

```
❌ repels insects / insect repellent
❌ repels bugs / bug repellent
❌ repels mosquitoes / mosquito repellent
❌ repels rodents / rodent repellent
❌ kills insects / insecticide
❌ kills ants / kills roaches / kills spiders
❌ pest control / pest killer
❌ keeps bugs away
❌ deters pests
```

### Category C: Medical/Drug Claims (FDA) — HARD BLOCK

```
❌ cures [any condition]
❌ treats [any disease]
❌ prevents [any disease]
❌ heals / healing
❌ therapeutic
❌ medicinal
❌ relieves pain
❌ reduces inflammation
❌ treats infection
❌ medical grade (unless certified)
❌ pharmaceutical grade (unless certified)
❌ FDA approved (unless actually approved)
```

### Category D: Health Claims — HARD BLOCK

```
❌ removes allergens
❌ eliminates allergens
❌ hypoallergenic (for chemicals)
❌ allergy-free
❌ asthma-safe
❌ improves air quality (health context)
❌ purifies air (health context)
❌ detoxifies / detoxifying
❌ cleanses toxins
```

### Category E: Absolute Safety Claims — HARD BLOCK

```
❌ non-toxic / nontoxic
❌ chemical-free
❌ toxin-free
❌ completely safe
❌ 100% safe
❌ totally safe
❌ absolutely safe
❌ perfectly safe
❌ harmless
❌ no harmful chemicals
❌ safe for everyone
❌ safe for all uses
❌ child-safe (unqualified)
❌ pet-safe (unqualified)
```

### Category F: Environmental Claims — SOFT BLOCK (Requires Substantiation)

```
⚠️ eco-friendly
⚠️ environmentally friendly
⚠️ green (environmental context)
⚠️ sustainable
⚠️ biodegradable (without qualification)
⚠️ compostable (without certification)
⚠️ recyclable (without qualification)
⚠️ carbon neutral
⚠️ zero waste
⚠️ planet-friendly
⚠️ earth-friendly
⚠️ natural (unqualified)
⚠️ all-natural
⚠️ organic (without USDA certification)
```

### Category G: Superiority Claims — SOFT BLOCK (Requires Evidence)

```
⚠️ best
⚠️ #1 / number one
⚠️ leading
⚠️ top-rated
⚠️ most effective
⚠️ strongest
⚠️ most powerful
⚠️ better than [competitor]
⚠️ superior to
⚠️ outperforms
⚠️ unmatched
⚠️ unbeatable
```

---

## 4. Amazon SEO Fundamentals for Chemical Products

### How Amazon A9/A10 Algorithm Works

Amazon's search algorithm prioritizes:

1. **Relevance** — Does your listing match what the customer searched?
2. **Performance** — Does your listing convert browsers to buyers?
3. **Customer Satisfaction** — Reviews, returns, seller metrics

### Chemical Product Ranking Factors

| Factor | Weight | Notes |
|--------|--------|-------|
| Title keyword match | High | Exact match in title ranks highest |
| Bullet point keywords | Medium | Secondary keyword placement |
| Backend search terms | Medium | Hidden keywords, 250 bytes max |
| Sales velocity | High | More sales = higher rank |
| Conversion rate | High | Clicks → purchases ratio |
| Review rating | Medium | 4.0+ stars preferred |
| Review count | Medium | More reviews = more trust |
| Price competitiveness | Medium | Value perception matters |
| Fulfillment method | Medium | FBA slightly preferred over FBM |
| Stock availability | High | Out of stock = rank drops |

### Chemical-Specific Challenges

1. **Restricted keywords**: Many high-volume keywords are forbidden
2. **Category limitations**: Some categories have stricter rules
3. **Hazmat restrictions**: Shipping limitations affect Prime eligibility
4. **Review acquisition**: Chemical products get fewer reviews
5. **Return rates**: Education reduces returns

---

## 5. Listing Optimization Strategy

### The Alliance Chemical Optimization Framework

```
┌─────────────────────────────────────────────────────────────────┐
│                    OPTIMIZATION FUNNEL                          │
├─────────────────────────────────────────────────────────────────┤
│  1. DISCOVERY        │ Customer finds your listing              │
│     Keywords ────────│ Title, bullets, backend terms            │
├──────────────────────┼──────────────────────────────────────────┤
│  2. CONSIDERATION    │ Customer evaluates your listing          │
│     Content ─────────│ Images, bullets, description, A+         │
├──────────────────────┼──────────────────────────────────────────┤
│  3. CONVERSION       │ Customer decides to buy                  │
│     Trust ───────────│ Reviews, brand, certifications           │
├──────────────────────┼──────────────────────────────────────────┤
│  4. SATISFACTION     │ Customer experience post-purchase        │
│     Quality ─────────│ Product quality, support, accuracy       │
└─────────────────────────────────────────────────────────────────┘
```

### Priority Matrix for Optimization

| Element | SEO Impact | Conversion Impact | Effort | Priority |
|---------|------------|-------------------|--------|----------|
| Product Title | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Low | 1st |
| Main Image | ⭐⭐ | ⭐⭐⭐⭐⭐ | Medium | 2nd |
| Bullet Points | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Low | 3rd |
| Backend Keywords | ⭐⭐⭐⭐ | ⭐ | Low | 4th |
| Product Description | ⭐⭐⭐ | ⭐⭐⭐ | Medium | 5th |
| A+ Content | ⭐⭐ | ⭐⭐⭐⭐ | High | 6th |
| Secondary Images | ⭐ | ⭐⭐⭐⭐ | Medium | 7th |

---

## 6. Content Writing Guidelines

### Voice & Tone for Alliance Chemical

**Brand Voice Attributes:**
- Professional but approachable
- Technical but understandable
- Confident but not boastful
- Helpful and educational

**Do:**
- Use specific, measurable claims
- Include application guidance
- Reference industry standards
- Explain benefits through features

**Don't:**
- Make absolute statements
- Use superlatives without evidence
- Copy competitor language
- Oversimplify technical products

### Safe Claim Patterns

#### Pattern 1: Feature → Benefit (Safe)

```
✅ "High-purity formula (99.5%+) ensures consistent results in laboratory applications"
✅ "Fast-evaporating solvent reduces drying time between cleaning cycles"
✅ "Concentrated formula means less product needed per application"
```

#### Pattern 2: Application-Specific (Safe)

```
✅ "Designed for industrial degreasing applications"
✅ "Formulated for use in food processing equipment cleaning"
✅ "Compatible with stainless steel, aluminum, and most plastics"
```

#### Pattern 3: Specification-Based (Safe)

```
✅ "Meets ACS reagent grade specifications"
✅ "Technical grade suitable for manufacturing processes"
✅ "NSF registered for use in food processing facilities"
```

#### Pattern 4: Qualified Statements (Safe)

```
✅ "When used as directed, suitable for..."
✅ "In proper concentrations, effective for..."
✅ "With appropriate PPE, can be used for..."
```

### Dangerous Claim Patterns to Avoid

#### Pattern 1: Absolute Claims

```
❌ "Safe for all surfaces" → ✅ "Compatible with most common surfaces; test in inconspicuous area first"
❌ "Works on everything" → ✅ "Effective on oil, grease, and carbon-based soils"
❌ "Completely non-toxic" → ✅ "Low acute oral toxicity (see SDS for details)"
```

#### Pattern 2: Organism Claims (Even Indirect)

```
❌ "Keeps surfaces clean and germ-free" → ✅ "Removes visible soils and residues"
❌ "Fresh, clean scent eliminates odor-causing bacteria" → ✅ "Fresh scent helps mask unpleasant odors"
❌ "Prevents buildup that causes contamination" → ✅ "Regular use prevents residue accumulation"
```

#### Pattern 3: Health Implications

```
❌ "Creates a healthier environment" → ✅ "Maintains clean working surfaces"
❌ "Reduces sick days" → ✅ "Supports facility cleanliness programs"
❌ "Protects your family" → ✅ "Professional-grade cleaning for home use"
```

---

## 7. Keyword Research Process

### Step 1: Seed Keyword Generation

Start with your facts card:
- Product name and variations
- Chemical name (common and IUPAC)
- CAS number
- Primary applications
- Industry terms

### Step 2: Amazon-Specific Research

**Tools to use:**
- Amazon search bar autocomplete
- Amazon Brand Analytics (if available)
- Helium 10 / Jungle Scout (optional)
- Competitor listing analysis

**Amazon Autocomplete Method:**
```
1. Type "[product type]" in Amazon search
2. Note all autocomplete suggestions
3. Add modifiers: "[product] for...", "[product] industrial", etc.
4. Record all relevant suggestions
```

### Step 3: Keyword Filtering for Compliance

Run ALL keywords through blocklist check:

```
┌─────────────────┐
│ Raw Keywords    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Blocklist Check │ ──── Contains forbidden term? ──── REMOVE
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Intent Analysis │ ──── Implies forbidden claim? ──── REMOVE
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Safe Keywords   │
└─────────────────┘
```

### Step 4: Keyword Categorization

| Category | Example | Use In |
|----------|---------|--------|
| Primary | "isopropyl alcohol 99%" | Title |
| Secondary | "IPA solvent", "rubbing alcohol" | Bullets |
| Long-tail | "isopropyl alcohol for electronics cleaning" | Backend |
| Application | "flux remover", "degreaser" | Bullets, backend |
| Industry | "laboratory solvent", "industrial cleaner" | Description |

### Step 5: Search Volume vs. Safety Matrix

```
                    HIGH SEARCH VOLUME
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         │   CAUTION       │    PRIORITY     │
         │   High volume   │    High volume  │
    LOW  │   but risky     │    and safe     │  HIGH
  SAFETY │                 │                 │ SAFETY
         │                 │                 │
         │   AVOID         │    SECONDARY    │
         │   Low value,    │    Safe but     │
         │   high risk     │    low volume   │
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
                    LOW SEARCH VOLUME
```

---

## 8. Product Title Optimization

### Amazon Title Formula for Chemicals

```
[Brand] + [Product Name] + [Key Attribute] + [Size/Quantity] + [Primary Application]
```

**Character Limit**: 200 characters (but 80 visible on mobile)

### Title Component Priority

1. **Brand Name** (required, front-loaded)
2. **Product Name** (primary keyword)
3. **Concentration/Purity** (if key differentiator)
4. **Size** (gallons, pounds, etc.)
5. **Application** (what it's for)
6. **Form** (liquid, powder, etc.)

### Good Title Examples

```
✅ Alliance Chemical Isopropyl Alcohol 99% (IPA) - 1 Gallon - Laboratory & Electronics Grade Solvent

✅ Alliance Chemical Phosphoric Acid 85% Technical Grade - 1 Gallon - Rust Removal & Metal Prep Solution

✅ Alliance Chemical Sodium Hydroxide (Caustic Soda) Flakes - 10 lbs - Industrial Strength for Cleaning & Manufacturing

✅ Alliance Chemical Citric Acid Powder - 5 lb Bag - Food Grade - For Canning, Cleaning, Bath Bombs
```

### Bad Title Examples (And Why)

```
❌ Alliance Chemical BEST Disinfecting Sanitizer Kills 99.9% Germs - SAFE Non-Toxic
   Problems: "disinfecting", "sanitizer", "kills germs", "safe", "non-toxic"

❌ Alliance Chemical Miracle Cleaner - Antibacterial Anti-Mold Eco-Friendly Green Solution
   Problems: "antibacterial", "anti-mold", "eco-friendly" without substantiation

❌ Alliance Chemical Industrial Chemical - Cheap Wholesale Bulk - FREE SHIPPING!!!
   Problems: No keywords, spam triggers, all caps
```

### Title Optimization Checklist

- [ ] Primary keyword in first 80 characters
- [ ] Brand name at front
- [ ] No forbidden terms
- [ ] No ALL CAPS (except acronyms)
- [ ] No promotional language ("sale", "free shipping")
- [ ] No special characters for decoration
- [ ] Size/quantity included
- [ ] Readable and grammatical

---

## 9. Bullet Point Strategy

### Amazon Bullet Point Structure

5 bullet points available, each up to 500 characters (but 200-250 recommended)

### The SAFE Framework for Chemical Bullets

```
S - Specification (what it is)
A - Application (what it's for)
F - Feature (how it works)
E - Experience (what to expect)
```

### Bullet Point Template

```
Bullet 1: SPECIFICATION - Grade, purity, composition
Bullet 2: PRIMARY APPLICATION - Main use case
Bullet 3: SECONDARY APPLICATION - Additional use cases
Bullet 4: FEATURE/BENEFIT - Key differentiator
Bullet 5: PRACTICAL INFO - Packaging, storage, usage tips
```

### Example Bullet Points (Good)

**Product: Isopropyl Alcohol 99%**

```
• PURITY (GRADE ONLY IF VERIFIED): 99%+ isopropyl alcohol (IPA) for precision cleaning and solvent applications. **Only include any grade term if the exact grade appears in the Shopify product title.**

• ELECTRONICS & ELECTRICAL CLEANING: Ideal for removing flux residue, cleaning circuit boards, connectors, and contacts; fast evaporation leaves no residue

• VERSATILE SOLVENT: Effective for degreasing metal parts, preparing surfaces for painting or bonding, and general industrial cleaning tasks

• FAST-EVAPORATING FORMULA: Rapid evaporation rate minimizes drying time and reduces the need for rinsing in most applications

• PROFESSIONAL PACKAGING: Shipped in chemical-resistant HDPE container with secure seal; store in cool, dry place away from heat sources and open flame
```

### Example Bullet Points (Bad — Do NOT Use)

```
❌ KILLS 99.9% OF GERMS: Hospital-grade disinfectant sanitizes surfaces on contact
   Problem: Antimicrobial claims

❌ COMPLETELY SAFE & NON-TOXIC: Eco-friendly formula is safe for your family and pets
   Problem: Absolute safety claims, unsubstantiated environmental claims

❌ BEST QUALITY GUARANTEED: Superior to other brands, #1 rated industrial chemical
   Problem: Unsubstantiated superiority claims

❌ PREVENTS MOLD AND MILDEW: Anti-fungal formula stops bacterial growth
   Problem: Antimicrobial/antifungal claims
```

### Bullet Point Compliance Checklist

For each bullet:
- [ ] No blocklist terms present
- [ ] Claims traceable to facts card
- [ ] No absolute safety statements
- [ ] No organism-related claims
- [ ] No unsubstantiated comparisons
- [ ] Benefit clearly stated
- [ ] Professional tone maintained

---

## 10. Product Description Best Practices

### Description Structure

**HTML Allowed**: Basic formatting (bold, line breaks, lists)

**Recommended Length**: 1000-2000 characters

### Description Template

```html
[OPENING - What it is and primary use]

[APPLICATION SECTION - Detailed use cases]
Ideal for:
• Application 1
• Application 2
• Application 3

[SPECIFICATIONS SECTION - Technical details]
Specifications:
• Purity/concentration
• Physical form
• Key properties

[USAGE GUIDANCE - How to use]
For best results, [usage instructions]

[PACKAGING & STORAGE - Practical info]
Each order includes [packaging details]. Store [storage requirements].

[PROFESSIONAL/QUALITY STATEMENT - Build trust]
Alliance Chemical has been providing [quality statement based on facts].
```

### Example Product Description

**Product: Citric Acid Powder, Food Grade**

```html
Alliance Chemical Citric Acid Powder is a high-purity, food-grade acidulant suitable for culinary, household, and DIY applications. This naturally occurring organic acid is derived from citrus fruits and provided in convenient crystalline powder form.

<b>Common Applications:</b>
• Home canning and preserving - adjusts pH for safe food preservation
• Homemade bath bombs, shower steamers, and fizzing bath products
• Descaling coffee makers, kettles, and dishwashers
• Cheese making and other culinary uses requiring acid adjustment
• DIY cleaning solutions for hard water deposits

<b>Product Specifications:</b>
• Purity: 99.5%+ anhydrous citric acid
• Form: Fine crystalline powder
• Solubility: Highly soluble in water
• Food-grade quality suitable for culinary applications

<b>Usage Guidance:</b>
Dissolve in water according to your specific application requirements. For descaling appliances, a typical solution is 1-2 tablespoons per quart of water. For canning, follow tested recipes from trusted sources like the USDA or Ball.

<b>Packaging:</b>
Supplied in resealable food-safe packaging to maintain freshness and prevent moisture absorption. Store in a cool, dry place with container tightly sealed.

Alliance Chemical is committed to providing consistent, high-quality chemical products for both professional and consumer applications.
```

---

## 11. Backend Search Terms

### What Are Backend Search Terms?

Hidden keywords that customers don't see but Amazon indexes for search. Located in Seller Central under "Keywords" tab.

**Limit**: 250 bytes (not characters — special characters count more)

### Backend Keyword Best Practices

**Do Include:**
- Alternate spellings
- Synonyms
- Abbreviations
- Common misspellings
- Related terms not in visible content
- Spanish/other language terms (if relevant)

**Do NOT Include:**
- Words already in title/bullets
- Competitor brand names
- Forbidden/blocked terms
- Subjective claims (best, amazing)
- Temporary terms (new, on sale)

### Backend Keyword Template

```
[synonym1] [synonym2] [alternate spelling] [abbreviation] [application term] [industry term] [related chemical] [misspelling] [spanish term if applicable]
```

### Example Backend Keywords

**Product: Isopropyl Alcohol 99%**

```
IPA isopropanol 2-propanol rubbing alcohol electronics cleaner flux remover solvent degreaser cleaning alcohol technical grade lab grade reagent electronic repair phone screen cleaner computer cleaner alcohol isopropilico
```

**What's NOT included (and why):**
- "isopropyl alcohol" — already in title
- "sanitizer" — forbidden term
- "disinfectant" — forbidden term
- "kills germs" — forbidden term
- "best cleaner" — subjective

### Backend Keyword Compliance Check

Before adding backend keywords:
1. Run full blocklist scan
2. Remove any forbidden terms
3. Remove duplicates from visible content
4. Check byte count (≤250)
5. Remove any competitor brand names

---

## 12. A+ Content Strategy

### What is A+ Content?

Enhanced product descriptions with images, comparison charts, and rich media. Available to Brand Registered sellers.

### A+ Content Modules for Chemicals

**Recommended Modules:**

1. **Standard Image & Text** — Product photos with feature callouts
2. **Comparison Chart** — Compare your product sizes/grades (NOT competitors)
3. **Technical Specifications** — Detailed specs in clean format
4. **Application Gallery** — Show use cases (with safe imagery)
5. **Brand Story** — Company background and values

### A+ Content Safety Rules

All text in A+ Content follows the same blocklist rules as listings.

**Image Guidelines:**
- No images implying antimicrobial use
- No medical/healthcare settings (unless actually registered)
- No children near chemicals
- No unprotected skin contact with hazardous materials
- Include appropriate PPE in use images

### A+ Content Example Outline

**Module 1: Header Image**
- Product lineup photo
- Brand logo
- Tagline: "Professional-Grade Chemical Solutions"

**Module 2: Feature Callouts**
- Image: Close-up of product
- Callout 1: "High Purity" — 99%+ specification
- Callout 2: "Versatile Applications" — Multiple uses
- Callout 3: "Secure Packaging" — Safe shipping

**Module 3: Application Grid**
- 4 images showing safe use cases
- Industrial cleaning, electronics, laboratory, manufacturing

**Module 4: Specification Table**
- Purity, pH, specific gravity, flash point, etc.

**Module 5: Brand Story**
- Company history
- Quality commitment
- Customer service focus

---

## 13. Workflow & Approval Process

### Content Creation Workflow

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        CONTENT CREATION WORKFLOW                          │
└──────────────────────────────────────────────────────────────────────────┘

Step 1: GATHER FACTS
    │
    ├── Pull current listing data from Amazon
    ├── Review product facts card
    ├── Check SDS and TDS documents
    └── Identify optimization opportunities
    │
    ▼
Step 2: DRAFT CONTENT
    │
    ├── Write title (use template)
    ├── Write 5 bullet points (use SAFE framework)
    ├── Write description (use template)
    ├── Compile backend keywords
    └── Draft A+ content (if applicable)
    │
    ▼
Step 3: COMPLIANCE CHECK
    │
    ├── Run automated blocklist scan
    ├── Verify all claims against facts card
    ├── Check for heuristic warnings
    └── Flag any items for manual review
    │
    ▼
Step 4: REVIEW & APPROVAL
    │
    ├── If automated check passes → Queue for approval
    ├── If warnings present → Manual compliance review
    └── If blocks present → Return to drafting
    │
    ▼
Step 5: APPROVAL GATE
    │
    ├── Reviewer examines proposed changes
    ├── Approver signs off in approval system
    └── Approved changes added to approved.csv
    │
    ▼
Step 6: STAGED APPLY
    │
    ├── Run apply in dry-run mode first
    ├── Verify changes look correct
    └── Execute with --execute flag
    │
    ▼
Step 7: POST-APPLY
    │
    ├── Rollback file automatically created
    ├── Verify changes live on Amazon
    └── Monitor for any issues
```

### Approval Roles

| Role | Responsibilities | Can Approve |
|------|------------------|-------------|
| Content Creator | Draft listings, research keywords | No |
| Content Reviewer | Review for quality, clarity | No |
| Compliance Officer | Review for regulatory compliance | Compliance items |
| E-Commerce Manager | Final business approval | All items |
| System Admin | Technical execution | N/A (execution only) |

### Approval Record Format

**File**: `approvals/approved.csv`

```csv
sku,field,old_value,new_value,approved_by,approved_at,notes
AC-IPA-99-1GAL,item_name,"Old Title Here","Alliance Chemical Isopropyl Alcohol 99% - 1 Gallon - Laboratory Grade",jsmith,2024-01-15T14:30:00Z,Approved after compliance review
AC-IPA-99-1GAL,bullet_point_1,"Old bullet","PURITY (GRADE ONLY IF VERIFIED): 99%+ isopropyl alcohol... (Only include grade if it appears in the Shopify title)",jsmith,2024-01-15T14:30:00Z,
```

### Emergency Rollback Process

```
1. Identify the issue
2. Locate rollback file: data/rollback/rollback_{sku}_{timestamp}.json
3. Execute rollback command
4. Verify original content restored
5. Document incident
6. Investigate root cause
```

---

## 14. CLI Tool Architecture

### Command Overview

| Command | Purpose | Mode |
|---------|---------|------|
| `pull:listings` | Fetch all merchant listings from Amazon | Read-only |
| `pull:item <sku>` | Fetch single listing details from Amazon | Read-only |
| `pull:shopify` | Fetch all products from Shopify | Read-only |
| `pull:shopify-product <sku>` | Fetch single product from Shopify | Read-only |
| `build:facts <sku>` | Generate facts card from Shopify data | Read-only |
| `verify:grade <sku>` | Check if grade claim is allowed for SKU | Read-only |
| `propose:seo <sku>` | Generate SEO proposals via LLM | Read-only |
| `lint:compliance <content>` | Check content for violations | Read-only |
| `apply <sku>` | Apply approved changes to Amazon | Dry-run default |

### Safety Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI SAFETY LAYERS                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Layer 0: SHOPIFY AS SOURCE OF TRUTH                         │
│  ───────────────────────────────────                         │
│  • All product data pulled from Shopify first                │
│  • Grade claims ONLY if present in Shopify title             │
│  • Specs/claims validated against Shopify metafields         │
│                                                              │
│  Layer 1: DEFAULT READ-ONLY                                  │
│  ─────────────────────────                                   │
│  • All commands read-only unless explicitly specified        │
│  • apply command requires --execute flag for writes          │
│                                                              │
│  Layer 2: COMPLIANCE GATE                                    │
│  ────────────────────────                                    │
│  • Blocklist scan runs before any content generation         │
│  • Grade verification against Shopify title                  │
│  • Hard blocks prevent further processing                    │
│  • Warnings require acknowledgment                           │
│                                                              │
│  Layer 3: FACTS-ONLY GENERATION                              │
│  ──────────────────────────────                              │
│  • LLM prompts constrained to Shopify-sourced facts          │
│  • Output validated against facts card                       │
│  • No invented claims allowed                                │
│                                                              │
│  Layer 4: APPROVAL REQUIREMENT                               │
│  ─────────────────────────────                               │
│  • Write operations require matching approval record         │
│  • Approval must match: sku + field + exact new_value        │
│  • No approval = no write                                    │
│                                                              │
│  Layer 5: MANDATORY ROLLBACK                                 │
│  ────────────────────────────                                │
│  • Every --execute creates rollback file                     │
│  • Rollback contains: previous values, timestamp, response   │
│  • Enables quick recovery from any issue                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Environment Configuration

```bash
# Amazon SP-API Credentials
SP_API_CLIENT_ID=your_client_id
SP_API_CLIENT_SECRET=your_client_secret
SP_API_REFRESH_TOKEN=your_refresh_token
SP_API_SELLER_ID=your_seller_id
SP_API_MARKETPLACE_ID=ATVPDKIKX0DER

# Shopify API Credentials (SOURCE OF TRUTH)
SHOPIFY_STORE_URL=alliance-chemical.myshopify.com
SHOPIFY_API_KEY=your_api_key
SHOPIFY_API_SECRET=your_api_secret
SHOPIFY_ACCESS_TOKEN=shpat_xxxxxxxxxxxxx

# LLM Configuration (for propose:seo)
ANTHROPIC_API_KEY=your_anthropic_key
```

### Command: propose:seo

**Purpose**: Generate SEO-optimized content using LLM, constrained to facts card.

**LLM System Prompt**:

```
You are an Amazon listing optimization assistant for Alliance Chemical.

CRITICAL RULES:
1. Use ONLY the facts provided in the facts card below. Do not invent any claims.
2. NEVER use any of these forbidden terms, regardless of context:
   - Antimicrobial claims: disinfect, sanitize, antibacterial, antimicrobial, kills germs, etc.
   - Pesticide claims: repels insects, bug repellent, etc.
   - Absolute safety: non-toxic, chemical-free, completely safe, etc.
   - Health claims: cures, treats, prevents disease, removes allergens, etc.
3. Focus on features, specifications, and applications that ARE in the facts card.
4. Write in a professional, clear tone appropriate for B2B and sophisticated consumers.
5. Include keywords naturally without keyword stuffing.

FACTS CARD:
{facts_card_json}

CURRENT LISTING:
{current_listing}

Generate optimized:
1. Product title (max 200 chars)
2. 5 bullet points (max 250 chars each)
3. Product description (1000-2000 chars)
4. Backend keywords (max 250 bytes)

For each element, note which facts from the card support the content.
```

### Command: lint:compliance

**Purpose**: Scan content for blocklist violations and compliance issues.

**Output Format**:

```
COMPLIANCE CHECK RESULTS
========================

Input: "Industrial strength sanitizer kills 99.9% of bacteria..."

BLOCKED TERMS FOUND (2):
  ❌ "sanitizer" [antimicrobial] at position 20
     Context: "...strength sanitizer kills..."
     
  ❌ "kills 99.9% of bacteria" [antimicrobial] at position 30
     Context: "...sanitizer kills 99.9% of bacteria..."

WARNINGS (1):
  ⚠️ "Industrial strength" - Verify claim is substantiated

STATUS: FAILED
Cannot proceed to approval with blocked terms present.
```

---

## 15. Facts Card System

### 🚨 CRITICAL RULE: GRADES MUST BE IN SHOPIFY TITLE

```
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║   ⛔ DO NOT MENTION ANY PRODUCT GRADE UNLESS IT IS SPECIFICALLY          ║
║      IN THE SHOPIFY PRODUCT TITLE                                        ║
║                                                                          ║
║   This includes:                                                         ║
║   • Laboratory Grade / Lab Grade                                         ║
║   • Technical Grade                                                      ║
║   • Food Grade / FCC Grade                                               ║
║   • ACS Grade / ACS Reagent Grade                                        ║
║   • USP Grade / NF Grade                                                 ║
║   • Pharmaceutical Grade                                                 ║
║   • Industrial Grade                                                     ║
║   • Reagent Grade                                                        ║
║   • HPLC Grade / Spectroscopic Grade                                     ║
║   • Any other grade designation                                          ║
║                                                                          ║
║   ✅ Shopify title: "Citric Acid Food Grade 5lb"                         ║
║      → CAN say "Food Grade" on Amazon                                    ║
║                                                                          ║
║   ❌ Shopify title: "Citric Acid 5lb"                                    ║
║      → CANNOT say ANY grade on Amazon                                    ║
║                                                                          ║
║   NO EXCEPTIONS. NO ASSUMPTIONS. CHECK SHOPIFY FIRST.                    ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
```

### Shopify as the Source of Truth

**Your Shopify store is the master data source.** All product information for Amazon listings should be pulled from or validated against Shopify data via API.

#### Why Shopify First?

1. **Single source of truth** — Product names, grades, specs already vetted
2. **Consistency** — Same claims across all sales channels
3. **Accuracy** — Real data, not guesswork
4. **Automation** — API enables automatic facts card generation

#### Shopify Data to Pull

| Shopify Field | Use For | Priority |
|---------------|---------|----------|
| `title` | Product name, grade verification | **CRITICAL** |
| `body_html` | Description content, specs | High |
| `product_type` | Category mapping | Medium |
| `tags` | Keywords, applications | Medium |
| `variants[].sku` | SKU matching | **CRITICAL** |
| `variants[].title` | Size/variant info | High |
| `variants[].price` | Pricing reference | Medium |
| `variants[].weight` | Shipping calc | Low |
| `metafields` | Custom specs (CAS#, purity, etc.) | **CRITICAL** |
| `vendor` | Brand verification | Low |

#### Shopify API Integration

**Authentication**: Use Shopify Admin API with private app credentials.

```
Required Environment Variables:
- SHOPIFY_STORE_URL=your-store.myshopify.com
- SHOPIFY_API_KEY=your_api_key
- SHOPIFY_API_SECRET=your_api_secret
- SHOPIFY_ACCESS_TOKEN=your_access_token
```

**Key Endpoints:**

```
GET /admin/api/2024-01/products.json          # List all products
GET /admin/api/2024-01/products/{id}.json     # Single product
GET /admin/api/2024-01/products/{id}/metafields.json  # Product metafields
```

#### Grade Verification Flow

```
┌─────────────────────────────────────────────────────────────┐
│                  GRADE VERIFICATION FLOW                     │
└─────────────────────────────────────────────────────────────┘

1. Input: SKU for Amazon listing
          │
          ▼
2. API Call: GET product from Shopify by SKU
          │
          ▼
3. Extract: product.title from Shopify response
          │
          ▼
4. Check: Does title contain grade term?
          │
          ├── YES: "Isopropyl Alcohol 99% Technical Grade"
          │         → Can use "Technical Grade" in Amazon listing
          │
          └── NO:  "Isopropyl Alcohol 99%"
                   → Do NOT add any grade claims to Amazon listing
```

#### Recommended Shopify Metafields for Chemicals

Set up these custom metafields in Shopify to enable richer Amazon listings:

```
Namespace: product_specs
─────────────────────────
• cas_number (single line text)
• purity_percentage (number)
• concentration (single line text)
• physical_form (single line text: Liquid/Solid/Powder/Gas)
• flash_point (single line text)
• ph_level (single line text)
• specific_gravity (number)
• shelf_life (single line text)

Namespace: compliance
─────────────────────────
• certifications (list of text)
• approved_applications (list of text)
• approved_marketing_claims (list of text)
• forbidden_claims (list of text)
• sds_url (URL)
• tds_url (URL)

Namespace: amazon
─────────────────────────
• backend_keywords (multi-line text)
• bullet_1 through bullet_5 (single line text)
• product_type (single line text)
```

#### Shopify → Facts Card Mapping

When generating a facts card, pull from Shopify:

```json
{
  "sku": "← variants[].sku",
  "product_name": "← title (AUTHORITATIVE FOR GRADE CLAIMS)",
  "chemical_name": "← metafields.product_specs.chemical_name",
  "cas_number": "← metafields.product_specs.cas_number",
  
  "specifications": {
    "purity": "← metafields.product_specs.purity_percentage",
    "concentration": "← metafields.product_specs.concentration",
    "physical_form": "← metafields.product_specs.physical_form"
  },
  
  "certifications": "← metafields.compliance.certifications",
  "applications": "← metafields.compliance.approved_applications",
  "approved_marketing_claims": "← metafields.compliance.approved_marketing_claims",
  
  "keywords": {
    "primary": "← extracted from title",
    "secondary": "← tags",
    "backend": "← metafields.amazon.backend_keywords"
  }
}
```

### Purpose

The facts card is the single source of truth for all claims that can be made about a product. If a fact isn't in the card, it cannot appear in the listing.

### Facts Card Schema

```json
{
  "sku": "AC-12345",
  "asin": "B0XXXXXXXXX",
  "product_name": "Official Product Name",
  "brand": "Alliance Chemical",
  
  "chemical_identity": {
    "chemical_name": "Common chemical name",
    "iupac_name": "IUPAC systematic name (if applicable)",
    "cas_number": "CAS registry number",
    "other_names": ["Synonym 1", "Synonym 2"]
  },
  
  "specifications": {
    "purity": "99.5%",
    "concentration": "If solution, concentration %",
    "grade": "ONLY if in Shopify title — otherwise NULL/omit",
    "appearance": "Clear colorless liquid",
    "odor": "Characteristic alcohol odor",
    "ph": "7.0 (if applicable)",
    "specific_gravity": "0.785",
    "boiling_point": "82°C",
    "flash_point": "12°C",
    "solubility": "Miscible with water"
  },
  
  "packaging": {
    "container_type": "HDPE bottle",
    "sizes_available": ["1 Gallon", "5 Gallon", "55 Gallon"],
    "units_per_case": 4,
    "shipping_weight": "8.5 lbs"
  },
  
  "applications": [
    "Electronics cleaning",
    "Flux removal",
    "Surface preparation",
    "Laboratory solvent",
    "General degreasing"
  ],
  
  "certifications": [
    "ACS Reagent Grade",
    "NSF Registered (Category Code)"
  ],
  
  "compatible_materials": [
    "Stainless steel",
    "Aluminum", 
    "Glass",
    "Most plastics (test first)"
  ],
  
  "incompatible_materials": [
    "Certain rubbers",
    "Some plastics - test first"
  ],
  
  "storage": {
    "temperature": "Store at 59-86°F (15-30°C)",
    "conditions": "Keep container tightly closed",
    "shelf_life": "2 years from manufacture date",
    "special_requirements": "Keep away from heat, sparks, open flame"
  },
  
  "safety_summary": {
    "signal_word": "Danger",
    "primary_hazards": ["Flammable liquid", "Eye irritant"],
    "ppe_required": ["Safety glasses", "Gloves", "Ventilation"]
  },
  
  "approved_marketing_claims": [
    "High-purity formula for consistent results",
    "Fast-evaporating solvent",
    "Professional-grade quality",
    "Versatile industrial solvent"
  ],
  
  "keywords": {
    "primary": ["isopropyl alcohol", "IPA", "99% alcohol"],
    "secondary": ["isopropanol", "2-propanol", "rubbing alcohol"],
    "application": ["electronics cleaner", "flux remover", "degreaser"],
    "long_tail": ["isopropyl alcohol for electronics", "IPA solvent"]
  },
  
  "sds_link": "URL to Safety Data Sheet",
  "tds_link": "URL to Technical Data Sheet",
  
  "last_updated": "2024-01-15",
  "updated_by": "compliance_team"
}
```

### Facts Card Maintenance

**Update Triggers:**
- New certification obtained
- Specification change
- New application validated
- SDS revision
- Marketing claim approval

**Update Process:**
1. Identify change needed
2. Verify with documentation (SDS, TDS, cert)
3. Update facts card JSON
4. Run lint:compliance on affected listings
5. Queue listings for re-optimization if needed

---

## 16. Examples: Allowed vs Forbidden Wording

### Example 1: Degreasing Products

**Scenario**: Selling an industrial degreaser

**❌ FORBIDDEN:**
```
"This powerful degreaser sanitizes and disinfects surfaces while removing tough grease. 
Kills 99.9% of bacteria for a clean, germ-free workspace. 
Non-toxic and eco-friendly formula is safe for all surfaces."
```

**Problems:**
- "sanitizes" — antimicrobial claim
- "disinfects" — antimicrobial claim
- "Kills 99.9% of bacteria" — antimicrobial claim
- "germ-free" — antimicrobial claim
- "Non-toxic" — absolute safety claim
- "eco-friendly" — unsubstantiated environmental claim
- "safe for all surfaces" — absolute claim

**✅ ALLOWED:**
```
"This heavy-duty industrial degreaser effectively removes oil, grease, carbon deposits, 
and other petroleum-based soils from metal surfaces. Fast-acting formula cuts through 
tough residue, reducing cleaning time in manufacturing and maintenance applications. 
Compatible with steel, aluminum, and most industrial equipment when used as directed."
```

**Why it works:**
- Describes cleaning action (removes, cuts through)
- Specific to soil types (oil, grease, carbon)
- Qualified claims (when used as directed)
- Application-focused (manufacturing, maintenance)
- Material compatibility stated

---

### Example 2: Acid-Based Cleaners

**Scenario**: Selling phosphoric acid for rust removal

**❌ FORBIDDEN:**
```
"Phosphoric acid descaler kills bacteria and removes scale buildup in one step. 
Sanitizes pipes and equipment while descaling. Prevents mold and mildew growth. 
Safe, non-toxic formula."
```

**Problems:**
- "kills bacteria" — antimicrobial claim
- "Sanitizes" — antimicrobial claim
- "Prevents mold and mildew growth" — antimicrobial claim
- "Safe, non-toxic" — absolute safety claims (especially for an acid!)

**✅ ALLOWED:**
```
"Phosphoric acid solution for removing rust, scale, and mineral deposits from metal 
surfaces and equipment. Effective on calcium, lime, and rust buildup in pipes, 
tanks, and industrial machinery. Dissolves hard water scale to restore proper flow 
and function. Technical grade suitable for industrial and manufacturing applications. 
Always use appropriate PPE and follow SDS guidelines."
```

**Why it works:**
- Focuses on mineral/inorganic removal
- No organism claims
- Includes safety guidance
- Technical/industrial positioning

---

### Example 3: Alcohol Products

**Scenario**: Selling isopropyl alcohol

**❌ FORBIDDEN:**
```
"Medical-grade isopropyl alcohol sanitizes and disinfects surfaces on contact. 
Kills germs, bacteria, and viruses. Antibacterial formula prevents infection. 
Hospital-grade disinfectant. Safe and non-toxic."
```

**Problems:**
- "Medical-grade" — likely false unless certified
- "sanitizes" — antimicrobial claim
- "disinfects" — antimicrobial claim
- "Kills germs, bacteria, and viruses" — antimicrobial claims
- "Antibacterial" — antimicrobial claim
- "prevents infection" — medical claim
- "Hospital-grade disinfectant" — antimicrobial claim
- "Safe and non-toxic" — absolute safety claims

**✅ ALLOWED:**
```
"High-purity 99% isopropyl alcohol (IPA) for precision cleaning and solvent applications. 
Ideal for electronics cleaning, flux removal, surface preparation, and degreasing. 
Fast-evaporating formula leaves no residue on most surfaces. Technical grade suitable 
for industrial, laboratory, and professional applications. Store away from heat and 
open flame."
```

**Why it works:**
- Accurate purity claim
- Focus on cleaning/solvent properties
- No organism claims
- Application-specific
- Includes appropriate safety note

---

### Example 4: Water Treatment Chemicals

**Scenario**: Selling a pH adjustment chemical

**❌ FORBIDDEN:**
```
"Water treatment chemical kills harmful bacteria and purifies water. Prevents algae 
growth and eliminates waterborne pathogens. Makes water safe for drinking and swimming. 
Eco-friendly and non-toxic."
```

**Problems:**
- "kills harmful bacteria" — antimicrobial claim
- "purifies water" — implies pathogen removal
- "Prevents algae growth" — antimicrobial claim
- "eliminates waterborne pathogens" — antimicrobial claim
- "safe for drinking" — safety claim
- "Eco-friendly and non-toxic" — unsubstantiated claims

**✅ ALLOWED:**
```
"Sodium bisulfate pH decreaser for water chemistry adjustment in pools, spas, 
and industrial water systems. Dry acid formula effectively lowers pH and total 
alkalinity. Granular form dissolves quickly for easy application. Compatible 
with standard pool and spa equipment. Follow product label and test water 
chemistry before and after treatment."
```

**Why it works:**
- Focus on pH chemistry, not organisms
- Application-specific (pools, industrial)
- Physical properties described
- Usage guidance included
- No health claims

---

### Example 5: General Industrial Chemicals

**Scenario**: Selling sodium hydroxide (caustic soda)

**❌ FORBIDDEN:**
```
"Powerful cleaner kills all germs and bacteria. Safe, non-toxic caustic soda 
removes everything. Chemical-free cleaning for a healthier home. Best quality 
guaranteed - better than competitors."
```

**Problems:**
- "kills all germs and bacteria" — antimicrobial claim
- "Safe, non-toxic" — absolutely false for caustic soda!
- "Chemical-free" — impossible claim
- "healthier home" — health claim
- "Best quality guaranteed" — unsubstantiated
- "better than competitors" — unsubstantiated comparison

**✅ ALLOWED:**
```
"Industrial-grade sodium hydroxide (caustic soda) flakes, 99% purity. Versatile 
chemical for soap making, drain cleaning, food processing, and manufacturing 
applications. Highly alkaline - effective for heavy-duty cleaning and degreasing. 
Technical grade suitable for industrial processes. Caustic material - always use 
appropriate PPE including chemical-resistant gloves and eye protection. Keep away 
from acids."
```

**Why it works:**
- Accurate specification (99% purity)
- Legitimate applications listed
- Appropriate hazard warning included
- No safety misrepresentation
- Technical positioning

---

## 17. Competitive Analysis Framework

### Safe Competitive Research

**DO analyze:**
- Competitor keyword usage (visible and backend)
- Product title structures
- Bullet point organization
- Price positioning
- Image strategies
- Review themes (what customers value)

**DO NOT copy:**
- Any text verbatim
- Potentially forbidden claims (even if competitors use them)
- Competitor brand names or trademarked terms

### Competitor Analysis Template

```
COMPETITOR ANALYSIS - [Product Category]
========================================

Competitor 1: [Name]
ASIN: [ASIN]
Price: $XX.XX
Rating: X.X stars (XXX reviews)

Title Structure:
[Break down their title components]

Keywords Identified:
[List keywords they're targeting]

Claims Made:
[List claims - flag any that appear non-compliant]

Review Themes:
+ Positive: [What customers like]
- Negative: [What customers complain about]

COMPLIANCE CHECK:
⚠️ Potential violations observed:
[List any forbidden terms they use - DO NOT COPY THESE]

LEARNINGS TO APPLY:
[What can we legally and safely learn from this?]
```

### Turning Competitor Insights into Safe Content

**If competitor says**: "Kills 99.9% of germs and bacteria"

**You CANNOT say**: Anything similar (antimicrobial claim)

**You CAN say**: Nothing — find a different angle

---

**If competitor says**: "Non-toxic and safe for kids"

**You CANNOT say**: "Non-toxic" or unqualified safety claims

**You CAN say**: "When used as directed by adults, suitable for household cleaning tasks"

---

**If competitor says**: "Best quality on Amazon"

**You CANNOT say**: "Best" or unsubstantiated superlatives

**You CAN say**: "99.5%+ purity verified by independent testing" (if true and documented)

---

## 18. Performance Metrics & KPIs

### Key Metrics to Track

| Metric | What It Measures | Target |
|--------|-----------------|--------|
| Organic Search Rank | Visibility for target keywords | Top 20 |
| Click-Through Rate (CTR) | Title/image effectiveness | >0.5% |
| Conversion Rate | Listing persuasiveness | >10% |
| Sessions | Traffic volume | Increasing |
| Page Views | Interest level | Increasing |
| Buy Box % | Pricing competitiveness | >90% |
| Review Rating | Customer satisfaction | >4.0 stars |
| Review Count | Social proof volume | Increasing |

### Optimization Impact Tracking

**Before/After Template:**

```
SKU: [SKU]
Optimization Date: [Date]

CHANGES MADE:
- Title: [Old] → [New]
- Bullets: [Summary of changes]
- Backend: [Summary of changes]

30-DAY COMPARISON:
                Before      After       Change
Sessions:       XXX         XXX         +XX%
Page Views:     XXX         XXX         +XX%
Units Sold:     XXX         XXX         +XX%
Conversion:     X.X%        X.X%        +X.X%
Avg Position:   XX          XX          -X

KEYWORD RANKING CHANGES:
[keyword 1]: Position XX → XX
[keyword 2]: Position XX → XX

NOTES:
[Any observations or learnings]
```

### Warning Signs to Monitor

| Warning Sign | Possible Cause | Action |
|--------------|---------------|--------|
| Sudden rank drop | Policy violation, algorithm change | Review listing for issues |
| Listing suppression | Forbidden term detected | Immediate compliance audit |
| Increased returns | Inaccurate description | Review content accuracy |
| Negative reviews citing claims | Overpromising | Revise to be more accurate |
| Account health alert | Multiple violations | Escalate to compliance team |

---

## 19. Troubleshooting Common Issues

### Issue: Listing Suppressed

**Possible Causes:**
1. Forbidden term in content
2. Restricted product category
3. Missing required information
4. Image policy violation
5. Hazmat classification issue

**Resolution Steps:**
1. Check Seller Central for specific error
2. Run lint:compliance on all content
3. Review against complete blocklist
4. Check category requirements
5. Verify hazmat documentation

---

### Issue: Keyword Not Ranking

**Possible Causes:**
1. Keyword not indexed
2. High competition
3. Poor relevance signals
4. Low sales velocity

**Resolution Steps:**
1. Verify keyword is in listing (title, bullets, backend)
2. Check keyword isn't blocked by Amazon
3. Ensure product is relevant to keyword
4. Consider PPC to build relevance

---

### Issue: Low Conversion Rate

**Possible Causes:**
1. Poor main image
2. Price too high
3. Weak bullet points
4. Missing key information
5. Negative reviews

**Resolution Steps:**
1. A/B test main image
2. Review competitor pricing
3. Strengthen value proposition in bullets
4. Add missing specs/info
5. Address review concerns in content

---

### Issue: Content Rejected by Amazon

**Possible Causes:**
1. Forbidden terms detected
2. Prohibited claims
3. HTML formatting errors
4. Character limit exceeded
5. Category restrictions

**Resolution Steps:**
1. Review Amazon's specific rejection reason
2. Run compliance check
3. Verify formatting
4. Check character/byte counts
5. Review category-specific guidelines

---

## 20. Appendices

### Appendix A: Amazon Marketplace IDs

| Marketplace | Country | ID |
|-------------|---------|-----|
| amazon.com | USA | ATVPDKIKX0DER |
| amazon.ca | Canada | A2EUQ1WTGCTBG2 |
| amazon.com.mx | Mexico | A1AM78C64UM0Y8 |
| amazon.co.uk | UK | A1F83G8C2ARO7P |
| amazon.de | Germany | A1PA6795UKMFR9 |
| amazon.fr | France | A13V1IB3VIYBER |
| amazon.it | Italy | APJ6JRA9NG5V4 |
| amazon.es | Spain | A1RKKUPIHCS9HS |

### Appendix B: Character/Byte Limits

| Field | Limit | Notes |
|-------|-------|-------|
| Product Title | 200 chars | 80 visible on mobile |
| Bullet Points | 500 chars each | 200-250 recommended |
| Product Description | 2000 chars | HTML allowed |
| Backend Keywords | 250 bytes | Bytes, not characters |
| A+ Content | Varies by module | Check module specs |

### Appendix C: Regulatory Quick Links

- **EPA Pesticide Registration**: https://www.epa.gov/pesticide-registration
- **FDA Drug Definition**: https://www.fda.gov/drugs
- **FTC Green Guides**: https://www.ftc.gov/green-guides
- **Amazon Restricted Products**: Seller Central > Program Policies
- **Amazon Chemical Policy**: Seller Central > Product Compliance

### Appendix D: Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2024-01 | E-Commerce Team | Initial release |

---

## Final Notes

This document should be treated as a living reference. Update it as:
- New regulations emerge
- Amazon policies change
- New forbidden terms are identified
- Processes improve

**Remember the core principle:**

```
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║   When in doubt, leave it out.                                     ║
║                                                                    ║
║   No SEO improvement is worth a listing suspension,                ║
║   regulatory fine, or legal liability.                             ║
║                                                                    ║
║   Safety and compliance ALWAYS come first.                         ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
```

---

*End of Document*

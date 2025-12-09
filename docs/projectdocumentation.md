# Product Marketing Content Generation System
## Project Documentation

---

## 1. Problem Statement

Modern e-commerce requires consistent, high-quality marketing content for product pages. Creating this content manually is:
- **Time-consuming**: Each product needs FAQs, descriptions, and comparison content
- **Inconsistent**: Different writers produce varying quality and style  
- **Expensive**: Skilled copywriters are costly to hire at scale
- **Repetitive**: Similar products require similar content structures

### The Challenge

Given a single product's data (e.g., a skincare serum), automatically generate:
1. **FAQ Page** with 15+ categorized questions and answers
2. **Product Page** with marketing copy, benefits, and specifications
3. **Comparison Page** against a fictional competitor

All outputs must be clean, machine-readable JSON without manual intervention.

---

## 2. Solution Overview

An **autonomous multi-agent system** where specialized AI agents collaborate to generate marketing content. Each agent has a focused responsibility, enabling modularity, testability, and extensibility.

### Key Features

| Feature | Description |
|---------|-------------|
| **Multi-Agent Architecture** | 5 specialized agents orchestrated by a coordinator |
| **Template-Based Generation** | Explicit templates ensure consistent output structure |
| **Reusable Content Blocks** | Shared transformation functions for data formatting |
| **Schema Validation** | Pydantic models enforce data integrity |
| **Flexible LLM Backend** | Supports Groq and Gemini with easy switching |

### Output

```
Input: glowboost.json (product data)
         ↓
   [Agent Pipeline]
         ↓
Output: faq.json, product_page.json, comparison_page.json
```

---

## 3. Scope & Assumptions

### In Scope

- Single-product content generation
- Three page types: FAQ, Product, Comparison
- Skincare/cosmetics product domain
- JSON input and output format
- Fictional competitor generation for comparison

### Out of Scope

- Multi-product batch processing
- Real competitor research (web scraping)
- Image generation or visual assets
- Multi-language support
- Direct CMS integration

### Assumptions

1. **Input data is complete** - Product JSON contains all required fields
2. **LLM is available** - Groq or Gemini API accessible with valid key
3. **Single product focus** - One product per execution
4. **English only** - All content generated in English
5. **No external data** - Comparison uses AI-generated fictional product, not real competitors

---

## 4. System Design

### 4.1 High-Level Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                           ENTRY POINT (main.py)                             │
│                    Parses args, loads config, initializes                   │
└───────────────────────────────────┬────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                         COORDINATOR AGENT                                   │
│                  Orchestrates 7-step workflow                               │
└──────┬───────────┬───────────┬───────────┬───────────┬─────────────────────┘
       │           │           │           │           │
       ▼           ▼           ▼           ▼           ▼
  ┌────────┐ ┌──────────┐ ┌─────────┐ ┌─────────┐ ┌──────────┐
  │  Data  │ │ Question │ │ Product │ │ Content │ │ Quality  │
  │Extract │ │Generator │ │ Creator │ │Generator│ │Validator │
  └────────┘ └──────────┘ └─────────┘ └─────────┘ └──────────┘
       │           │           │           │           │
       └───────────┴───────────┴─────┬─────┴───────────┘
                                     │
                ┌────────────────────┼────────────────────┐
                ▼                    ▼                    ▼
         ┌──────────┐         ┌──────────┐         ┌──────────┐
         │Templates │         │ Content  │         │ Schemas  │
         │(structure)│         │ Blocks   │         │(Pydantic)│
         └──────────┘         │(transform)│         └──────────┘
                              └──────────┘
```

### 4.2 Agent Workflow (Sequence Diagram)

```
┌─────────┐  ┌────────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐
│  Main   │  │Coordinator │  │  Data     │  │ Question  │  │  Product  │  │  Content  │
│         │  │   Agent    │  │ Extractor │  │ Generator │  │  Creator  │  │ Generator │
└────┬────┘  └─────┬──────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘
     │             │               │              │              │              │
     │ run(input)  │               │              │              │              │
     │────────────>│               │              │              │              │
     │             │               │              │              │              │
     │             │ Step 1: run() │              │              │              │
     │             │──────────────>│              │              │              │
     │             │  ProductData  │              │              │              │
     │             │<──────────────│              │              │              │
     │             │               │              │              │              │
     │             │ Step 2: run(ProductData)     │              │              │
     │             │──────────────────────────────>│              │              │
     │             │     CategorizedQuestions     │              │              │
     │             │<──────────────────────────────│              │              │
     │             │               │              │              │              │
     │             │ Step 3: run(ProductData)     │              │              │
     │             │───────────────────────────────────────────>│              │
     │             │              ProductData (B)               │              │
     │             │<───────────────────────────────────────────│              │
     │             │               │              │              │              │
     │             │ Step 4-6: run(task, data)    │              │              │
     │             │──────────────────────────────────────────────────────────>│
     │             │    FAQPage, ProductPage, ComparisonPage                   │
     │             │<──────────────────────────────────────────────────────────│
     │             │               │              │              │              │
     │  results    │               │              │              │              │
     │<────────────│               │              │              │              │
     │             │               │              │              │              │
```

### 4.3 Data Flow

```
┌──────────────────┐
│  Input JSON      │
│  (glowboost)     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  ProductData     │◄─── Pydantic Validation
│  (Schema)        │
└────────┬─────────┘
         │
    ┌────┴────────────────────────────┐
    │                                 │
    ▼                                 ▼
┌──────────────────┐         ┌──────────────────┐
│  Product A       │         │  Product B       │
│  (Original)      │         │  (AI Generated)  │
└────────┬─────────┘         └────────┬─────────┘
         │                            │
         └───────────┬────────────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
    ▼                ▼                ▼
┌────────┐     ┌──────────┐     ┌────────────┐
│  FAQ   │     │  Product │     │ Comparison │
│  Page  │     │   Page   │     │    Page    │
└────────┘     └──────────┘     └────────────┘
    │                │                │
    ▼                ▼                ▼
┌────────────────────────────────────────────┐
│              JSON Output Files              │
│   faq.json  product_page.json  comparison_page.json │
└────────────────────────────────────────────┘
```

### 4.4 Component Relationships

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            AGENT LAYER                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ BaseAgent   │◄─┤ Coordinator │  │  Question   │  │ ContentGenerator    │ │
│  │ (Abstract)  │  │   Agent     │  │  Generator  │  │ uses: Templates +   │ │
│  │             │◄─┤             │  │             │  │      ContentBlocks  │ │
│  │             │◄─┤ DataExtract │  │ ProductCreator │                     │ │
│  │             │◄─┤ QualityValid│  │             │  │                     │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          INFRASTRUCTURE LAYER                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ LLM Provider│  │  Templates  │  │   Content   │  │     Schemas         │ │
│  │ (Groq/Gemini)│ │ (FAQ, Prod, │  │   Blocks    │  │   (Pydantic)        │ │
│  │             │  │  Comparison)│  │ (Formatting)│  │                     │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.5 Design Patterns Used

| Pattern | Where | Purpose |
|---------|-------|---------|
| **Template Method** | BaseAgent | Standardizes agent lifecycle (validate → execute → format) |
| **Strategy** | LLMProvider | Swappable LLM backends (Groq, Gemini) |
| **Orchestrator** | CoordinatorAgent | Manages workflow and agent calling order |
| **Builder** | Templates | Constructs complex page structures step-by-step |

### 4.6 API Call Strategy

```
Step 1: DataExtractor      ─── No API (local validation)
Step 2: QuestionGenerator  ─── 1 API call (15 questions)
Step 3: ProductCreator     ─── 1 API call (fictional product)
Step 4: FAQ Generation     ─── 1 API call (or uses Step 2 output)
Step 5: Product Page       ─── 1 API call (marketing copy)
Step 6: Comparison Page    ─── 1 API call (comparison content)
Step 7: QualityValidator   ─── No API (local checks)
─────────────────────────────────────────────────────────
Total: 4-5 API calls per execution (optimized for rate limits)
```

---

## 5. Running the System

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
export GROQ_API_KEY=your_key_here

# Run
python src/main.py --input examples/glowboost.json --output-dir output
```

---

**Author:** Gopi Chand  
**Project:** Kasparro Applied AI Engineer Challenge  
**Date:** December 2025

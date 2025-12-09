# Product Marketing Content Generation System

A modular multi-agent system that generates marketing content pages for skincare products using AI-powered analysis.

## 🎯 Overview

This system demonstrates a sophisticated multi-agent architecture that:
- **Parses product data** into a clean internal model
- **Generates 15+ categorized user questions** (Informational, Safety, Usage, Purchase, Comparison)
- **Creates a fictional competitor product** for comparison
- **Produces 3 structured JSON pages**: FAQ, Product Page, Comparison Page

## 🏗️ Architecture

```
                         ┌─────────────────────┐
                         │  Coordinator Agent  │
                         │   (Orchestrator)    │
                         └──────────┬──────────┘
                                    │
    ┌───────────┬───────────┬───────┼───────┬───────────┐
    │           │           │       │       │           │
┌───▼───┐ ┌─────▼─────┐ ┌───▼───┐ ┌─▼─┐ ┌───▼───┐ ┌─────▼─────┐
│ Data  │ │ Question  │ │Product│ │FAQ│ │Product│ │  Quality  │
│Extract│ │ Generator │ │Creator│ │Gen│ │ Page  │ │ Validator │
└───────┘ └───────────┘ └───────┘ └───┘ └───────┘ └───────────┘
```

### Agent Responsibilities

| Agent | Role |
|-------|------|
| **Coordinator** | Orchestrates the 7-step workflow |
| **DataExtractor** | Parses input JSON into ProductData schema |
| **QuestionGenerator** | Creates 15+ categorized questions |
| **ProductCreator** | Generates fictional Product B |
| **ContentGenerator** | Produces FAQ, Product, Comparison pages |
| **QualityValidator** | Validates output structure and content |

## 📦 Product Data Format

The system accepts product data in this format:

```json
{
    "Product Name": "GlowBoost Vitamin C Serum",
    "Concentration": "10% Vitamin C",
    "Skin Type": "Oily, Combination",
    "Key Ingredients": "Vitamin C, Hyaluronic Acid",
    "Benefits": "Brightening, Fades dark spots",
    "How to Use": "Apply 2–3 drops in the morning before sunscreen",
    "Side Effects": "Mild tingling for sensitive skin",
    "Price": "₹699"
}
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Google Gemini API Key

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### Running the System

```bash
python src/main.py --input examples/glowboost.json --output-dir output
```

### Output

The system generates 3 JSON files in the output directory:
1. `faq.json` - FAQ page with 5+ Q&As
2. `product_page.json` - Product description page
3. `comparison_page.json` - GlowBoost vs fictional Product B

## 📁 Project Structure

```
├── src/
│   ├── agents/                   # Agent implementations
│   │   ├── base_agent.py         # Abstract base class
│   │   ├── coordinator.py        # Workflow orchestrator
│   │   ├── data_extractor.py     # Input parsing
│   │   ├── question_generator.py # 15+ categorized questions
│   │   ├── product_creator.py    # Fictional product creation
│   │   ├── content_generator.py  # Page content generation
│   │   └── quality_validator.py  # Output validation
│   ├── templates/                # Page templates
│   │   ├── faq_template.py
│   │   ├── product_page_template.py
│   │   └── comparison_template.py
│   ├── schemas/                  # Pydantic data models
│   │   └── output_schema.py
│   ├── utils/                    # Utilities
│   │   ├── config.py
│   │   ├── logger.py
│   │   ├── state_manager.py
│   │   └── content_blocks.py     # Reusable content logic
│   └── main.py                   # Entry point
├── examples/                     # Sample input files
│   └── glowboost.json
├── output/                       # Generated outputs
├── config.yaml                   # Configuration
└── requirements.txt
```

## 📊 Output Examples

### FAQ Page (faq.json)
```json
{
  "product_name": "GlowBoost Vitamin C Serum",
  "faqs": [
    {"question": "What is GlowBoost?", "answer": "..."},
    {"question": "Is it safe for sensitive skin?", "answer": "..."}
  ]
}
```

### Comparison Page (comparison_page.json)
```json
{
  "product_a_name": "GlowBoost Vitamin C Serum",
  "product_b_name": "[Fictional Competitor]",
  "comparison_table": [...],
  "verdict": "..."
}
```

## 🔧 Configuration

Edit `config.yaml` to customize:
- Gemini model and parameters
- Agent-specific settings
- Logging levels

## ✅ Assignment Requirements Met

- ✅ Parse & understand product data
- ✅ Auto-generate 15+ categorized questions
- ✅ Define explicit templates (FAQ, Product, Comparison)
- ✅ Create reusable content logic blocks
- ✅ Assemble 3 pages via multi-agent pipeline
- ✅ Output clean, machine-readable JSON
- ✅ Fictional Product B for comparison

---

**Built for Kasparro - Applied AI Engineer Challenge**  
**Author:** Gopi Chand

"""
Coordinator Agent

Orchestrates the Product Marketing Content workflow with proper template and content block integration:
1. Extract Product Data (GlowBoost) - No API, uses Pydantic validation
2. Generate Categorized Questions - API call, feeds into FAQ generation
3. Create Fictional Competitor (Product B) - API call
4. Generate FAQ Page - API call + FAQTemplate + content_blocks
5. Generate Product Page - API call + ProductPageTemplate + content_blocks
6. Generate Comparison Page - API call + ComparisonTemplate + content_blocks
7. Quality Validation - No API, validates all outputs

Total: 5 API calls (optimized for rate limiting)
"""

from typing import Dict, Any
from datetime import datetime
import time
from utils import StateManager
from agents.base_agent import BaseAgent
from agents.data_extractor import DataExtractionAgent
from agents.question_generator import QuestionGeneratorAgent
from agents.product_creator import ProductCreatorAgent
from agents.content_generator import ContentGenerationAgent
from agents.quality_validator import QualityValidationAgent


class CoordinatorAgent(BaseAgent):
    """
    Main orchestrator for the marketing content system.
    
    Coordinates 5 worker agents in a 7-step workflow:
    - DataExtractionAgent: Parses input JSON
    - QuestionGeneratorAgent: Creates 15+ categorized questions
    - ProductCreatorAgent: Generates fictional competitor
    - ContentGenerationAgent: Creates FAQ, Product, Comparison pages
    - QualityValidationAgent: Validates all outputs
    """
    
    def __init__(self, state_manager: StateManager, config: Dict[str, Any] = None):
        super().__init__("Coordinator", state_manager, config)
        
        # Initialize all 5 worker agents
        self.data_extractor = DataExtractionAgent(state_manager)
        self.question_generator = QuestionGeneratorAgent(state_manager)
        self.product_creator = ProductCreatorAgent(state_manager)
        self.content_generator = ContentGenerationAgent(state_manager)
        self.quality_validator = QualityValidationAgent(state_manager)
        
        self.logger.info("Coordinator initialized with 5 worker agents")

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the full 7-step workflow.
        
        Steps:
        1. Data Extraction (no API)
        2. Question Generation (API call 1)
        3. Product B Creation (API call 2)
        4. FAQ Page Generation (API call 3)
        5. Product Page Generation (API call 4)
        6. Comparison Page Generation (API call 5)
        7. Quality Validation (no API)
        """
        workflow_id = f"marketing_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.log_decision("Starting marketing content workflow", {"workflow_id": workflow_id})
        
        def wait():
            self.logger.info("Waiting 5s between API calls...")
            time.sleep(5)
        
        # =====================================================================
        # STEP 1: Extract Data (No API)
        # =====================================================================
        self.logger.info("\n" + "="*60)
        self.logger.info("STEP 1: Data Extraction (Product A)")
        self.logger.info("="*60)
        product_a = self.data_extractor.run(input_data)
        self.logger.info(f"✓ Extracted: {product_a.product_name}")
        
        # =====================================================================
        # STEP 2: Generate Categorized Questions (API Call 1)
        # =====================================================================
        self.logger.info("\n" + "="*60)
        self.logger.info("STEP 2: Generating Categorized Questions (15+)")
        self.logger.info("="*60)
        
        try:
            categorized_questions = self.question_generator.run(product_a)
            total_questions = sum(len(q) for q in categorized_questions.values())
            self.logger.info(f"✓ Generated {total_questions} questions across {len(categorized_questions)} categories")
        except Exception as e:
            self.logger.warning(f"Question generation failed, will use extended FAQ: {e}")
            categorized_questions = None
        
        wait()
        
        # =====================================================================
        # STEP 3: Create Product B (API Call 2)
        # =====================================================================
        self.logger.info("\n" + "="*60)
        self.logger.info("STEP 3: Creating Fictional Competitor")
        self.logger.info("="*60)
        product_b = self.product_creator.run(product_a)
        self.logger.info(f"✓ Created: {product_b.product_name}")
        wait()
        
        # =====================================================================
        # STEP 4: Generate FAQ Page (API Call 3)
        # Uses: QuestionGeneratorAgent output + FAQTemplate + content_blocks
        # =====================================================================
        self.logger.info("\n" + "="*60)
        self.logger.info("STEP 4: Generating FAQ Page (15+ questions)")
        self.logger.info("="*60)
        
        if categorized_questions:
            # Use pre-generated categorized questions
            faq_page = self.content_generator.run({
                'task': 'faq',
                'data': product_a,
                'questions': categorized_questions
            })
        else:
            # Fallback: generate extended FAQ directly
            faq_page = self.content_generator.run({
                'task': 'faq_extended',
                'data': product_a
            })
        
        self.logger.info(f"✓ FAQ Page: {len(faq_page.faqs)} Q&As")
        wait()
        
        # =====================================================================
        # STEP 5: Generate Product Page (API Call 4)
        # Uses: ProductPageTemplate + content_blocks
        # =====================================================================
        self.logger.info("\n" + "="*60)
        self.logger.info("STEP 5: Generating Product Page")
        self.logger.info("="*60)
        product_page = self.content_generator.run({'task': 'product_page', 'data': product_a})
        self.logger.info("✓ Product Page generated")
        wait()
        
        # =====================================================================
        # STEP 6: Generate Comparison Page (API Call 5)
        # Uses: ComparisonTemplate + content_blocks (build_comparison_table)
        # =====================================================================
        self.logger.info("\n" + "="*60)
        self.logger.info("STEP 6: Generating Comparison Page")
        self.logger.info("="*60)
        comparison_page = self.content_generator.run({
            'task': 'comparison',
            'data': {'product_a': product_a, 'product_b': product_b}
        })
        self.logger.info(f"✓ Comparison: {product_a.product_name} vs {product_b.product_name}")
        
        # =====================================================================
        # STEP 7: Quality Validation (No API)
        # =====================================================================
        self.logger.info("\n" + "="*60)
        self.logger.info("STEP 7: Quality Validation")
        self.logger.info("="*60)
        validation = self.quality_validator.run({
            "faq": faq_page,
            "product_page": product_page,
            "comparison": comparison_page
        })
        self.logger.info(f"✓ Validation: {validation['status']}")
        
        return {
            "faq_page": faq_page,
            "product_page": product_page,
            "comparison_page": comparison_page,
            "validation": validation,
            "metadata": {
                "workflow_id": workflow_id,
                "faq_count": len(faq_page.faqs),
                "product_a": product_a.product_name,
                "product_b": product_b.product_name,
                "questions_generated": total_questions if categorized_questions else "extended",
                "api_calls": 5
            }
        }

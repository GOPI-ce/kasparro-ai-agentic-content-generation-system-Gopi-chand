"""
Content Generation Agent

Responsible for generating marketing content pages (FAQ, Product Page, Comparison).
Uses:
- LLM provider for AI-generated content
- Templates for structured output formatting
- Content blocks for reusable transformations
"""

from typing import Dict, Any, List
import json
import os
from schemas import ProductData, FAQPage, ProductPage, ComparisonPage, FAQItem, ProductSpec, ComparisonRow
from utils import StateManager, get_config
from agents.base_agent import BaseAgent

# Import templates
from templates.faq_template import FAQTemplate
from templates.product_page_template import ProductPageTemplate
from templates.comparison_template import ComparisonTemplate

# Import content blocks
from utils.content_blocks import (
    format_price,
    generate_benefit_bullets,
    build_comparison_table,
    format_ingredients,
    categorize_benefits
)


class ContentGenerationAgent(BaseAgent):
    """
    Agent for generating marketing content using LLM + templates + content blocks.
    
    Flow for each page type:
    1. LLM generates raw content based on product data
    2. Content blocks transform/format specific fields
    3. Templates structure the final output
    """
    
    def __init__(self, state_manager: StateManager, config: Dict[str, Any] = None):
        super().__init__("ContentGenerator", state_manager, config)
        
        self.mock_mode = os.getenv("MOCK_MODE", "false").lower() == "true"
        
        if not self.mock_mode:
            from utils.llm_provider import get_llm_provider
            self.llm = get_llm_provider()
        else:
            self.llm = None
            self.logger.info("Running in MOCK MODE")

    def execute(self, input_data: Any) -> Any:
        task = input_data.get('task')
        data = input_data.get('data')
        questions = input_data.get('questions')  # Categorized questions from QuestionGenerator
        
        if task == 'faq':
            return self.generate_faq(data, questions)
        elif task == 'faq_extended':
            return self.generate_faq_extended(data)
        elif task == 'product_page':
            return self.generate_product_page(data)
        elif task == 'comparison':
            return self.generate_comparison(data['product_a'], data['product_b'])
        else:
            raise ValueError(f"Unknown task: {task}")

    def generate_faq_extended(self, product: ProductData) -> FAQPage:
        """
        Generate extended FAQ page with 15+ categorized questions.
        
        Uses:
        - LLM for question/answer generation
        - FAQTemplate for structured output
        - content_blocks for benefit categorization
        """
        self.log_decision("Generating Extended FAQ Page (15+ questions)", {"product": product.product_name})
        
        if self.mock_mode:
            return self._mock_faq_extended(product)
        
        # Step 1: Use content blocks to analyze product data
        categorized_benefits = categorize_benefits(product.benefits)
        formatted_ingredients = format_ingredients(product.key_ingredients)
        
        self.logger.debug(f"Categorized benefits: {list(categorized_benefits.keys())}")
        self.logger.debug(f"Parsed ingredients: {[i['name'] for i in formatted_ingredients]}")
        
        # Step 2: Generate FAQ content via LLM with enriched context
        prompt = f"""
        Generate a comprehensive FAQ Page for this product with at least 15 questions across 5 categories.
        
        PRODUCT DATA:
        {product.model_dump_json(indent=2)}
        
        ADDITIONAL CONTEXT:
        - Main ingredients: {', '.join([i['name'] for i in formatted_ingredients])}
        - Benefit categories: {list(categorized_benefits.keys())}
        
        REQUIREMENTS:
        1. Generate 15 questions total (3 from each category: Informational, Safety, Usage, Purchase, Comparison)
        2. Base answers ONLY on the provided product data.
        3. Return ONLY valid JSON, no markdown.
        
        OUTPUT FORMAT:
        {{"product_name": "{product.product_name}", "faqs": [{{"question": "...", "answer": "...", "category": "Informational|Safety|Usage|Purchase|Comparison"}}, ...]}}
        """
        
        response_json = self.llm.generate_json(prompt)
        
        # Step 3: Apply FAQ template for structured output
        raw_faqs = response_json.get("faqs", [])
        
        # Use FAQTemplate to add structure (icons, sections, metadata)
        templated_output = FAQTemplate.apply(
            product_name=product.product_name,
            faqs=raw_faqs
        )
        
        self.logger.info(f"Applied FAQTemplate: {templated_output.get('metadata', {})}")
        
        # Step 4: Return Pydantic model (final output is still schema-compliant)
        return FAQPage(
            product_name=product.product_name,
            faqs=[FAQItem(question=f["question"], answer=f["answer"]) for f in raw_faqs]
        )

    def generate_faq(self, product: ProductData, categorized_questions: Dict[str, List] = None) -> FAQPage:
        """Generate FAQ page using pre-generated categorized questions."""
        self.log_decision("Generating FAQ Page", {"product": product.product_name})
        
        if self.mock_mode:
            return self._mock_faq_extended(product)
        
        # If categorized questions provided (from QuestionGeneratorAgent), use them
        if categorized_questions:
            faqs = []
            for category, questions in categorized_questions.items():
                for qa in questions:
                    faqs.append(FAQItem(question=qa.get('question', ''), answer=qa.get('answer', '')))
            
            # Apply template structure
            templated = FAQTemplate.apply(
                product_name=product.product_name,
                faqs=[{"question": f.question, "answer": f.answer} for f in faqs],
                categorized_questions=categorized_questions
            )
            self.logger.info(f"Applied FAQTemplate with {len(faqs)} categorized questions")
            
            return FAQPage(product_name=product.product_name, faqs=faqs)
        
        # Fallback: generate via LLM
        return self.generate_faq_extended(product)

    def generate_product_page(self, product: ProductData) -> ProductPage:
        """
        Generate product marketing page.
        
        Uses:
        - LLM for tagline and description generation
        - content_blocks for price and benefit formatting
        - ProductPageTemplate for structured output
        """
        self.log_decision("Generating Product Page", {"product": product.product_name})
        
        if self.mock_mode:
            return self._mock_product_page(product)
        
        # Step 1: Use content blocks to format data
        formatted_price = format_price(product.price)
        benefit_bullets = generate_benefit_bullets(product.benefits)
        formatted_ingredients = format_ingredients(product.key_ingredients)
        
        self.logger.debug(f"Formatted price: {formatted_price}")
        self.logger.debug(f"Benefit bullets: {len(benefit_bullets)} items")
        
        # Step 2: Generate creative content via LLM
        prompt = f"""
        Generate a marketing Product Page for this product. Return ONLY valid JSON.
        
        PRODUCT: {product.model_dump_json(indent=2)}
        
        FORMATTING HINTS:
        - Price display: {formatted_price['display']}
        - Key benefits: {[b['text'] for b in benefit_bullets]}
        
        FORMAT: {{"title": "{product.product_name}", "price": "{formatted_price['display']}", "tagline": "...", "description": "...", "key_benefits": ["...", "..."], "specifications": [{{"name": "...", "value": "..."}}], "usage_guide": "...", "safety_info": "..."}}
        """
        response_json = self.llm.generate_json(prompt)
        
        # Step 3: Apply ProductPage template for structured layout
        templated = ProductPageTemplate.apply(
            title=response_json.get("title", product.product_name),
            price=response_json.get("price", formatted_price['display']),
            tagline=response_json.get("tagline", ""),
            description=response_json.get("description", ""),
            key_benefits=response_json.get("key_benefits", [b['text'] for b in benefit_bullets]),
            specifications=[{"name": s.get("name", ""), "value": s.get("value", "")} for s in response_json.get("specifications", [])],
            usage_guide=response_json.get("usage_guide", product.how_to_use),
            safety_info=response_json.get("safety_info", product.side_effects)
        )
        
        self.logger.info(f"Applied ProductPageTemplate: {templated.get('metadata', {})}")
        
        # Step 4: Return Pydantic model
        return ProductPage(**response_json)

    def generate_comparison(self, product_a: ProductData, product_b: ProductData) -> ComparisonPage:
        """
        Generate comparison page between two products.
        
        Uses:
        - content_blocks for comparison table building and price comparison
        - LLM for summary and verdict generation
        - ComparisonTemplate for structured output with scores
        """
        self.log_decision("Generating Comparison Page", {
            "product_a": product_a.product_name,
            "product_b": product_b.product_name
        })
        
        if self.mock_mode:
            return self._mock_comparison_page(product_a, product_b)
        
        # Step 1: Use content_blocks to build comparison table
        comparison_table = build_comparison_table(
            product_a.model_dump(by_alias=True),
            product_b.model_dump(by_alias=True)
        )
        
        # Step 2: Use content_blocks for price comparison
        price_comparison = format_price(product_a.price)
        price_b = format_price(product_b.price)
        
        self.logger.debug(f"Built comparison table: {len(comparison_table)} rows")
        self.logger.debug(f"Price A: {price_comparison['display']}, Price B: {price_b['display']}")
        
        # Step 3: Generate summary and verdict via LLM
        prompt = f"""
        Generate a summary and verdict for this product comparison. Return ONLY valid JSON.
        
        PRODUCT A: {product_a.product_name} ({product_a.price})
        PRODUCT B: {product_b.product_name} ({product_b.price})
        
        COMPARISON DATA (already computed):
        {json.dumps(comparison_table, indent=2)}
        
        FORMAT: {{"summary": "2-3 sentence overview...", "verdict": "Our recommendation and why..."}}
        """
        llm_response = self.llm.generate_json(prompt)
        
        # Step 4: Apply ComparisonTemplate for structured output with scores
        templated = ComparisonTemplate.apply(
            product_a_name=product_a.product_name,
            product_b_name=product_b.product_name,
            comparison_table=comparison_table,
            summary=llm_response.get("summary", ""),
            verdict=llm_response.get("verdict", "")
        )
        
        self.logger.info(f"Applied ComparisonTemplate: scores={templated.get('scores', {})}")
        
        # Step 5: Return Pydantic model
        return ComparisonPage(
            product_a_name=product_a.product_name,
            product_b_name=product_b.product_name,
            summary=llm_response.get("summary", ""),
            comparison_table=[ComparisonRow(**row) for row in comparison_table],
            verdict=llm_response.get("verdict", "")
        )

    # =========================================================================
    # MOCK DATA GENERATORS (used when MOCK_MODE=true)
    # =========================================================================
    
    def _mock_faq_extended(self, product: ProductData) -> FAQPage:
        """Mock FAQ generation using content_blocks for formatting."""
        # Use content blocks even in mock mode for consistency
        benefit_bullets = generate_benefit_bullets(product.benefits)
        
        faqs = [
            FAQItem(question=f"What is {product.product_name}?", answer=f"It is a skincare serum with {product.concentration}."),
            FAQItem(question="What are the key ingredients?", answer=f"Main ingredients: {product.key_ingredients}."),
            FAQItem(question="What are the benefits?", answer=f"Benefits include: {product.benefits}."),
            FAQItem(question="Are there any side effects?", answer=f"{product.side_effects or 'No major side effects.'}"),
            FAQItem(question="Is this safe for sensitive skin?", answer="Perform a patch test before first use."),
            FAQItem(question="Can I use if I have allergies?", answer="Check ingredients. Consult dermatologist if needed."),
            FAQItem(question="How do I apply it?", answer=product.how_to_use),
            FAQItem(question="When in my routine?", answer="Apply after cleansing, before moisturizer."),
            FAQItem(question="How often to use?", answer="Use once daily in the morning."),
            FAQItem(question=f"What's the price?", answer=f"Priced at {product.price}."),
            FAQItem(question="Where to buy?", answer="Available online and at select retailers."),
            FAQItem(question="Is it good value?", answer=f"Excellent value at {product.price}."),
            FAQItem(question="How does it compare to others?", answer=f"With {product.concentration}, offers balanced concentration."),
            FAQItem(question="Better than drugstore options?", answer="Premium formulation provides better results."),
            FAQItem(question="Can I use with other serums?", answer="Yes, layer with water-based serums."),
        ]
        return FAQPage(product_name=product.product_name, faqs=faqs)
    
    def _mock_product_page(self, product: ProductData) -> ProductPage:
        """Mock product page using content_blocks for formatting."""
        formatted_price = format_price(product.price)
        benefit_bullets = generate_benefit_bullets(product.benefits)
        
        return ProductPage(
            title=product.product_name,
            price=formatted_price['display'],
            tagline=f"Unlock Your Natural Glow with {product.concentration}",
            description=f"{product.product_name} - premium skincare for {product.skin_type} skin with {product.key_ingredients}.",
            key_benefits=[b['text'] for b in benefit_bullets],
            specifications=[
                ProductSpec(name="Concentration", value=product.concentration or "N/A"),
                ProductSpec(name="Skin Type", value=product.skin_type),
                ProductSpec(name="Key Ingredients", value=product.key_ingredients),
            ],
            usage_guide=product.how_to_use,
            safety_info=product.side_effects
        )
    
    def _mock_comparison_page(self, product_a: ProductData, product_b: ProductData) -> ComparisonPage:
        """Mock comparison page using content_blocks for table building."""
        # Use content_blocks to build comparison table
        comparison_table = build_comparison_table(
            product_a.model_dump(by_alias=True),
            product_b.model_dump(by_alias=True)
        )
        
        return ComparisonPage(
            product_a_name=product_a.product_name,
            product_b_name=product_b.product_name,
            summary=f"Comparing {product_a.product_name} with {product_b.product_name}.",
            comparison_table=[ComparisonRow(**row) for row in comparison_table],
            verdict=f"Both are excellent. {product_a.product_name} offers better value at {product_a.price}."
        )

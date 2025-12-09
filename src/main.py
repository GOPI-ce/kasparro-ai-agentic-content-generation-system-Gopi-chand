"""
Main entry point for Product Marketing Content System.
Generates 3 JSON files: faq.json, product_page.json, comparison_page.json
"""

import argparse
import json
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from agents.coordinator import CoordinatorAgent
from utils import StateManager, get_config, get_logger


def main():
    parser = argparse.ArgumentParser(description="Multi-Agent Product Marketing System")
    parser.add_argument("--input", "-i", default="examples/glowboost.json", help="Path to input JSON")
    parser.add_argument("--output-dir", "-o", default="output", help="Directory to save output files")
    args = parser.parse_args()
    
    logger = get_logger("Main")
    logger.info("=" * 70)
    logger.info("Product Marketing Content System")
    logger.info("=" * 70)
    
    try:
        # Load Config
        config = get_config()
        
        # Load Input
        input_path = Path(args.input)
        if not input_path.exists():
            logger.error(f"Input file not found: {args.input}")
            sys.exit(1)
            
        with open(input_path, 'r', encoding='utf-8') as f:
            input_data = json.load(f)
            
        logger.info(f"✓ Loaded input: {args.input}")
        
        # Initialize & Run workflow
        state_manager = StateManager()
        coordinator = CoordinatorAgent(state_manager)
        
        results = coordinator.run(input_data)
        
        # Save Outputs
        out_dir = Path(args.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. faq.json
        with open(out_dir / "faq.json", 'w', encoding='utf-8') as f:
            f.write(results['faq_page'].model_dump_json(indent=2))
        logger.info(f"✓ Saved: {out_dir}/faq.json")
        
        # 2. product_page.json
        with open(out_dir / "product_page.json", 'w', encoding='utf-8') as f:
            f.write(results['product_page'].model_dump_json(indent=2))
        logger.info(f"✓ Saved: {out_dir}/product_page.json")
            
        # 3. comparison_page.json
        with open(out_dir / "comparison_page.json", 'w', encoding='utf-8') as f:
            f.write(results['comparison_page'].model_dump_json(indent=2))
        logger.info(f"✓ Saved: {out_dir}/comparison_page.json")
        
        # Display Summary
        print("\n" + "="*70)
        print("EXECUTION COMPLETED")
        print("="*70)
        print(f"Validation Status: {results['validation']['status']}")
        if results['validation']['warnings']:
            print("Warnings:")
            for w in results['validation']['warnings']:
                print(f"- {w}")
        print("\nGenerated Files:")
        print(f"1. {out_dir}/faq.json")
        print(f"2. {out_dir}/product_page.json")
        print(f"3. {out_dir}/comparison_page.json")
        print("="*70)
        
    except Exception as e:
        logger.error(f"Execution failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Hockey Canada Rules Integration Script

Extracts official Hockey Canada playing rules from PDF using 2-stage async LLM pipeline
and integrates with existing hockey_rules collection maintaining exact metadata schema.
"""

import asyncio
import json
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import logging

# Setup paths and imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from openai import AsyncOpenAI
from utils.chroma_utils import get_client
import pdfplumber

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Exact metadata schema from existing collection
METADATA_SCHEMA = {
    "roles": ["all", "coach", "official", "parent", "player", "team official"],
    "topics": ["administration", "compliance", "conduct", "discipline", "financial disclosure", 
               "inclusion", "other", "procedure", "reporting", "respect", "safety", 
               "sportsmanship", "transparency"],
    "document_types": ["definition", "exception", "expectation", "procedure", "reporting", "rule"],
    "type": "conduct_policy"  # Fixed value for all records
}

# LLM Prompts
EXTRACTION_PROMPT = """Extract ALL hockey rules from this PDF page content. Focus on official Hockey Canada playing rules.

PDF CONTENT:
{pdf_content}

OUTPUT (JSON array of rules):
[
  {{
    "title": "Rule title (e.g., 'Icing', 'Body Checking', 'Equipment Violations')",
    "content": "Complete rule text including all details and subsections",
    "section": "Section number (e.g., 'Section 6')",
    "rule_number": "Rule number (e.g., 'Rule 81')",
    "page": "{page_num}"
  }}
]

REQUIREMENTS:
- Extract EVERY identifiable rule, even partial ones
- Include complete rule text with subsections
- Preserve official Hockey Canada terminology exactly
- If no clear rules found, return empty array []
- Output must be valid JSON array
"""

ENRICHMENT_PROMPT = """You are enriching a Hockey Canada rule for integration into an existing collection.

RULE TO ENRICH:
{rule_data}

EXISTING COLLECTION SCHEMA (EXACT VALUES ONLY):
- role: {roles}
- topic: {topics}  
- document_type: {document_types}
- source: "hockey_canada_rulebook_2023"
- page: "{page}"
- type: "conduct_policy"

OUTPUT (JSON):
{{
  "title": "Keep original title",
  "content": "Enhanced content with better coaching context while preserving official language",
  "role": "MUST be one of the exact role values above",
  "topic": "MUST be one of the exact topic values above", 
  "document_type": "MUST be one of the exact document_type values above",
  "source": "hockey_canada_rulebook_2023",
  "page": "original page number",
  "type": "conduct_policy"
}}

CLASSIFICATION RULES:
- role: "official" for referee duties, "coach" for bench/team rules, "player" for on-ice conduct, "all" for general rules
- topic: "discipline" for penalties/infractions, "procedure" for game flow, "safety" for equipment/protection, "other" if unclear
- document_type: "rule" for official regulations, "procedure" for processes, "definition" for terminology, "expectation" for conduct standards

CONTENT ENHANCEMENT:
- Add coaching context without changing rule meaning
- Improve clarity for search while keeping official terminology
- Include practical application notes for coaches
"""


class HockeyCanadaAsyncProcessor:
    """Async processor for Hockey Canada rulebook integration."""
    
    def __init__(self, max_concurrent: int = 12, dry_run: bool = False):
        self.client = AsyncOpenAI()
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.dry_run = dry_run
        
        # Statistics tracking
        self.stats = {
            "pages_processed": 0,
            "rules_extracted": 0,
            "rules_enriched": 0,
            "rules_validated": 0,
            "extraction_failures": 0,
            "enrichment_failures": 0
        }
    
    def extract_pdf_pages(self, pdf_path: str, limit_pages: Optional[int] = None) -> List[Tuple[str, int]]:
        """Extract text from PDF pages using pdfplumber."""
        logger.info(f"📄 Extracting text from PDF: {pdf_path}")
        
        pages = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                pages_to_process = min(total_pages, limit_pages) if limit_pages else total_pages
                
                logger.info(f"Processing {pages_to_process} of {total_pages} pages")
                
                for page_num in range(pages_to_process):
                    page = pdf.pages[page_num]
                    text = page.extract_text()
                    
                    if text and len(text.strip()) > 100:  # Skip mostly empty pages
                        pages.append((text, page_num + 1))
                        
                logger.info(f"✅ Extracted text from {len(pages)} pages with content")
                
        except Exception as e:
            logger.error(f"❌ PDF extraction failed: {e}")
            raise
            
        return pages
    
    async def extract_rules_batch(self, pdf_pages: List[Tuple[str, int]]) -> List[Dict]:
        """Stage 1: Async concurrent extraction from all PDF pages."""
        logger.info(f"🔍 Stage 1: Starting concurrent rule extraction from {len(pdf_pages)} pages...")
        
        async def extract_single_page(page_content: str, page_num: int) -> List[Dict]:
            async with self.semaphore:
                try:
                    if self.dry_run:
                        # Mock response for dry run
                        await asyncio.sleep(0.1)  # Simulate API delay
                        return [{
                            "title": f"Mock Rule from Page {page_num}",
                            "content": "Mock rule content for dry run testing",
                            "section": "Section 1",
                            "rule_number": "Rule 1",
                            "page": str(page_num)
                        }]
                    
                    response = await self.client.chat.completions.create(
                        model="gpt-4o-mini",  # Faster/cheaper for extraction
                        messages=[{
                            "role": "user",
                            "content": EXTRACTION_PROMPT.format(
                                pdf_content=page_content[:8000],  # Limit content size
                                page_num=page_num
                            )
                        }],
                        response_format={"type": "json_object"},
                        temperature=0.1
                    )
                    
                    result_text = response.choices[0].message.content
                    result = json.loads(result_text)
                    
                    # Handle both array and object responses
                    if isinstance(result, dict) and "rules" in result:
                        return result["rules"]
                    elif isinstance(result, list):
                        return result
                    else:
                        return []
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"⚠️ JSON decode error for page {page_num}: {e}")
                    self.stats["extraction_failures"] += 1
                    return []
                except Exception as e:
                    logger.warning(f"⚠️ Extraction failed for page {page_num}: {e}")
                    self.stats["extraction_failures"] += 1
                    return []
        
        # Create all tasks at once for true concurrent processing
        logger.info(f"📤 Submitting {len(pdf_pages)} concurrent extraction tasks (max concurrent: {self.semaphore._value})...")
        tasks = [
            extract_single_page(content, page_num) 
            for content, page_num in pdf_pages
        ]
        
        # Execute all pages concurrently with semaphore controlling concurrency
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten results and collect statistics
        all_rules = []
        successful_pages = 0
        for i, result in enumerate(results):
            if isinstance(result, list):
                all_rules.extend(result)
                if result:  # Page had rules
                    successful_pages += 1
            elif isinstance(result, Exception):
                logger.warning(f"⚠️ Page {pdf_pages[i][1]} failed: {result}")
                
        self.stats["pages_processed"] = len(pdf_pages)
        self.stats["rules_extracted"] = len(all_rules)
        logger.info(f"✅ Stage 1 Complete: Extracted {len(all_rules)} rules from {successful_pages}/{len(pdf_pages)} pages")
        return all_rules
    
    async def enrich_rules_batch(self, extracted_rules: List[Dict]) -> List[Dict]:
        """Stage 2: Async concurrent enrichment of all extracted rules."""
        logger.info(f"🔧 Stage 2: Starting concurrent rule enrichment for {len(extracted_rules)} rules...")
        
        async def enrich_single_rule(rule: Dict) -> Optional[Dict]:
            async with self.semaphore:
                try:
                    if self.dry_run:
                        # Mock enrichment for dry run
                        await asyncio.sleep(0.1)  # Simulate API delay
                        return {
                            **rule,
                            "role": "all",
                            "topic": "other", 
                            "document_type": "rule",
                            "source": "hockey_canada_rulebook_2023",
                            "type": "conduct_policy"
                        }
                    
                    response = await self.client.chat.completions.create(
                        model="gpt-4o",  # Higher quality for enrichment
                        messages=[{
                            "role": "user",
                            "content": ENRICHMENT_PROMPT.format(
                                rule_data=json.dumps(rule, indent=2),
                                roles=METADATA_SCHEMA["roles"],
                                topics=METADATA_SCHEMA["topics"],
                                document_types=METADATA_SCHEMA["document_types"],
                                page=rule.get("page", "0")
                            )
                        }],
                        response_format={"type": "json_object"},
                        temperature=0.1
                    )
                    
                    enriched_text = response.choices[0].message.content
                    enriched = json.loads(enriched_text)
                    
                    # Validate metadata against exact schema
                    if not self.validate_metadata(enriched):
                        logger.warning(f"⚠️ Invalid metadata for rule: {enriched.get('title', 'Unknown')}")
                        return None
                        
                    return enriched
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"⚠️ JSON decode error in enrichment: {e}")
                    self.stats["enrichment_failures"] += 1
                    return None
                except Exception as e:
                    logger.warning(f"⚠️ Enrichment failed for rule {rule.get('title', 'Unknown')}: {e}")
                    self.stats["enrichment_failures"] += 1
                    return None
        
        # Create all enrichment tasks at once for true concurrent processing
        logger.info(f"📤 Submitting {len(extracted_rules)} concurrent enrichment tasks (max concurrent: {self.semaphore._value})...")
        tasks = [enrich_single_rule(rule) for rule in extracted_rules]
        
        # Execute all rules concurrently with semaphore controlling concurrency
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful enrichments and collect statistics
        enriched_rules = []
        successful_enrichments = 0
        for i, result in enumerate(results):
            if isinstance(result, dict) and result is not None:
                enriched_rules.append(result)
                successful_enrichments += 1
            elif isinstance(result, Exception):
                rule_title = extracted_rules[i].get('title', 'Unknown') if i < len(extracted_rules) else 'Unknown'
                logger.warning(f"⚠️ Enrichment failed for rule '{rule_title}': {result}")
                
        self.stats["rules_enriched"] = len(enriched_rules)
        logger.info(f"✅ Stage 2 Complete: Enriched {successful_enrichments}/{len(extracted_rules)} rules successfully")
        return enriched_rules
    
    def validate_metadata(self, enriched_rule: Dict) -> bool:
        """Validate metadata matches exact existing schema."""
        required_fields = ["role", "topic", "document_type", "source", "page", "type"]
        
        # Check all required fields exist
        for field in required_fields:
            if field not in enriched_rule or not enriched_rule[field]:
                return False
                
        # Validate values against exact schema
        if enriched_rule["role"] not in METADATA_SCHEMA["roles"]:
            logger.warning(f"Invalid role: {enriched_rule['role']}")
            return False
        if enriched_rule["topic"] not in METADATA_SCHEMA["topics"]:
            logger.warning(f"Invalid topic: {enriched_rule['topic']}")
            return False  
        if enriched_rule["document_type"] not in METADATA_SCHEMA["document_types"]:
            logger.warning(f"Invalid document_type: {enriched_rule['document_type']}")
            return False
        if enriched_rule["type"] != METADATA_SCHEMA["type"]:
            logger.warning(f"Invalid type: {enriched_rule['type']}")
            return False
            
        return True
    
    def final_validation(self, rule: Dict) -> bool:
        """Final validation before integration."""
        required_fields = ["title", "content", "role", "topic", "document_type", "source", "page", "type"]
        
        for field in required_fields:
            if field not in rule or not rule[field] or len(str(rule[field]).strip()) == 0:
                return False
                
        return True
    
    async def process_pdf_async(self, pdf_path: str, limit_pages: Optional[int] = None, 
                               save_intermediate: bool = True, resume_from: Optional[str] = None) -> List[Dict]:
        """Complete 2-stage async processing pipeline with intermediate saves."""
        logger.info("🏒 Starting Hockey Canada Rules Processing...")
        
        # Check if resuming from saved files
        if resume_from:
            if resume_from == "enriched":
                enriched_path = Path("chroma_load/processed/hockey_canada/hockey_canada_rules_enriched.json")
                if enriched_path.exists():
                    logger.info(f"📂 Loading enriched rules from {enriched_path}")
                    with open(enriched_path, 'r') as f:
                        enriched_rules = json.load(f)
                    validated_rules = [rule for rule in enriched_rules if self.final_validation(rule)]
                    self.stats["rules_validated"] = len(validated_rules)
                    logger.info(f"✅ Loaded {len(validated_rules)} validated rules from saved file")
                    return validated_rules
            elif resume_from == "extracted":
                extracted_path = Path("chroma_load/processed/hockey_canada/hockey_canada_rules_extracted.json")
                if extracted_path.exists():
                    logger.info(f"📂 Loading extracted rules from {extracted_path}")
                    with open(extracted_path, 'r') as f:
                        extracted_rules = json.load(f)
                    logger.info(f"📂 Loaded {len(extracted_rules)} extracted rules")
                    # Continue with enrichment
                    enriched_rules = await self.enrich_rules_batch(extracted_rules)
                    if save_intermediate:
                        save_path = Path("chroma_load/processed/hockey_canada/hockey_canada_rules_enriched.json")
                        save_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(save_path, 'w') as f:
                            json.dump(enriched_rules, f, indent=2)
                        logger.info(f"💾 Saved enriched rules to {save_path}")
                    validated_rules = [rule for rule in enriched_rules if self.final_validation(rule)]
                    self.stats["rules_validated"] = len(validated_rules)
                    return validated_rules
        
        # Step 1: Extract PDF pages (synchronous)
        pdf_pages = self.extract_pdf_pages(pdf_path, limit_pages)
        logger.info(f"📄 Loaded {len(pdf_pages)} PDF pages")
        
        if not pdf_pages:
            logger.error("❌ No PDF pages extracted")
            return []
        
        # Step 2: Stage 1 - Async batch extraction
        extracted_rules = await self.extract_rules_batch(pdf_pages)
        
        if not extracted_rules:
            logger.error("❌ No rules extracted from PDF")
            return []
        
        # Save extracted rules
        if save_intermediate:
            save_path = Path("chroma_load/processed/hockey_canada/hockey_canada_rules_extracted.json")
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, 'w') as f:
                json.dump(extracted_rules, f, indent=2)
            logger.info(f"💾 Saved {len(extracted_rules)} extracted rules to {save_path}")
        
        # Step 3: Stage 2 - Async batch enrichment  
        enriched_rules = await self.enrich_rules_batch(extracted_rules)
        
        # Save enriched rules
        if save_intermediate:
            save_path = Path("chroma_load/processed/hockey_canada/hockey_canada_rules_enriched.json")
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, 'w') as f:
                json.dump(enriched_rules, f, indent=2)
            logger.info(f"💾 Saved {len(enriched_rules)} enriched rules to {save_path}")
        
        # Step 4: Final validation and cleanup
        validated_rules = [rule for rule in enriched_rules if self.final_validation(rule)]
        self.stats["rules_validated"] = len(validated_rules)
        
        logger.info(f"✅ Processing Complete: {len(validated_rules)} rules ready for integration")
        
        return validated_rules
    
    def generate_processing_report(self) -> Dict[str, Any]:
        """Generate comprehensive processing report."""
        return {
            "processing_statistics": self.stats,
            "success_rate": {
                "extraction": (self.stats["rules_extracted"] / max(self.stats["pages_processed"], 1)) * 100,
                "enrichment": (self.stats["rules_enriched"] / max(self.stats["rules_extracted"], 1)) * 100,
                "validation": (self.stats["rules_validated"] / max(self.stats["rules_enriched"], 1)) * 100
            },
            "ready_for_integration": self.stats["rules_validated"] > 0
        }


async def integrate_hockey_canada_rules(
    pdf_path: str, 
    collection_name: str = "hockey_rules",
    max_concurrent: int = 12,
    limit_pages: Optional[int] = None,
    dry_run: bool = False,
    clear_existing_hc: bool = False,
    resume_from: Optional[str] = None,
    chunk_size: int = 50
) -> Dict[str, Any]:
    """Main integration function with resume capability."""
    
    logger.info(f"🚀 Starting Hockey Canada Rules Integration")
    logger.info(f"   PDF: {pdf_path}")
    logger.info(f"   Collection: {collection_name}")
    logger.info(f"   Max concurrent: {max_concurrent}")
    logger.info(f"   Limit pages: {limit_pages}")
    logger.info(f"   Dry run: {dry_run}")
    logger.info(f"   Resume from: {resume_from}")
    logger.info(f"   Chunk size: {chunk_size}")
    
    # Initialize processor
    processor = HockeyCanadaAsyncProcessor(
        max_concurrent=max_concurrent,
        dry_run=dry_run
    )
    
    # Process PDF with 2-stage async pipeline
    try:
        enriched_rules = await processor.process_pdf_async(pdf_path, limit_pages, resume_from=resume_from)
        
        if not enriched_rules:
            return {
                "status": "FAILED",
                "error": "No rules processed successfully",
                "report": processor.generate_processing_report()
            }
        
        if dry_run:
            logger.info("🔍 DRY RUN: Skipping actual integration")
            return {
                "status": "DRY_RUN_SUCCESS",
                "processed_rules": len(enriched_rules),
                "sample_rules": enriched_rules[:3],
                "report": processor.generate_processing_report()
            }
        
        # Integration with existing collection
        logger.info("💾 Integrating with ChromaDB collection...")
        client = get_client()
        collection = client.get_collection(collection_name)
        
        # Clear existing Hockey Canada rules if requested
        if clear_existing_hc:
            logger.info("🗑️ Clearing existing Hockey Canada rules...")
            existing_data = collection.get()
            hc_ids = [
                existing_data['ids'][i] for i, meta in enumerate(existing_data['metadatas'])
                if meta.get('source') == 'hockey_canada_rulebook_2023'
            ]
            if hc_ids:
                collection.delete(ids=hc_ids)
                logger.info(f"Removed {len(hc_ids)} existing Hockey Canada rules")
        
        # Prepare for ChromaDB format and add in chunks
        logger.info(f"📦 Adding {len(enriched_rules)} rules to ChromaDB in chunks of {chunk_size}...")
        
        total_added = 0
        for chunk_start in range(0, len(enriched_rules), chunk_size):
            chunk_end = min(chunk_start + chunk_size, len(enriched_rules))
            chunk_rules = enriched_rules[chunk_start:chunk_end]
            
            documents = [rule["content"] for rule in chunk_rules]
            metadatas = [{k: str(v) for k, v in rule.items() if k != "content"} for rule in chunk_rules]
            ids = [f"hc-rule-{i:04d}" for i in range(chunk_start, chunk_end)]
            
            # Add chunk to collection
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            total_added += len(chunk_rules)
            logger.info(f"   ✅ Added chunk {chunk_start//chunk_size + 1}/{(len(enriched_rules)-1)//chunk_size + 1} ({total_added}/{len(enriched_rules)} rules)")
        
        final_count = collection.count()
        logger.info(f"🎉 Successfully integrated {len(enriched_rules)} Hockey Canada rules!")
        logger.info(f"📊 Collection now contains {final_count} total rules")
        
        return {
            "status": "SUCCESS",
            "processed_rules": len(enriched_rules),
            "collection_size": final_count,
            "integration_ids": ids,
            "report": processor.generate_processing_report()
        }
        
    except Exception as e:
        logger.error(f"❌ Integration failed: {e}")
        return {
            "status": "FAILED",
            "error": str(e),
            "report": processor.generate_processing_report()
        }


def main():
    """Command line interface."""
    parser = argparse.ArgumentParser(description="Integrate Hockey Canada rules into ChromaDB collection")
    
    parser.add_argument(
        "pdf_path",
        help="Path to Hockey Canada rulebook PDF"
    )
    parser.add_argument(
        "--collection-name",
        default="hockey_rules",
        help="ChromaDB collection name (default: hockey_rules)"
    )
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=12,
        help="Maximum concurrent API calls (default: 12)"
    )
    parser.add_argument(
        "--limit-pages",
        type=int,
        help="Limit processing to first N pages (for testing)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without actual LLM calls or integration"
    )
    parser.add_argument(
        "--clear-existing-hc",
        action="store_true",
        help="Clear existing Hockey Canada rules before adding new ones"
    )
    parser.add_argument(
        "--resume-from",
        choices=["extracted", "enriched"],
        help="Resume from saved extracted or enriched rules JSON file"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=50,
        help="Chunk size for adding to ChromaDB (default: 50)"
    )
    
    args = parser.parse_args()
    
    # Validate PDF path
    if not Path(args.pdf_path).exists():
        logger.error(f"❌ PDF file not found: {args.pdf_path}")
        return 1
    
    # Run integration
    try:
        result = asyncio.run(integrate_hockey_canada_rules(
            pdf_path=args.pdf_path,
            collection_name=args.collection_name,
            max_concurrent=args.max_concurrent,
            limit_pages=args.limit_pages,
            dry_run=args.dry_run,
            clear_existing_hc=args.clear_existing_hc,
            resume_from=args.resume_from,
            chunk_size=args.chunk_size
        ))
        
        # Print results
        print("\n" + "="*60)
        print("🏒 HOCKEY CANADA RULES INTEGRATION RESULTS")
        print("="*60)
        print(json.dumps(result, indent=2))
        
        return 0 if result["status"] in ["SUCCESS", "DRY_RUN_SUCCESS"] else 1
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
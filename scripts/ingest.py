import argparse
import logging
from src.ingestion.scraper import scrape_all
from src.ingestion.parser import parse_all
from src.ingestion.chunker import chunk_all

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Run the ingestion pipeline.")
    parser.add_argument(
        "--step",
        choices=["scrape", "parse", "chunk", "embed", "all"],
        default="all",
        help="Pipeline step to run (default: all)",
    )
    args = parser.parse_args()
    
    if args.step in ["scrape", "all"]:
        logger.info("Starting scrape step...")
        scrape_all()
        logger.info("Scrape step completed.")
        
    if args.step in ["parse", "all"]:
        logger.info("Starting parse step...")
        parse_all()
        logger.info("Parse step completed.")
        
    if args.step in ["chunk", "all"]:
        logger.info("Starting chunk step...")
        chunk_all()
        logger.info("Chunk step completed.")
        
    if args.step in ["embed", "all"]:
        logger.info("Starting embed step...")
        from src.ingestion.pipeline import embed_and_store_all
        embed_and_store_all()
        logger.info("Embed step completed.")

if __name__ == "__main__":
    main()

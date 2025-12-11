import argparse
import sys

from config import CACHE_DIR, LOG_FILE
from pipeline.concepts import extract_concepts
from pipeline.evaluation import evaluate
from pipeline.quiz import generate_quiz
from pipeline.seeding import seed_questions
from utils.cache import WikipediaCache
from utils.logger import setup_logger

logger = setup_logger(__name__, log_file=LOG_FILE)


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="ConQuerX Educational Quiz Generation Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run full pipeline
  python main.py --step quiz        # Run only quiz generation
  python main.py --verbose          # Run with verbose logging
  python main.py --clear-cache      # Clear cache and run pipeline
        """,
    )

    parser.add_argument(
        "--step",
        choices=["seed", "concepts", "quiz", "eval", "all"],
        default="all",
        help="Which pipeline step to run (default: all)",
    )

    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose (DEBUG level) logging"
    )

    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear Wikipedia cache before running",
    )

    return parser.parse_args()


def main(step: str = "all", verbose: bool = False, clear_cache: bool = False) -> int:
    """
    Run ConQuerX pipeline.

    Args:
        step: Which step to run ("seed", "concepts", "quiz", "eval", or "all")
        verbose: Enable verbose logging
        clear_cache: Clear Wikipedia cache before running

    Returns:
        Exit code (0 = success, 1 = failure)
    """
    # setup logging with verbosity level
    global logger
    logger = setup_logger(__name__, log_file=LOG_FILE, verbose=verbose)

    # clear cache if requested
    if clear_cache:
        cache = WikipediaCache(CACHE_DIR)
        cleared = cache.clear()
        logger.info(f"Cleared {cleared} cached Wikipedia pages")

    logger.info("=" * 60)
    logger.info("ConQuerX Educational Quiz Generation Pipeline")
    logger.info("=" * 60)

    try:
        if step in ["seed", "all"]:
            logger.info("Step 1/4: Seeding questions")
            seed_questions()
            logger.info("Completed step 1/4")

        if step in ["concepts", "all"]:
            logger.info("Step 2/4: Extracting concepts")
            extract_concepts()
            logger.info("Completed step 2/4")

        if step in ["quiz", "all"]:
            logger.info("Step 3/4: Generating quizzes")
            generate_quiz()
            logger.info("Completed step 3/4")

        if step in ["eval", "all"]:
            logger.info("Step 4/4: Evaluating quizzes")
            evaluate()
            logger.info("Completed step 4/4")

        logger.info("=" * 60)
        logger.info("Pipeline completed successfully")
        logger.info("=" * 60)
        return 0

    except KeyboardInterrupt:
        logger.warning("\nPipeline interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    args = parse_args()
    sys.exit(main(step=args.step, verbose=args.verbose, clear_cache=args.clear_cache))

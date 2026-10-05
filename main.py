"""
Main pipeline orchestrator for Smart Regulatory Watch Tool.
Coordinates all agents: Extraction → Translation (Gemini) → Keyword Analysis → Notification
"""

from core.state import PipelineState
from core.logging_utils import logger
from agents.extraction_agent import run_extraction_agent
from agents.translation_agent import run_translation_agent
from agents.keyword_agent import run_keyword_agent
from agents.notification_agent import run_notification_agent

# Configuration
DEFAULT_KEYWORDS = [
    "AML", "CRR", "Basel", "liquidity", "capital", "risk",
    "AnaCredit", "reporting", "regulatory", "compliance"
]


def run_pipeline(
    regulator: str = "BCL",
    predefined_keywords: list = None,
    user_keywords: list = None,
    enable_translation: bool = True,
    enable_notification: bool = True,
    send_only_if_keywords: bool = True,
    email_recipients: list = None,
    force_process_existing: bool = False,
    selected_file: str = None,
    target_language: str = "French"
):
    """
    Run the complete regulatory watch pipeline.
    
    Args:
        regulator: Regulator name (e.g., "BCL", "ECB")
        predefined_keywords: List of predefined keywords to search
        user_keywords: List of user-defined keywords
        enable_translation: Whether to run translation agent (uses Gemini)
        enable_notification: Whether to send email notifications
        send_only_if_keywords: Only send email if keywords are found
        email_recipients: List of email addresses for notifications
    """
    
    logger.info("=" * 60)
    logger.info("STARTING REGULATORY WATCH PIPELINE")
    logger.info("=" * 60)
    
    # Initialize pipeline state
    state = PipelineState(regulator=regulator)
    
    try:
        # Step 1: Extraction Agent
        logger.info("\n>>> STEP 1: EXTRACTION AGENT")
        state = run_extraction_agent(state)
        
        if state.errors:
            logger.error(f"Extraction errors: {state.errors}")
            return state
        
        if not state.file_paths:
            logger.warning("No new documents found.")
            # For testing: process a selected file or existing file if no new ones found
            if force_process_existing or selected_file:
                import os
                if selected_file and os.path.exists(selected_file):
                    logger.info(f"[TEST MODE] Processing selected file: {selected_file}")
                    state.file_paths = [selected_file]
                    state.current_doc = selected_file
                elif force_process_existing:
                    test_file = os.path.join("data", "downloads", "AnaCredit_instructions_EN.pdf")
                    if os.path.exists(test_file):
                        logger.info(f"[TEST MODE] Processing default test file: {test_file}")
                        state.file_paths = [test_file]
                        state.current_doc = test_file
                    else:
                        logger.warning("No test file found. Pipeline stopping.")
                        return state
                else:
                    logger.warning("Selected file not found. Pipeline stopping.")
                    return state
            else:
                logger.warning("Pipeline stopping. Use force_process_existing=True or select a file to test with existing files.")
                return state
        
        # Step 2: Translation Agent (using Gemini)
        if enable_translation:
            logger.info(f"\n>>> STEP 2: TRANSLATION AGENT (Gemini → {target_language})")
            state = run_translation_agent(state, target_language=target_language)
            
            if state.errors:
                logger.error(f"Translation errors: {state.errors}")
        else:
            logger.info("Translation agent skipped.")
        
        # Step 3: Keyword Analysis Agent
        logger.info("\n>>> STEP 3: KEYWORD ANALYSIS AGENT")
        state = run_keyword_agent(
            state,
            predefined_keywords=predefined_keywords or DEFAULT_KEYWORDS,
            user_keywords=user_keywords or [],
            use_semantic=True
        )
        
        if state.errors:
            logger.error(f"Keyword analysis errors: {state.errors}")
        
        # Step 4: Notification Agent
        if enable_notification:
            logger.info("\n>>> STEP 4: NOTIFICATION AGENT")
            if email_recipients:
                state = run_notification_agent(
                    state,
                    recipients=email_recipients,
                    send_only_if_keywords=send_only_if_keywords
                )
            else:
                logger.warning("Email notifications enabled but no recipients configured.")
        
        logger.info("\n" + "=" * 60)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        
        # Summary
        logger.info(f"Regulator: {state.regulator}")
        logger.info(f"Files processed: {len(state.file_paths)}")
        logger.info(f"Keywords found: {len(state.keyword_hits)}")
        if state.keyword_hits:
            for keyword, contexts in list(state.keyword_hits.items())[:5]:
                logger.info(f"  - {keyword}: {len(contexts)} match(es)")
        
    except Exception as e:
        logger.error(f"Pipeline failed with error: {e}", exc_info=True)
        state.errors.append(str(e))
    
    return state


if __name__ == "__main__":
    # Example: Run pipeline manually
    result = run_pipeline(
        regulator="BCL",
        predefined_keywords=DEFAULT_KEYWORDS,
        user_keywords=[],
        enable_translation=True,
        enable_notification=False,  # Set to True and configure EMAIL_USER/EMAIL_PASS in .env
        force_process_existing=True,  # Set to True to test with existing files
        target_language="French"  # Target language for translation
    )
    
    print(f"\nPipeline completed. Errors: {len(result.errors)}")
    if result.errors:
        print("Errors:", result.errors)

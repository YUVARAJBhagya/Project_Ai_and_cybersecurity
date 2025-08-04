import uuid

from celery import group

from a4s_eval.celery_app import celery_app
from a4s_eval.service.api_client import (
    fetch_pending_evaluations,
    mark_completed,
    mark_failed,
)
from a4s_eval.tasks.evaluation_tasks import dataset_evaluation_task


@celery_app.task
def poll_and_run_evaluation() -> None:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("=== POLL_AND_RUN_EVALUATION START ===")
        logger.info("1. Starting poll_and_run_evaluation task")
        
        logger.info("2. About to call fetch_pending_evaluations()")
        eval_ids = fetch_pending_evaluations()
        logger.info(f"3. fetch_pending_evaluations() completed. Found {len(eval_ids)} evaluations: {eval_ids}")

        if not eval_ids:
            logger.info("4. No pending evaluations found, returning")
            return

        logger.info(f"5. Creating groups for {len(eval_ids)} evaluations...")
        groups = [group(dataset_evaluation_task.s(eval_id)) for eval_id in eval_ids]
        logger.info(f"6. Groups created: {len(groups)} groups")

        logger.info("7. Starting to apply groups...")
        # Apply each group in parallel
        for i, (eval_id, g) in enumerate(zip(eval_ids, groups)):
            logger.info(f"8.{i+1} About to launch evaluation task for {eval_id}")
            try:
                (g | finalize_evaluation.si(eval_id)).apply_async()
                logger.info(f"9.{i+1} Task launched successfully for {eval_id}")
            except Exception as e:
                logger.error(f"ERROR launching task for {eval_id}: {str(e)}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
        
        logger.info("10. All tasks processed")
        
    except Exception as e:
        logger.error(f"ERROR in poll_and_run_evaluation: {str(e)}")
        logger.error(f"Exception type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise
    finally:
        logger.info("=== POLL_AND_RUN_EVALUATION END ===")


@celery_app.task
def finalize_evaluation(evaluation_id: uuid.UUID) -> None:
    print(f"Finalizing evaluation {evaluation_id}")
    try:
        response = mark_completed(evaluation_id)
        print(
            f"Evaluation {evaluation_id} marked as completed, status: {response.status_code}"
        )
    except Exception as e:
        print(f"Failed to mark evaluation {evaluation_id} as completed: {e}")
        mark_failed(evaluation_id)


# @celery_app.task
# def test_simple_task() -> str:
#     """Simple test task to debug Celery"""
#     import logging
#     logging.basicConfig(level=logging.INFO)
#     logger = logging.getLogger(__name__)
    
#     logger.info("=== TEST SIMPLE TASK START ===")
#     logger.info("This is a simple test task")
#     logger.info("=== TEST SIMPLE TASK END ===")
    
#     return "Test task completed successfully"

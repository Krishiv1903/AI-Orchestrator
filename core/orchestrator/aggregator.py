from core.utils.logger import setup_logger

logger = setup_logger("aggregator")


def aggregate(state):

    logger.info("Aggregating final response")

    try:
        outputs = state.get("outputs", {})

        logger.info(f"Final outputs: {outputs}")

        return {
            "final_response": outputs
        }

    except Exception as e:
        logger.error(f"Aggregation failed: {str(e)}")

        return {
            "error": "Aggregation failed",
            "details": str(e)
        }

from unittest.mock import AsyncMock, Mock

import pytest

from app.services import scheduler_service


# =========================================================
# TEST: SCHEDULED PRICE CHECK SUCCESS
# =========================================================

@pytest.mark.asyncio
async def test_check_all_product_prices_success(monkeypatch):

    mock_results = [
        {
            "product_id": 1,
            "price_changed": True
        },
        {
            "product_id": 2,
            "price_changed": False
        }
    ]

    mock_service = Mock()

    mock_service.check_all_products = AsyncMock(
        return_value=mock_results
    )

    monkeypatch.setattr(
        scheduler_service,
        "PriceTrackerService",
        Mock(return_value=mock_service)
    )

    await scheduler_service.check_all_product_prices()

    mock_service.check_all_products.assert_awaited_once()


# =========================================================
# TEST: SCHEDULED PRICE CHECK FAILURE
# =========================================================

@pytest.mark.asyncio
async def test_check_all_product_prices_failure(monkeypatch):

    mock_service = Mock()

    mock_service.check_all_products = AsyncMock(
        side_effect=Exception("Database failure")
    )

    monkeypatch.setattr(
        scheduler_service,
        "PriceTrackerService",
        Mock(return_value=mock_service)
    )

    await scheduler_service.check_all_product_prices()

    mock_service.check_all_products.assert_awaited_once()


# =========================================================
# TEST: START SCHEDULER
# =========================================================

def test_start_scheduler(monkeypatch):

    mock_scheduler = Mock()
    mock_scheduler.running = False

    monkeypatch.setattr(
        scheduler_service,
        "scheduler",
        mock_scheduler
    )

    scheduler_service.start_scheduler()

    mock_scheduler.add_job.assert_called_once()

    mock_scheduler.start.assert_called_once()


# =========================================================
# TEST: PREVENT DUPLICATE SCHEDULER START
# =========================================================

def test_start_scheduler_when_already_running(monkeypatch):

    mock_scheduler = Mock()
    mock_scheduler.running = True

    monkeypatch.setattr(
        scheduler_service,
        "scheduler",
        mock_scheduler
    )

    scheduler_service.start_scheduler()

    mock_scheduler.add_job.assert_not_called()

    mock_scheduler.start.assert_not_called()


# =========================================================
# TEST: SHUTDOWN SCHEDULER
# =========================================================

def test_shutdown_scheduler(monkeypatch):

    mock_scheduler = Mock()
    mock_scheduler.running = True

    monkeypatch.setattr(
        scheduler_service,
        "scheduler",
        mock_scheduler
    )

    scheduler_service.shutdown_scheduler()

    mock_scheduler.shutdown.assert_called_once()


# =========================================================
# TEST: SHUTDOWN WHEN SCHEDULER NOT RUNNING
# =========================================================

def test_shutdown_scheduler_when_not_running(monkeypatch):

    mock_scheduler = Mock()
    mock_scheduler.running = False

    monkeypatch.setattr(
        scheduler_service,
        "scheduler",
        mock_scheduler
    )

    scheduler_service.shutdown_scheduler()

    mock_scheduler.shutdown.assert_not_called()
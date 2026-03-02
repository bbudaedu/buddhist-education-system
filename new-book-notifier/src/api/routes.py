from fastapi import APIRouter, BackgroundTasks
from datetime import datetime
from src.models.schemas import HealthResponse, WebhookResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    健康檢查端點，確認服務是否存活
    """
    return HealthResponse(
        status="ok",
        timestamp=datetime.now().isoformat()
    )

@router.post("/trigger", response_model=WebhookResponse)
async def trigger_new_book_check(background_tasks: BackgroundTasks):
    """
    手動發起新書偵測任務
    """
    from src.main import run_process_task
    
    # 這裡將實際處理邏輯以 background task 執行
    background_tasks.add_task(run_process_task)

    return WebhookResponse(
        status="accepted",
        message="New book monitoring task triggered in the background."
    )

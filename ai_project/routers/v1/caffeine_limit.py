from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from models.caffeine_limit import CaffeineLimitModel

router = APIRouter()

# 🔹 요청 데이터 모델
class CaffeineLimitRequest(BaseModel):
    user_id: str
    gender: str
    age: int
    height: float
    weight: float
    is_smoker: int
    take_hormonal_contraceptive: int
    caffeine_sensitivity: int
    total_caffeine_today: int
    caffeine_intake_count: int
    first_intake_hour: int
    last_intake_hour: int
    sleep_duration: float
    sleep_quality: str

# 🔹 응답 템플릿 함수
def make_response(status: str, message: str, data: dict, code=None, detail=None):
    response = {
        "status": status,
        "message": message,
        "data": data
    }
    if code or detail:
        response["data"].update({"code": code, "detail": detail})
    return response


@router.post("/caffeine-limit/predict")
def predict_caffeine_limit(request: CaffeineLimitRequest):
    try:
        model = CaffeineLimitModel()
        limit = model.predict(request.dict())

        if limit is None:
            raise HTTPException(status_code=400, detail="필수 파라미터 'caffeine_limit'이 누락되었습니다.")

        # 섭취 가능 여부 판단
        if request.total_caffeine_today < limit:
            caffeine_status = "N"  # 추가 섭취 가능
            return make_response(
                "success",
                "추가 커피 섭취 가능여부가 생성되었습니다.",
                {
                    "user_id": request.user_id,
                    "caffeine_status": caffeine_status
                }
            )
        else:
            caffeine_status = "Y"  # 초과
            return make_response(
                "success",
                "카페인 권장량을 초과했습니다.",
                {
                    "user_id": request.user_id,
                    "caffeine_status": caffeine_status
                }
            )

    except ValueError as ve:
        raise HTTPException(
            status_code=400,
            detail=make_response("error", "잘못된 요청입니다.", {}, "invalid_request", str(ve))
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=make_response("error", "서버 내부 오류가 발생했습니다.", {}, "resource_exhausted", "컴퓨팅 리소스 부족으로 AI 추론을 완료할 수 없었습니다.")
        """    
            detail={
            "status": "error",
            "message": "서버 내부 오류가 발생했습니다.",
            "data": {
                "code": "resource_exhausted",
                "detail": str(e)  # 원래는 숨겨야 하지만 지금은 디버깅용
            }
        }
        """        
        )

from django.apps import AppConfig

class DreamlensCoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "dreamlens_core"

    def ready(self):
        import os
        import sys
        from pathlib import Path

        # 서버 실행(runserver) 시에만 실행
        if "runserver" not in sys.argv:
            return

        base_dir = Path(__file__).resolve().parent.parent
        data_dir = base_dir / "data"
        json_path = data_dir / "dream_clean.json"

        # 이미 존재하면 변환 생략
        if json_path.exists():
            return

        try:
            from data.convert_dream_json import convert_json
            convert_json()
            print("✅ dream_clean.json 생성 완료")
        except Exception as e:
            print(f"⚠️ dream_clean.json 변환 중 오류 발생: {e}")

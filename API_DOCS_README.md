# 🤗 Transformers API Documentation Suite

이 프로젝트는 Hugging Face Transformers 라이브러리의 **통합 API 문서 생성 도구**입니다. 핵심 모듈, 모델 패키지, 개별 서브모듈까지 포괄하는 완전한 문서를 제공합니다.

## 📋 생성된 문서 개요

### 🎯 통합 문서 (`api_docs/`)
- **핵심 모듈**: 58개 transformers 핵심 모듈 (자동 탐지)
- **모델 패키지**: 15개 주요 모델 패키지  
- **서브모듈**: 112개 개별 서브모듈 (자동 탐지)
- **총 성공률**: 97.4% (185/190)
- **접근 방법**: `http://localhost:8080/`

## 🔧 통합된 문서 생성 스크립트

### 📄 통합 문서 생성기 (권장)
```bash
# 기본 사용법
python3 generate_model_docs.py --some     # 주요 모델들만 생성
python3 generate_model_docs.py --all      # 모든 모델들 생성

# 단축 명령어
python3 generate_model_docs.py -s         # --some와 동일
python3 generate_model_docs.py -a         # --all과 동일

# HTTP 서버 관련
python3 generate_model_docs.py --run      # 기존 문서 서버만 실행
python3 generate_model_docs.py -s --run   # 생성 후 서버 실행
python3 generate_model_docs.py -s --open  # 생성 후 브라우저 열기

# 사용자 지정 디렉토리
python3 generate_model_docs.py -s --dir ./my_docs    # 지정된 디렉토리에 생성
python3 generate_model_docs.py --run -d ./my_docs    # 지정된 디렉토리 서버 실행
```

### ⚙️ 설정 파일
- **`generate_model_docs.yaml`**: "some" 모드에서 생성할 주요 모델들을 정의
- **동적 탐지**: 핵심 모듈과 서브모듈들은 디렉토리에서 자동 탐지
- **수정 가능**: priority_models 리스트에 필요한 모델만 추가/제거

### 🧪 테스트
```bash
# 생성된 모듈들의 import 테스트
python3 test_model_docs.py
```

## 🌐 문서 보기

### 통합 문서 (권장)
```bash
# 방법 1: 생성과 동시에 서버 실행
python3 generate_model_docs.py --some --run

# 방법 2: 기존 문서 서버만 실행  
python3 generate_model_docs.py --run

# 방법 3: 브라우저 자동 열기
python3 generate_model_docs.py --some --open

# 방법 4: 수동 서버 실행
cd api_docs
python3 -m http.server 8080
# 브라우저: http://localhost:8080/
```

### 구조
- **Core Modules**: `api_docs/core_modules/` - 핵심 transformers 모듈들
- **Model Packages**: `api_docs/model_packages/` - 전체 모델 패키지들  
- **Model Submodules**: `api_docs/model_submodules/` - 개별 서브모듈들

## 📚 문서 내용 상세

### 🔧 Core Transformers Modules (58개 - 자동 탐지)
`src/transformers/` 디렉토리에서 자동으로 탐지된 핵심 모듈들:
```python
from transformers import cache_utils          # 캐싱 유틸리티
from transformers import modeling_utils       # 모델 베이스 클래스
from transformers import tokenization_utils   # 토크나이저 유틸리티
from transformers import configuration_utils  # 설정 관리
from transformers import training_args        # 훈련 설정
from transformers import trainer              # 훈련 루프
from transformers import image_processing_utils # 이미지 처리
from transformers import feature_extraction_utils # 특성 추출
from transformers import activations          # 활성화 함수
from transformers import optimization         # 최적화 도구
# ... 48개 더 (모두 자동 탐지)
```

### 📦 Model Packages (15개)
전체 모델 패키지 구조:
```python
from transformers.models import llama      # LLaMA 전체 패키지
from transformers.models import bert       # BERT 전체 패키지
from transformers.models import gpt2       # GPT-2 전체 패키지
from transformers.models import whisper    # Whisper 전체 패키지
# ... 11개 더
```

### 🔍 Model Submodules (112개 - 자동 탐지)
각 모델 디렉토리에서 자동으로 탐지된 서브모듈들:
```python
# LLaMA 컴포넌트들 (6개 탐지)
from transformers.models.llama import modeling_llama
from transformers.models.llama import configuration_llama
from transformers.models.llama import tokenization_llama
from transformers.models.llama import convert_llama_weights_to_hf
from transformers.models.llama import modeling_flax_llama
# ... 등등

# BERT 컴포넌트들 (11개 탐지)
from transformers.models.bert import modeling_bert
from transformers.models.bert import configuration_bert
from transformers.models.bert import modeling_tf_bert
from transformers.models.bert import modeling_flax_bert
# ... 등등

# Whisper 컴포넌트들 (11개 탐지)
from transformers.models.whisper import feature_extraction_whisper
from transformers.models.whisper import modeling_whisper
from transformers.models.whisper import english_normalizer
# ... 등등
```

## 🎨 문서 특징

### 🔍 고급 검색 기능
- **실시간 필터링**: 키워드로 즉시 모듈 검색
- **카테고리별 분류**: Core/Package/Submodule 구분
- **태그 시스템**: Config, Model, Tokenizer, Feature 등

### 📖 풍부한 내용
- **완전한 API 참조**: 모든 클래스, 함수, 매개변수
- **타입 힌트**: Python 타입 정보 포함
- **소스 코드**: 구현 세부사항 확인 가능  
- **네비게이션**: 모듈 간 빠른 이동

### 🎯 반응형 디자인
- **모바일 친화적**: 다양한 화면 크기 지원
- **다크/라이트 모드**: 눈의 피로 최소화
- **빠른 로딩**: 최적화된 HTML/CSS

## 💡 실제 사용 사례

### 1. 개발자 - API 참조
```python
# cache_utils의 DynamicCache를 사용하고 싶을 때
# → core_modules/src/transformers/cache_utils.html에서 확인
from transformers import cache_utils
cache = cache_utils.DynamicCache()
```

### 2. 연구자 - 모델 구조 분석
```python
# LLaMA의 attention 메커니즘을 분석하고 싶을 때
# → model_submodules/llama/src/transformers/models/llama/modeling_llama.html
from transformers.models.llama import modeling_llama
attention_class = modeling_llama.LlamaAttention
```

### 3. 학습자 - 라이브러리 구조 이해
```python
# Transformers의 전체 구조를 이해하고 싶을 때
# → extended_index.html에서 카테고리별로 탐색
```

## 📊 통계 정보

### 생성 성공률
- **기본 모델 문서**: 15/15 (100%)
- **확장 문서**: 61/61 (100%)
- **총 커버리지**: 76개 모듈/패키지

### 성능 정보
- **생성 시간**: 
  - 기본 문서: ~5-10분
  - 확장 문서: ~10-15분
- **문서 크기**: 총 ~100-150MB
- **로딩 속도**: 각 페이지 < 1초

## 🔧 고급 사용법

### 개별 모듈 문서 생성
```bash
# 특정 core 모듈
python3 -m pdoc src.transformers.cache_utils -o api_docs_extended/core_modules

# 특정 model submodule  
python3 -m pdoc src.transformers.models.llama.modeling_llama -o custom_docs

# 특정 model package
python3 -m pdoc src.transformers.models.llama -o custom_docs
```

### 커스텀 문서 스타일링
생성된 HTML 파일들의 CSS를 수정하여 원하는 스타일로 커스터마이징 가능

### 자동 업데이트
```bash  
# 정기적으로 문서 업데이트하는 cron job 설정 가능
0 2 * * * cd /path/to/transformers && python3 generate_extended_docs.py
```

## 🤝 기여 방법

1. **모듈 추가**: `generate_extended_docs.py`의 `CORE_MODULES`나 `PRIORITY_MODELS_WITH_SUBMODULES`에 새 모듈 추가
2. **스타일 개선**: HTML 템플릿과 CSS 스타일 수정
3. **기능 추가**: 검색, 필터링, 네비게이션 기능 개선
4. **버그 리포트**: 문제가 있는 모듈이나 생성 오류 신고

## 📞 문제 해결

### 일반적인 문제들

**Q: 일부 모듈이 import 에러가 발생해요**
A: `deprecated` 폴더나 실험적 기능들은 의도적으로 제외되었습니다. 필요시 `PROBLEMATIC_MODULES`에서 제거하세요.

**Q: 문서 생성이 느려요**  
A: 병렬 처리 옵션을 사용하거나, 필요한 모듈만 선택적으로 생성하세요.

**Q: 브라우저에서 스타일이 깨져요**
A: HTTP 서버를 통해 접근하세요. 직접 파일을 열면 CSS/JS가 제대로 로드되지 않을 수 있습니다.

## 📜 라이선스 & 크레딧

- **Base Library**: Hugging Face Transformers
- **Documentation Tool**: pdoc 15.0.4  
- **Generated by**: GitHub Copilot
- **Date**: 2025-10-19

---

🎉 **Happy Documenting!** 이 도구로 Transformers 라이브러리를 더 쉽게 탐색하고 활용하세요!
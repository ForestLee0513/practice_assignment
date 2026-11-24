"""Day27 설정과 최소 권한 검증. Key·Password를 로그에 노출하지 않습니다."""
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL_ID = 'intfloat/multilingual-e5-small'
RERANK_ID = 'BAAI/bge-reranker-v2-m3'
DIMENSION = 384


def load_env():
    from dotenv import load_dotenv
    load_dotenv(ROOT / '.env', override=False, encoding='utf-8')


def require_setting(key):
    load_env()
    value = os.getenv(key, '').strip()
    if not value or value.startswith('CHANGE_ME'):
        raise RuntimeError(f'{key}를 .env에 설정하세요. 실제 비밀 값은 출력하지 않습니다.')
    return value


def schema_name():
    load_env()
    value = os.getenv('RAG_SCHEMA', 'd27_rag')
    if not re.fullmatch(r'd27_[a-z0-9_]{1,50}', value):
        raise ValueError('Day27 전용 d27_* Schema만 허용합니다.')
    return value


def db_options():
    load_env()
    return dict(host=os.getenv('PGHOST', 'localhost'), port=int(os.getenv('PGPORT', '5432')),
                dbname=os.getenv('PGDATABASE', 'knowledge_lab'),
                user=os.getenv('PGUSER', 'postgres'), password=require_setting('PGPASSWORD'))


def require_cuda():
    """사용 가능한 CUDA 또는 MPS GPU를 반환하며 CPU로 대체하지 않습니다."""
    import torch
    if torch.cuda.is_available():
        return 'cuda:0'
    if torch.backends.mps.is_available():
        return 'mps'
    raise RuntimeError('CUDA 또는 MPS GPU를 사용할 수 없습니다. PyTorch 설치와 GPU 환경을 확인하세요.')

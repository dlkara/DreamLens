import os
import json
import faiss
import numpy as np
from utils.embedder import embed_text

# 벡터와 메타 정보를 저장할 경로
INDEX_PATH = "vectorDB/dream.index"
META_PATH = "vectorDB/dream_meta.json"


def build_index(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    # 리스트가 아니면 nested dict 구조라고 가정하고 flatten 처리
    if not isinstance(raw_data, list):
        data = []
        for top_category in raw_data.values():
            for sub_items in top_category.values():
                data.extend(sub_items)
    else:
        data = raw_data

    if not isinstance(data, list):
        raise ValueError("JSON 파일 파싱 결과가 리스트가 아닙니다.")

    texts = [item['꿈'] for item in data if '꿈' in item]
    metas = [item for item in data if '꿈' in item]

    print(f"🔍 임베딩 대상 텍스트 개수: {len(texts)}")
    print(f"예시 텍스트: {texts[:1]}")

    vectors = embed_text(texts)

    # FAISS 인덱스 구성
    dim = len(vectors[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(vectors).astype('float32'))

    faiss.write_index(index, INDEX_PATH)

    with open(META_PATH, 'w', encoding='utf-8') as f:
        json.dump(metas, f, ensure_ascii=False, indent=2)

    print(f"✅ 인덱스와 메타데이터 저장 완료!")


def load_faiss_index():
    # FAISS 인덱스 및 메타데이터 불러오기
    if not os.path.exists(INDEX_PATH) or not os.path.exists(META_PATH):
        raise FileNotFoundError("FAISS 인덱스 또는 메타데이터 파일이 존재하지 않습니다.")

    index = faiss.read_index(INDEX_PATH)

    with open(META_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    return index, metadata


def search_similar_dreams(query, index, metadata, top_k=5):
    # 쿼리 임베딩
    query_vector = np.array(embed_text([query])).astype("float32")

    # 유사도 검색
    distances, indices = index.search(query_vector, top_k)

    # 결과 구성
    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx < len(metadata):
            result = metadata[idx].copy()
            result["score"] = float(dist)
            results.append(result)

    return results

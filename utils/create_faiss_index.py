from utils.faiss_helper import build_index

if __name__ == "__main__":
    json_path = "data/nate_dream_interpretation_final.json"
    build_index(json_path)
    print("FAISS 인덱스 생성 완료 ✅")

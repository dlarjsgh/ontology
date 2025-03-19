from SPARQLWrapper import SPARQLWrapper, JSON

# Jena Fuseki 서버의 SPARQL 엔드포인트 설정
sparql = SPARQLWrapper("http://localhost:3030/inventory/query")

# SPARQL 쿼리 작성
query = """
PREFIX ex: <http://example.com/inventory#>

SELECT ?warehouse ?capacity
WHERE {
  ?warehouse a ex:Warehouse .
  ?warehouse ex:capacity ?capacity .
  FILTER (?capacity < 5100)
}
"""

# SPARQL 쿼리 실행
sparql.setQuery(query)
sparql.setReturnFormat(JSON)

try:
    results = sparql.query().convert()

    # 🔍 응답 데이터 확인
    print("🔍 Raw SPARQL Query Result:")
    print(results)  # 결과가 비어 있는지 확인하기 위해 추가

    # 응답이 JSON인지 확인
    if "results" in results and "bindings" in results["results"]:
        bindings = results["results"]["bindings"]

        if not bindings:
            print("✅ 창고의 모든 용량이 5000 이상입니다. (재고 부족 없음)")
        else:
            for result in bindings:
                warehouse = result["warehouse"]["value"]
                capacity = result["capacity"]["value"]
                print(f"⚠ 재고 부족: 창고 {warehouse}, 현재 용량 {capacity}")
    else:
        print("❌ SPARQL 결과가 올바른 JSON 형식이 아닙니다.")
except Exception as e:
    print(f"🚨 오류 발생: {e}")

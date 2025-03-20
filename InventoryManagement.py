import os
from langchain_openai import ChatOpenAI  # 최신 방식 적용
from langchain.prompts import PromptTemplate
from SPARQLWrapper import SPARQLWrapper, JSON

# OpenAI API 키를 환경 변수에서 가져오기
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # ✅ 변경

# Jena Fuseki SPARQL 엔드포인트 설정
FUSEKI_ENDPOINT = "http://localhost:3030/inventory/query"

# OpenAI LangChain 설정
llm = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
    model_name="gpt-3.5-turbo",  # gpt-4 또는 gpt-3.5-turbo 사용 가능
    temperature=0.2
)

# SPARQL 쿼리 생성을 위한 프롬프트 템플릿
sparql_prompt = PromptTemplate(
    input_variables=["user_input"],
    template="""
    You are an AI that converts natural language queries into SPARQL queries for a warehouse inventory system.

    The ontology uses the following prefix:
    PREFIX ex: <http://example.com/inventory#>

    Convert the following natural language request into a valid SPARQL query **without any explanations**.
    Output only the SPARQL query, nothing else.

    "{user_input}"

    Example Output:
    SELECT ?warehouse ?capacity
    WHERE {{
        ?warehouse a ex:Warehouse .
        ?warehouse ex:capacity ?capacity .
        FILTER (?capacity < 5100)
    }}
    """
)


def generate_sparql_query(user_input):
    """자연어 입력을 SPARQL 쿼리로 변환"""
    prompt = sparql_prompt.format(user_input=user_input)
    response = llm.invoke(prompt)
    return response.content.strip()  # ✅ 설명 없이 순수한 SPARQL 쿼리만 반환


def execute_sparql_query(query):
    """SPARQL 쿼리를 실행하고 결과를 반환"""
    sparql = SPARQLWrapper(FUSEKI_ENDPOINT)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    try:
        results = sparql.query().convert()

        if "results" in results and "bindings" in results["results"]:
            bindings = results["results"]["bindings"]

            if not bindings:
                return "✅ 해당 조건을 만족하는 창고가 없습니다."

            result_messages = ["⚠ 검색된 창고 목록:"]
            for result in bindings:
                warehouse = result.get("warehouse", {}).get("value", "Unknown")
                capacity = result.get("capacity", {}).get("value", "Unknown")
                result_messages.append(f"- 창고 {warehouse}: 현재 용량 {capacity}")

            return "\n".join(result_messages)
        else:
            return "❌ SPARQL 결과가 올바른 JSON 형식이 아닙니다."

    except Exception as e:
        return f"🚨 오류 발생: {e}"


# ✅ 사용자 입력을 받는 부분 추가
user_input = input("🔍 조회할 창고 정보를 자연어로 입력하세요: ")

# ✅ PREFIX가 포함된 SPARQL 쿼리 생성
sparql_query = f"""
PREFIX ex: <http://example.com/inventory#>

{generate_sparql_query(user_input)}
"""

print("\n🔍 생성된 SPARQL 쿼리:")
print(sparql_query)

# ✅ SPARQL 실행 및 결과 출력
result = execute_sparql_query(sparql_query)

print("\n📢 최종 결과:")
print(result)

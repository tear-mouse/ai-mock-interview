# api_clients/llm_service.py
import os
import openai
from dotenv import load_dotenv

load_dotenv() # 加载 .env 文件中的环境变量

# openai.api_key = os.getenv("OPENAI_API_KEY") # 老版本用法
# 新版本 openai 库会自动从环境变量 OPENAI_API_KEY 读取密钥
# 或者在创建 client 时传入：
# client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# 如果环境变量已设置，则无需显式设置 api_key

client = openai.OpenAI() # 推荐使用新的客户端实例化方式

def generate_interview_questions(job_description, num_questions=5):
    """
    根据职位描述生成面试问题 (使用 OpenAI)。
    """
    try:
        prompt = f"""
        你是一个专业的面试官。请根据以下职位描述，生成 {num_questions} 个相关的面试问题。
        问题应该覆盖技术能力、行为问题和情景问题。

        职位描述：
        ---
        {job_description}
        ---

        请直接列出问题，每行一个问题。
        """
        response = client.chat.completions.create(
            model="gpt-4o", # 建议使用更新的模型，如 gpt-4o 或 gpt-4-turbo
            messages=[
                {"role": "system", "content": "你是一个专业的面试官。"},
                {"role": "user", "content": prompt}
            ]
        )
        questions_text = response.choices[0].message.content.strip()
        # 确保返回的是列表，即使只有一个问题或LLM没有按预期每行一个问题
        questions_list = [q.strip() for q in questions_text.split('\n') if q.strip()]
        return questions_list if questions_list else [questions_text] # 如果分割失败，返回整个文本作为一个问题
    except openai.APIError as e:
        print(f"OpenAI API Error generating questions: {e}")
        return []
    except Exception as e:
        print(f"Error generating questions: {e}")
        return []

def analyze_answer(question, answer, job_description):
    """
    分析应聘者的回答 (使用 OpenAI)。
    """
    try:
        prompt = f"""
        你是一位资深的面试评估官。请根据以下信息分析应聘者的回答：

        职位描述：
        ---
        {job_description}
        ---

        面试问题：
        {question}

        应聘者回答：
        {answer}
        ---

        请从以下几个方面进行评估：
        1.  **相关性**：回答是否直接针对问题，并与职位要求相关？
        2.  **清晰度**：回答是否条理清晰，易于理解？
        3.  **深度和具体性**：回答是否展现了足够的思考深度和具体例子？
        4.  **沟通能力**：从回答中体现出的沟通技巧如何？

        请给出一个综合评价，并指出优点和可以改进的地方。
        """
        response = client.chat.completions.create(
            model="gpt-4o", # 建议使用更新的模型
            messages=[
                {"role": "system", "content": "你是一位资深的面试评估官。"},
                {"role": "user", "content": prompt}
            ]
        )
        analysis = response.choices[0].message.content.strip()
        return analysis
    except openai.APIError as e:
        print(f"OpenAI API Error analyzing answer: {e}")
        return "无法分析回答。"
    except Exception as e:
        print(f"Error analyzing answer: {e}")
        return "无法分析回答。"

if __name__ == '__main__':
    # 测试代码
    sample_job_desc = """
    我们正在寻找一名经验丰富的 Python 后端开发工程师，负责设计、开发和维护我们的核心API服务。
    要求：熟悉 Django/Flask 框架，掌握 RESTful API 设计原则，熟悉数据库 (PostgreSQL/MySQL)，
    了解 Docker 和基本 Linux 操作。有云平台 (AWS/GCP) 经验者优先。
    """
    print("--- 测试生成面试问题 ---")
    questions = generate_interview_questions(sample_job_desc)
    if questions:
        print("生成的面试问题：")
        for q_idx, q_text in enumerate(questions):
            print(f"{q_idx + 1}. {q_text}")
    else:
        print("未能生成面试问题。")

    print("\n--- 测试回答分析 ---")
    if questions:
        sample_question = questions[0] if questions else "请描述一下你过去项目中遇到的一个主要技术挑战以及你是如何解决的？"
        sample_answer = "在我上一个项目中，我们遇到了数据库性能瓶颈问题。我通过分析查询语句，增加了索引，并且引入了缓存机制，最终将响应时间降低了70%。"
        analysis_result = analyze_answer(sample_question, sample_answer, sample_job_desc)
        print(f"\n对问题 '{sample_question}' 的回答 '{sample_answer}' 的分析结果：\n{analysis_result}")
    else:
        print("没有问题可用于测试回答分析。")

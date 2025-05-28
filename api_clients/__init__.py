# utils/analysis_utils.py

def calculate_speaking_rate(text, duration_seconds):
    """
    计算语速 (字/分钟 或 词/分钟).
    这里简单地按字符数计算，对于中文可能更接近“字/分钟”。
    对于英文，可以考虑分词后按词数计算。

    Args:
        text (str): 识别出的文本.
        duration_seconds (float): 回答持续时间 (秒).

    Returns:
        float: 语速 (字/分钟). 返回 0.0 如果时长为0或文本为空.
    """
    if not text or duration_seconds <= 0:
        return 0.0

    num_characters = len(text)
    # 如果是英文，可以考虑用 num_words = len(text.split())
    # 但对于中文，直接用字符数可能更合适，或者使用专门的分词库

    rate_per_minute = (num_characters / duration_seconds) * 60
    return round(rate_per_minute, 2)

def format_analysis_for_display(analysis_text):
    """
    对 LLM 返回的分析文本进行初步格式化，以便更好地在前端展示。
    (这只是一个示例，具体格式化需求可能更复杂)

    Args:
        analysis_text (str): LLM 返回的原始分析文本.

    Returns:
        str: 格式化后的文本 (例如，确保换行被正确处理).
    """
    # 简单的示例：确保换行符被保留，去除首尾多余空格
    # 在HTML中，<pre> 标签通常能很好地处理换行和空格
    # 但如果要在普通 <p> 中显示，可能需要将 \n 替换为 <br>
    return analysis_text.strip()

if __name__ == '__main__':
    # 测试 calculate_speaking_rate
    sample_text_cn = "你好，我今天感觉非常好，这是一个测试。"
    duration1 = 10.0  # 秒
    rate1 = calculate_speaking_rate(sample_text_cn, duration1)
    print(f"文本: '{sample_text_cn}'")
    print(f"时长: {duration1}s, 语速: {rate1} 字/分钟")

    sample_text_en = "Hello, I am feeling very good today, this is a test."
    duration2 = 8.0  # 秒
    # 如果是英文，可以这样计算词数
    num_words_en = len(sample_text_en.split())
    rate_words_en = (num_words_en / duration2) * 60
    print(f"\n文本: '{sample_text_en}'")
    print(f"时长: {duration2}s, 语速 (按词): {round(rate_words_en, 2)} 词/分钟")
    # 按字符计算（对于英文可能意义不大，但作为对比）
    rate_chars_en = calculate_speaking_rate(sample_text_en, duration2)
    print(f"时长: {duration2}s, 语速 (按字符): {rate_chars_en} 字符/分钟")


    # 测试 format_analysis_for_display
    raw_analysis = """
    候选人的回答展现了较好的逻辑性。
    优点：
    1. 清晰表达了观点。
    2. 结合了过往经验。

    不足：
    - 对于细节的阐述可以更充分一些。
    """
    formatted = format_analysis_for_display(raw_analysis)
    print(f"\n原始分析:\n{raw_analysis}")
    print(f"格式化后 (用于 <pre> 标签):\n{formatted}")

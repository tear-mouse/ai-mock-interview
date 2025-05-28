# api_clients/stt_service.py
import os
import openai
from dotenv import load_dotenv

load_dotenv() # 加载 .env 文件中的环境变量

# client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY")) # 如果环境变量已设置，则无需显式设置 api_key
client = openai.OpenAI()

def transcribe_audio(audio_file_path, language_code="zh"):
    """
    使用 OpenAI Whisper 模型将音频文件转换为文本。
    audio_file_path: 指向本地音频文件的路径。
    language_code: ISO-639-1 格式的语言代码，例如 "en", "zh", "es", "fr" 等。
                   如果提供，可以提高准确性。如果省略，Whisper 会自动检测。
    """
    print(f"正在使用 OpenAI Whisper 进行语音识别 (语言: {language_code or '自动检测'})...")
    try:
        with open(audio_file_path, "rb") as audio_file:
            # Whisper API 对文件大小有限制 (例如 25MB)。
            # 支持的音频格式: mp3, mp4, mpeg, mpga, m4a, wav, webm
            transcription_response = client.audio.transcriptions.create(
                model="whisper-1",  # Whisper 模型名称
                file=audio_file,
                language=language_code if language_code else None,
                response_format="text" # "json", "text", "srt", "verbose_json", "vtt"
            )
        # 当 response_format="text" 时, transcription_response 直接是文本字符串
        transcribed_text = transcription_response.strip()
        print(f"Whisper 识别结果: {transcribed_text[:100]}...") # 打印部分结果以供调试
        return transcribed_text
    except openai.APIError as e:
        print(f"OpenAI API Error during transcription: {e}")
        if "File too large" in str(e):
            print("错误：音频文件过大，请确保文件小于25MB。")
        elif "Invalid file format" in str(e):
            print(f"错误：无效的音频文件格式。请使用支持的格式 (mp3, mp4, mpeg, mpga, m4a, wav, webm)。文件路径: {audio_file_path}")
        return None
    except Exception as e:
        print(f"语音识别失败 (OpenAI Whisper): {e}")
        return None

if __name__ == '__main__':
    # 测试代码 - 确保你有一个测试音频文件
    # 将 "path/to/your/sample_audio.mp3" 替换为你的音频文件路径
    # 例如: sample_audio = "test_audio.mp3"
    # 你需要创建一个真实的音频文件来进行测试
    sample_audio_filename = "test_audio_zh.mp3" # 假设你有一个中文测试音频
    
    # 创建一个简单的测试音频文件（如果不存在） - 这需要 ffmpeg
    # 如果你没有 ffmpeg 或不想自动创建，请手动准备一个测试音频文件
    if not os.path.exists(sample_audio_filename):
        print(f"警告: 测试音频文件 {sample_audio_filename} 未找到。请手动准备一个。")
        # 以下代码尝试创建，但可能失败
        try:
            import subprocess
            # 生成一个简短的静音 mp3 文件，然后用 ffmpeg 转换成可用的测试文件
            # 这只是一个非常粗略的示例，实际测试时请使用有意义的音频
            subprocess.run([
                "ffmpeg", "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
                "-t", "2", "-q:a", "9", sample_audio_filename
            ], check=True, capture_output=True)
            print(f"已创建示例音频文件: {sample_audio_filename} (内容为静音，仅供API调用测试)")
        except Exception as e_create:
            print(f"创建示例音频文件失败: {e_create}。请手动提供一个测试音频。")


    if os.path.exists(sample_audio_filename):
        print(f"\n--- 测试 OpenAI Whisper STT ({sample_audio_filename}) ---")
        # 测试中文识别
        transcribed_text_zh = transcribe_audio(sample_audio_filename, language_code="zh")
        if transcribed_text_zh is not None: # 注意 Whisper 返回空字符串也是有效结果
            print(f"中文识别结果: '{transcribed_text_zh}'")
        else:
            print("中文识别未能获取结果。")

        # 假设你还有一个英文测试音频 test_audio_en.mp3
        # sample_audio_en_filename = "test_audio_en.mp3"
        # if os.path.exists(sample_audio_en_filename):
        #     transcribed_text_en = transcribe_audio(sample_audio_en_filename, language_code="en")
        #     if transcribed_text_en is not None:
        #         print(f"英文识别结果: '{transcribed_text_en}'")
        #     else:
        #         print("英文识别未能获取结果。")
        # else:
        #     print(f"英文测试音频 {sample_audio_en_filename} 未找到。")
    else:
        print(f"测试音频文件 {sample_audio_filename} 未找到或无法创建。请提供一个有效的音频文件路径。")
        print("Whisper 支持的格式包括: mp3, mp4, mpeg, mpga, m4a, wav, webm。")

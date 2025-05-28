# api_clients/tts_service.py
import os
import openai
from dotenv import load_dotenv

load_dotenv() # 加载 .env 文件中的环境变量

# client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
client = openai.OpenAI()

def generate_speech_audio(text_to_speak, voice="nova", model="tts-1-hd"):
    """
    使用 OpenAI TTS 模型将文本合成为语音。
    text_to_speak: 要转换为语音的文本。
    voice: OpenAI 提供的预设语音之一 (alloy, echo, fable, onyx, nova, shimmer)。
    model: 使用的 TTS 模型 (例如 "tts-1", "tts-1-hd", "gpt-4o-mini-tts")。
    """
    print(f"正在使用 OpenAI TTS 进行语音合成 (模型: {model}, 语音: {voice})...")
    try:
        # OpenAI TTS API 对输入文本长度有限制 (例如 4096 个字符)。
        response = client.audio.speech.create(
            model=model,
            voice=voice,
            input=text_to_speak,
            response_format="mp3" # "opus", "aac", "flac", "wav", "pcm"
        )
        # response.content 包含音频数据的字节流
        audio_content = response.content
        print(f"OpenAI TTS 合成成功，音频大小: {len(audio_content)} bytes.")
        return audio_content
    except openai.APIError as e:
        print(f"OpenAI API Error during speech synthesis: {e}")
        if "Input too long" in str(e):
            print("错误：输入文本过长，请确保文本少于4096个字符。")
        return None
    except Exception as e:
        print(f"语音合成失败 (OpenAI TTS): {e}")
        return None

if __name__ == '__main__':
    # 测试代码
    sample_text_cn = "你好，这是一个使用 OpenAI 进行语音合成的测试。"
    sample_text_en = "Hello, this is a test using OpenAI for text-to-speech."

    print(f"\n--- 测试 OpenAI TTS (中文, 声音: nova, 模型: tts-1-hd) ---")
    audio_data_cn = generate_speech_audio(sample_text_cn, voice="nova", model="tts-1-hd")
    if audio_data_cn:
        output_filename_cn = "openai_tts_output_zh.mp3"
        with open(output_filename_cn, "wb") as f:
            f.write(audio_data_cn)
        print(f"中文语音已合成并保存到 {output_filename_cn}")
    else:
        print("中文语音未能合成。")

    print(f"\n--- 测试 OpenAI TTS (英文, 声音: alloy, 模型: tts-1) ---")
    audio_data_en = generate_speech_audio(sample_text_en, voice="alloy", model="tts-1")
    if audio_data_en:
        output_filename_en = "openai_tts_output_en.mp3"
        with open(output_filename_en, "wb") as f:
            f.write(audio_data_en)
        print(f"英文语音已合成并保存到 {output_filename_en}")
    else:
        print("英文语音未能合成。")

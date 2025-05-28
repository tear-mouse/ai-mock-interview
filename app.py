# app.py
import os
import io # 用于处理字节流
from flask import Flask, request, jsonify, render_template, send_file
from dotenv import load_dotenv
from werkzeug.utils import secure_filename # 用于安全地处理上传文件名
import openai # 确保导入 openai，因为 overall_analysis 直接使用了

# 导入你的 API 调用模块
from api_clients import llm_service, st_service # 修正: 应该是 stt_service
from api_clients import tts_service # 确保 tts_service 被导入

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/' # 创建一个 uploads 文件夹存放临时音频
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制上传文件大小为 16MB

# 确保上传文件夹存在
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
    print(f"创建上传文件夹: {app.config['UPLOAD_FOLDER']}")

@app.route('/')
def index():
    print("[ROUTE] GET / - 返回主页")
    return render_template('index.html')

@app.route('/start_interview', methods=['POST'])
def start_interview():
    print("[ROUTE] POST /start_interview - 开始面试流程")
    data = request.get_json()
    job_description = data.get('job_description')
    print(f"  接收到的岗位描述 (前100字符): {job_description[:100] if job_description else '无'}")
    if not job_description:
        print("  错误: 缺少岗位描述")
        return jsonify({"error": "缺少岗位描述"}), 400

    questions = llm_service.generate_interview_questions(job_description)
    if not questions:
        print("  错误: llm_service未能生成面试问题")
        return jsonify({"error": "无法生成面试问题"}), 500
    
    print(f"  成功生成 {len(questions)} 个问题")
    return jsonify({"questions": questions})

@app.route('/synthesize_speech', methods=['POST'])
def synthesize_speech_route():
    print("[ROUTE] POST /synthesize_speech - 请求语音合成")
    data = request.get_json()
    text_to_speak = data.get('text')
    voice = data.get('voice', 'nova')
    model = data.get('model', 'tts-1-hd')
    print(f"  接收到的文本: '{text_to_speak}'")
    print(f"  使用的语音: {voice}, 模型: {model}")

    if not text_to_speak:
        print("  错误: 缺少需要合成的文本")
        return jsonify({"error": "缺少需要合成的文本"}), 400

    audio_content = tts_service.generate_speech_audio(text_to_speak, voice=voice, model=model)

    if audio_content:
        print(f"  tts_service 成功返回音频数据，大小: {len(audio_content)} bytes")
        try:
            response = send_file(
                io.BytesIO(audio_content),
                mimetype='audio/mpeg',
            )
            print("  成功准备音频文件响应")
            return response
        except Exception as e:
            print(f"  发送音频文件时发生错误: {e}")
            return jsonify({"error": f"发送音频文件错误: {str(e)}"}), 500
    else:
        print("  错误: tts_service 未能生成音频内容")
        return jsonify({"error": "语音合成失败"}), 500

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    print("[ROUTE] POST /submit_answer - 提交回答")
    if 'audio_data' not in request.files:
        print("  错误: 请求中没有找到 'audio_data'")
        return jsonify({"error": "没有找到音频文件"}), 400

    audio_file = request.files['audio_data']
    question = request.form.get('question')
    job_description = request.form.get('job_description')
    language_preference = request.form.get('language', 'zh') # 默认为中文

    print(f"  接收到的问题: '{question}'")
    print(f"  接收到的岗位描述 (前50字符): {job_description[:50] if job_description else '无'}")
    print(f"  接收到的音频文件名: {audio_file.filename}")
    print(f"  识别语言偏好: {language_preference}")


    if not question or not job_description:
        print("  错误: 缺少问题或职位描述信息")
        return jsonify({"error": "缺少问题或职位描述信息"}), 400

    if audio_file.filename == '':
        print("  错误: 音频文件名为空")
        return jsonify({"error": "没有选择音频文件"}), 400

    if audio_file:
        filename = secure_filename(audio_file.filename if audio_file.filename else "default_audio.webm")
        audio_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        try:
            audio_file.save(audio_file_path)
            print(f"  音频文件已保存到: {audio_file_path}")
        except Exception as e_save:
            print(f"  保存音频文件失败: {e_save}")
            return jsonify({"error": f"保存音频文件失败: {str(e_save)}"}), 500

        transcribed_text = st_service.transcribe_audio(audio_file_path, language_code=language_preference) # 修正: 应该是 stt_service
        
        if os.path.exists(audio_file_path):
            try:
                os.remove(audio_file_path)
                print(f"  临时音频文件已删除: {audio_file_path}")
            except Exception as e_remove:
                print(f"  删除临时音频文件失败: {e_remove}")
        
        if transcribed_text is None:
            print("  错误: stt_service 返回 None，语音识别失败")
            return jsonify({"error": "语音识别失败"}), 500
        
        print(f"  识别出的文本 (前100字符): {transcribed_text[:100]}")

        analysis_result = llm_service.analyze_answer(question, transcribed_text, job_description)
        print("  答案分析完成")

        return jsonify({
            "transcribed_text": transcribed_text,
            "analysis": analysis_result,
        })

    print("  错误: 未知处理音频文件错误")
    return jsonify({"error": "处理音频文件失败"}), 500

@app.route('/overall_analysis', methods=['POST'])
def overall_analysis_route():
    print("[ROUTE] POST /overall_analysis - 请求总体分析")
    data = request.get_json()
    job_description = data.get('job_description')
    interview_data = data.get('interview_data') 
    print(f"  接收到的岗位描述 (前50字符): {job_description[:50] if job_description else '无'}")
    print(f"  接收到的面试数据条数: {len(interview_data) if interview_data else 0}")


    if not job_description or not interview_data:
        print("  错误: 缺少职位描述或面试数据")
        return jsonify({"error": "缺少职位描述或面试数据"}), 400

    summary_prompt = f"""
    你是一位资深的招聘经理。请根据以下职位描述和候选人在模拟面试中各问题的回答及初步分析，
    给出一个关于候选人整体表现的综合评估。

    职位描述：
    ---
    {job_description}
    ---

    面试表现详情：
    """
    for item in interview_data:
        summary_prompt += f"""
    问题: {item['question']}
    回答: {item['answer_text']}
    初步分析: {item['analysis']}
    ---
    """
    summary_prompt += """
    请综合评估候选人的强项、潜在的不足之处，以及与该职位的匹配度。
    请注意评估回答速度是否合适 (如果提供了相关信息)，以及整体沟通表达能力。
    """
    try:
        if not os.getenv("OPENAI_API_KEY") and not openai.api_key:
             openai.api_key = os.getenv("OPENAI_API_KEY")
             if not openai.api_key:
                print("  错误: OpenAI API Key 未配置")
                return jsonify({"error": "OpenAI API Key 未配置"}), 500
        
        api_client_to_use = llm_service.client if hasattr(llm_service, 'client') else openai
        print(f"  使用 API 客户端: {'llm_service.client' if hasattr(llm_service, 'client') else 'global openai'}")

        response = api_client_to_use.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "你是一位资深的招聘经理。"},
                {"role": "user", "content": summary_prompt}
            ]
        )
        overall_summary = response.choices[0].message.content.strip()
        print("  总体分析生成成功")
        return jsonify({"overall_summary": overall_summary})

    except openai.APIError as e:
        print(f"  OpenAI API Error generating overall analysis: {e}")
        return jsonify({"error": f"生成总体分析失败: {str(e)}"}), 500
    except Exception as e:
        print(f"  Error generating overall analysis: {e}")
        return jsonify({"error": f"生成总体分析失败: {str(e)}"}), 500


if __name__ == '__main__':
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    port = int(os.getenv("FLASK_PORT", 5000))
    print(f"Flask app running in {'debug' if debug_mode else 'production'} mode on port {port}")
    app.run(debug=debug_mode, host='0.0.0.0', port=port)

// static/js/main.js
document.addEventListener('DOMContentLoaded', () => {
  console.log("DOM fully loaded and parsed");

  const jobDescriptionTextarea = document.getElementById('job-description');
  const startInterviewBtn = document.getElementById('start-interview-btn');
  const setupSection = document.getElementById('setup-section');
  const interviewSection = document.getElementById('interview-section');
  const analysisSection = document.getElementById('analysis-section');
  const questionNumberDisplay = document.getElementById('question-number');
  const currentQuestionDisplay = document.getElementById('current-question');
  const startRecordingBtn = document.getElementById('start-recording-btn');
  const stopRecordingBtn = document.getElementById('stop-recording-btn');
  const recordingStatusDisplay = document.getElementById('recording-status');
  const audioPlayback = document.getElementById('audio-playback'); // 用于播放用户录音的audio标签
  const answerAnalysisDisplay = document.getElementById('answer-analysis');
  const overallAnalysisDisplay = document.getElementById('overall-analysis');
  const restartInterviewBtn = document.getElementById('restart-interview-btn');

  let mediaRecorder;
  let audioChunks = [];
  let currentQuestions = [];
  let currentQuestionIndex = 0;
  let jobDesc = "";
  let interviewData = [];
  let questionAudio = new Audio(); // 用于播放AI提问的音频

  console.log("Initial variables set up.");

  // --- 语音合成 (Text-to-Speech) ---
  async function speakText(text) {
      console.log(`[TTS] Attempting to speak: "${text}"`);
      if (!text) {
          console.warn("[TTS] No text provided to speak.");
          return;
      }

      if (!questionAudio.paused) {
          console.log("[TTS] Previous audio was playing, pausing and resetting.");
          questionAudio.pause();
          questionAudio.currentTime = 0;
      }
      
      startRecordingBtn.disabled = true;
      recordingStatusDisplay.textContent = 'AI正在提问...';
      console.log("[TTS] Disabled start recording button, status updated.");

      try {
          console.log("[TTS] Sending request to /synthesize_speech");
          const response = await fetch('/synthesize_speech', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
              },
              body: JSON.stringify({ text: text }), // 可以添加 voice 和 model 参数
          });

          console.log(`[TTS] Response status from /synthesize_speech: ${response.status}`);
          if (!response.ok) {
              const errorData = await response.json().catch(() => ({ error: "未知错误，无法解析响应" }));
              console.error(`[TTS] Error from /synthesize_speech: ${response.status}`, errorData);
              throw new Error(errorData.error || `语音合成请求失败 (${response.status})`);
          }

          const audioBlob = await response.blob();
          console.log(`[TTS] Received audio blob, type: ${audioBlob.type}, size: ${audioBlob.size}`);
          const audioUrl = URL.createObjectURL(audioBlob);
          console.log(`[TTS] Created object URL for audio: ${audioUrl}`);
          
          questionAudio.src = audioUrl;
          
          questionAudio.onloadedmetadata = () => {
              console.log("[TTS] Audio metadata loaded. Duration:", questionAudio.duration);
          };
          
          console.log("[TTS] Attempting to play audio...");
          await questionAudio.play();
          console.log("[TTS] Audio playback started.");

          questionAudio.onended = () => {
              console.log("[TTS] Audio playback finished.");
              URL.revokeObjectURL(audioUrl);
              if (currentQuestionIndex < currentQuestions.length) {
                  startRecordingBtn.disabled = false;
                  recordingStatusDisplay.textContent = "AI提问完毕，请开始回答。";
                  console.log("[TTS] Enabled start recording button, status updated.");
              }
          };

          questionAudio.onerror = (e) => {
               console.error('[TTS] Error during audio playback:', e, questionAudio.error);
               URL.revokeObjectURL(audioUrl);
               startRecordingBtn.disabled = false;
               recordingStatusDisplay.textContent = "问题音频播放失败，请阅读文本问题。";
               console.error("[TTS] Playback error, enabled start recording button.");
          };

      } catch (error) {
          console.error('[TTS] Error in speakText function:', error);
          recordingStatusDisplay.textContent = `问题音频加载失败: ${error.message}`;
          startRecordingBtn.disabled = false;
          console.error("[TTS] Catch block error, enabled start recording button.");
      }
  }

  // --- 面试流程控制 ---
  startInterviewBtn.addEventListener('click', async () => {
      console.log("Start Interview button clicked.");
      jobDesc = jobDescriptionTextarea.value.trim();
      if (!jobDesc) {
          alert('请输入岗位描述！');
          console.warn("Job description is empty.");
          return;
      }
      console.log("Job description:", jobDesc.substring(0, 100) + "...");

      setupSection.style.display = 'none';
      analysisSection.style.display = 'none';
      answerAnalysisDisplay.innerHTML = '';
      overallAnalysisDisplay.innerHTML = '';
      interviewData = [];
      currentQuestionIndex = 0;
      console.log("Interview setup reset.");

      try {
          console.log("Fetching interview questions from /start_interview...");
          const response = await fetch('/start_interview', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ job_description: jobDesc }),
          });
          console.log("Response status from /start_interview:", response.status);

          if (!response.ok) {
              const errorData = await response.json().catch(() => ({error: "未知错误"}));
              console.error("Error fetching questions:", errorData);
              throw new Error(errorData.error || '生成面试问题失败');
          }
          const data = await response.json();
          currentQuestions = data.questions;
          console.log("Received questions:", currentQuestions);

          if (currentQuestions && currentQuestions.length > 0) {
              interviewSection.style.display = 'block';
              displayNextQuestion();
          } else {
              alert('未能获取面试问题，请检查后端服务或岗位描述。');
              console.warn("No questions received or empty list.");
              setupSection.style.display = 'block';
          }
      } catch (error) {
          console.error('开始面试时出错:', error);
          alert(`开始面试时出错: ${error.message}`);
          setupSection.style.display = 'block';
      }
  });

  function displayNextQuestion() {
      console.log(`Displaying question index: ${currentQuestionIndex}`);
      if (currentQuestionIndex < currentQuestions.length) {
          const questionText = currentQuestions[currentQuestionIndex];
          questionNumberDisplay.textContent = `问题 ${currentQuestionIndex + 1}/${currentQuestions.length}`;
          currentQuestionDisplay.textContent = questionText;
          console.log(`Current question text: "${questionText}"`);
          
          // 播放问题语音
          speakText(questionText); // speakText 内部会管理 startRecordingBtn 的状态

          // audioPlayback 是用户录音回放的，不是AI提问的，初始隐藏
          if (audioPlayback) audioPlayback.style.display = 'none';

      } else {
          console.log("All questions answered.");
          interviewSection.style.display = 'none';
          generateOverallAnalysis();
      }
  }

  startRecordingBtn.addEventListener('click', async () => {
      console.log("Start Recording button clicked.");
      // 确保AI提问的音频已停止
      if (questionAudio && !questionAudio.paused) {
          console.log("AI question audio was playing, stopping it now.");
          questionAudio.pause();
          questionAudio.currentTime = 0;
      }

      try {
          console.log("Requesting microphone access...");
          const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
          console.log("Microphone access granted.");
          
          const options = { mimeType: 'audio/webm; codecs=opus' }; // 推荐的格式
          if (!MediaRecorder.isTypeSupported(options.mimeType)) {
              console.warn(`${options.mimeType} is not supported! Falling back to default.`);
              mediaRecorder = new MediaRecorder(stream);
          } else {
              mediaRecorder = new MediaRecorder(stream, options);
              console.log(`Using mimeType: ${options.mimeType}`);
          }

          audioChunks = [];
          mediaRecorder.ondataavailable = event => {
              if (event.data.size > 0) {
                  audioChunks.push(event.data);
                  console.log(`Audio chunk received, size: ${event.data.size}`);
              }
          };

          mediaRecorder.onstop = async () => {
              console.log("MediaRecorder stopped. Total chunks:", audioChunks.length);
              if (audioChunks.length === 0) {
                  console.warn("No audio chunks recorded.");
                  recordingStatusDisplay.textContent = '未录制到音频，请重试。';
                  startRecordingBtn.disabled = false; // 允许用户重试
                  stopRecordingBtn.disabled = true;
                  return;
              }

              const audioBlob = new Blob(audioChunks, { type: mediaRecorder.mimeType });
              console.log(`Audio blob created, type: ${audioBlob.type}, size: ${audioBlob.size}`);
              
              if (audioPlayback) { // 用户录音回放
                  const audioUrl = URL.createObjectURL(audioBlob);
                  audioPlayback.src = audioUrl;
                  audioPlayback.style.display = 'block';
                  console.log("User recording playback src set.");
              }
              
              recordingStatusDisplay.textContent = '录音完成，正在上传分析...';

              const formData = new FormData();
              formData.append('audio_data', audioBlob, `interview_answer_${currentQuestionIndex + 1}.webm`);
              formData.append('question', currentQuestions[currentQuestionIndex]);
              formData.append('job_description', jobDesc);
              formData.append('language', 'zh'); // 可以根据用户选择变化
              console.log("FormData prepared for /submit_answer:", {
                  question: currentQuestions[currentQuestionIndex],
                  job_description_snippet: jobDesc.substring(0,50)+"...",
                  language: 'zh'
              });


              try {
                  console.log("Submitting answer to /submit_answer...");
                  const response = await fetch('/submit_answer', {
                      method: 'POST',
                      body: formData,
                  });
                  console.log("Response status from /submit_answer:", response.status);

                  if (!response.ok) {
                      const errorData = await response.json().catch(() => ({error: "未知错误"}));
                      console.error("Error submitting answer:", errorData);
                      throw new Error(errorData.error || '提交回答失败');
                  }
                  const result = await response.json();
                  console.log("Received analysis result:", result);

                  const singleAnalysisHtml = `
                      <div class="analysis-item">
                          <h3>问题 ${currentQuestionIndex + 1}: ${currentQuestions[currentQuestionIndex]}</h3>
                          <p><strong>你的回答 (文本):</strong> ${result.transcribed_text || '未能识别文本'}</p>
                          <p><strong>回答分析:</strong></p>
                          <pre>${result.analysis}</pre>
                          <hr>
                      </div>
                  `;
                  answerAnalysisDisplay.innerHTML += singleAnalysisHtml;
                  interviewData.push({
                      question: currentQuestions[currentQuestionIndex],
                      answer_text: result.transcribed_text,
                      analysis: result.analysis
                  });

                  currentQuestionIndex++;
                  displayNextQuestion();

              } catch (error) {
                  console.error('提交回答时出错:', error);
                  recordingStatusDisplay.textContent = `提交回答失败: ${error.message}`;
                  alert(`提交回答失败: ${error.message}`);
                  startRecordingBtn.disabled = false; // 允许重试当前问题或继续
                  stopRecordingBtn.disabled = true;
              }
          };

          mediaRecorder.start();
          startRecordingBtn.disabled = true;
          stopRecordingBtn.disabled = false;
          recordingStatusDisplay.textContent = '正在录音... 请回答问题。';
          console.log("MediaRecorder started.");

      } catch (err) {
          console.error('无法获取麦克风权限或开始录音:', err);
          recordingStatusDisplay.textContent = '无法启动录音功能，请检查麦克风权限。';
          alert('无法启动录音功能，请检查麦克风权限。');
          startRecordingBtn.disabled = false;
      }
  });

  stopRecordingBtn.addEventListener('click', () => {
      console.log("Stop Recording button clicked.");
      if (mediaRecorder && mediaRecorder.state === 'recording') {
          mediaRecorder.stop();
          console.log("MediaRecorder.stop() called.");
          // onstop回调会自动处理后续逻辑和按钮状态
          // startRecordingBtn.disabled = true; // 状态由 onstop 和 speakText 管理
          stopRecordingBtn.disabled = true;
          recordingStatusDisplay.textContent = '正在停止录音，请稍候...';
      } else {
          console.warn("Stop recording clicked but mediaRecorder not recording or not available.");
      }
  });

  async function generateOverallAnalysis() {
      console.log("Generating overall analysis...");
      recordingStatusDisplay.textContent = "";
      if (interviewData.length === 0) {
          overallAnalysisDisplay.innerHTML = "<p>没有完成任何问题，无法生成总体分析。</p>";
          analysisSection.style.display = 'block';
          console.warn("No interview data for overall analysis.");
          return;
      }
      overallAnalysisDisplay.innerHTML = "<p>正在生成总体表现分析...</p>";
      analysisSection.style.display = 'block';

      try {
          console.log("Sending data for overall analysis to /overall_analysis...");
          const response = await fetch('/overall_analysis', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                  job_description: jobDesc,
                  interview_data: interviewData
              }),
          });
          console.log("Response status from /overall_analysis:", response.status);

          if (!response.ok) {
              const errorData = await response.json().catch(() => ({error: "未知错误"}));
              console.error("Error generating overall analysis:", errorData);
              throw new Error(errorData.error || '生成总体分析失败');
          }
          const result = await response.json();
          console.log("Received overall analysis:", result);
          overallAnalysisDisplay.innerHTML = `<h2>总体表现分析</h2><pre>${result.overall_summary}</pre>`;

      } catch (error) {
          console.error('生成总体分析时出错:', error);
          overallAnalysisDisplay.innerHTML = `<p>生成总体分析失败: ${error.message}</p>`;
      }
  }

  restartInterviewBtn.addEventListener('click', () => {
      console.log("Restart Interview button clicked.");
      // 停止任何正在播放的AI提问语音
      if (questionAudio && !questionAudio.paused) {
          console.log("Stopping AI question audio on restart.");
          questionAudio.pause();
          questionAudio.currentTime = 0;
          URL.revokeObjectURL(questionAudio.src); // 清理旧的 object URL
          questionAudio.src = ""; // 重置src
      }
      // 停止任何正在进行的录音
      if (mediaRecorder && mediaRecorder.state === 'recording') {
          console.log("Stopping user recording on restart.");
          mediaRecorder.stop();
      }
      // 隐藏播放用户录音的audio标签
      if(audioPlayback) audioPlayback.style.display = 'none';


      analysisSection.style.display = 'none';
      interviewSection.style.display = 'none';
      setupSection.style.display = 'block';
      jobDescriptionTextarea.value = "";
      currentQuestions = [];
      currentQuestionIndex = 0;
      interviewData = [];
      audioChunks = [];
      recordingStatusDisplay.textContent = "";
      startRecordingBtn.disabled = false;
      stopRecordingBtn.disabled = true;
      console.log("Interview state reset for restart.");
  });
});

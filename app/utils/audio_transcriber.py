from google.cloud import speech
import requests
import time

def transcribe_streaming_audio(audio_url):
    """Attempts to transcribe audio with retry logic for unavailable resources."""
    attempts = 0
    max_attempts = 3
    initial_wait_time = 10  
    wait_time = 5  # seconds to wait between subsequent attempts

    time.sleep(initial_wait_time)  # Wait initially before making the first request

    while attempts < max_attempts:
        response = requests.get(audio_url, stream=True)
        if response.status_code == 200:
            client = speech.SpeechClient()
            audio_content = response.iter_content(chunk_size=4096)
            stream = (speech.StreamingRecognizeRequest(audio_content=chunk) for chunk in audio_content)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.MP3,
                sample_rate_hertz=16000,
                language_code="en-US",  # Adjusted to English assuming codes are in English
            )
            streaming_config = speech.StreamingRecognitionConfig(config=config)
            responses = client.streaming_recognize(streaming_config, stream)
            for response in responses:
                for result in response.results:
                    # Return the transcript directly without altering case
                    return result.alternatives[0].transcript
            return None  
        else:
            print(f"Attempt {attempts + 1}: Failed to download audio, status code {response.status_code}")
            time.sleep(wait_time)
            attempts += 1

    return f"Failed to download audio after {max_attempts} attempts: status code {response.status_code}"



# def transcribe_streaming_audio(audio_url):
#     """Attempts to transcribe audio with retry logic for unavailable resources, including an initial delay."""
#     attempts = 0
#     max_attempts = 3
#     initial_wait_time = 10  # seconds to wait before the first attempt
#     wait_time = 5  # seconds to wait between subsequent attempts

#     time.sleep(initial_wait_time)  # Wait initially before making the first request

#     while attempts < max_attempts:
#         response = requests.get(audio_url, stream=True)
#         if response.status_code == 200:
#             client = speech.SpeechClient()
#             audio_content = response.iter_content(chunk_size=4096)
#             stream = (speech.StreamingRecognizeRequest(audio_content=chunk) for chunk in audio_content if chunk)
#             config = speech.RecognitionConfig(
#                 encoding=speech.RecognitionConfig.AudioEncoding.MP3,
#                 sample_rate_hertz=16000,
#                 language_code="ka-GE",
#             )
#             streaming_config = speech.StreamingRecognitionConfig(config=config)
#             responses = client.streaming_recognize(streaming_config, stream)
#             for response in responses:
#                 for result in response.results:
#                     return result.alternatives[0].transcript.lower()
#             return None  # No transcription results
#         else:
#             print(f"Attempt {attempts + 1}: Failed to download audio, status code {response.status_code}")
#             time.sleep(wait_time)
#             attempts += 1

#     return f"Failed to download audio after {max_attempts} attempts: status code {response.status_code}"

# @router.post("process_speech")
# async def handle_call_status(
#     request: Request,
#     session: AsyncSession = Depends(get_session),
#     RecordingUrl: str = Form(...),
#     CallSid: str = Form(...),
# ):
#     # Read and store the request body immediately

#     print(f"Received CallSid: {CallSid}")
#     print(f"Recording URL: {RecordingUrl}")
#     if not RecordingUrl:
#         print("Recording URL is missing from the request.")
#     # Proceed with your function logic
#     # Assuming `transcribe_streaming_audio` and `transliterate_georgian` are defined elsewhere
#     recording_url = RecordingUrl.replace(".json", ".mp3")
#     print(f"Recording Url: {recording_url}")
#     transcript = transcribe_streaming_audio(recording_url)
#     print(f"Transcript: {transcript}")
    
#     if not transcript:
#         return {"message": "Failed to transcribe the recording"}

#     transliterated_transcript = transliterate_georgian(transcript)
#     print(f"Translated transcript: {transliterated_transcript}")

#     user = await get_user_by_call_sid(CallSid, session)
#     if user and (transliterated_transcript == user.name.lower().strip() or transcript == user.name.lower().strip()):
#         user.is_verified = True
#         await session.commit()
#         return {"message": "User verified successfully."}

#     return {"message": "Verification failed, name does not match.", "transcript": transliterated_transcript}

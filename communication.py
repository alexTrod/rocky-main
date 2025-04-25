import os
import whisper
import tempfile
from pathlib import Path
import torch
import torchaudio
import numpy as np
import shutil
import ssl
import time
from typing import Optional, Dict, Any, Union
from gtts import gTTS

class Communication:
    # initializes the audio processing system with model and device configuration
    def __init__(self, model_name: str = "tiny", device: Optional[str] = None):
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        
        self.device = device
        self.model = whisper.load_model(model_name).to(device)
        self.temp_dir = tempfile.mkdtemp()
        self.tts_enabled = True
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        
    # converts audio file to text using whisper model
    def transcribe_audio(self, audio_path: Union[str, Path]) -> Dict[str, Any]:
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
        result = self.model.transcribe(str(audio_path))
        return result
    
    # handles audio transcription from raw bytes data
    def transcribe_audio_bytes(self, audio_bytes: bytes) -> Dict[str, Any]:
        temp_file = os.path.join(self.temp_dir, "temp_audio.mp3")
        with open(temp_file, "wb") as f:
            f.write(audio_bytes)
            
        result = self.transcribe_audio(temp_file)
        
        os.remove(temp_file)
        
        return result
    
    # extracts text content from audio file transcription
    def get_text_from_audio(self, audio_path: Union[str, Path]) -> str:
        result = self.transcribe_audio(audio_path)
        return result["text"]
    
    # extracts text content from audio bytes transcription
    def get_text_from_audio_bytes(self, audio_bytes: bytes) -> str:
        result = self.transcribe_audio_bytes(audio_bytes)
        return result["text"]
    
    # converts text to speech and saves to specified output path
    def text_to_speech(self, text: str, output_path: Union[str, Path], 
                      lang: str = "en", speed: float = 1.0) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Try with retries
        for attempt in range(self.max_retries):
            try:
                # Create a custom SSL context that's more permissive
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                
                tts = gTTS(text=text, lang=lang)
                tts.save(str(output_path))
                return  # Success, exit the function
                
            except Exception as e:
                print(f"Error generating speech (attempt {attempt+1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    print(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    # If all retries failed, create a simple fallback audio file
                    self._create_fallback_audio(output_path)
                    print(f"Created fallback audio file at {output_path}")
    
    def _create_fallback_audio(self, output_path: Union[str, Path]) -> None:
        """
        Create a simple fallback audio file when gTTS fails.
        This creates a silent audio file as a placeholder.
        """
        try:
            # Create a simple silent audio file
            sample_rate = 22050
            duration = 1.0  # seconds
            t = torch.linspace(0, duration, int(sample_rate * duration))
            # Create a simple beep sound
            audio = 0.5 * torch.sin(2 * np.pi * 440 * t)  # 440 Hz tone
            audio = audio.unsqueeze(0)  # Add channel dimension
            
            # Save as MP3
            torchaudio.save(
                str(output_path), 
                audio, 
                sample_rate, 
                format="mp3"
            )
        except Exception as e:
            print(f"Error creating fallback audio: {e}")
            # If all else fails, create an empty file
            with open(output_path, 'wb') as f:
                f.write(b'')
    
    # processes audio file and returns transcribed text
    def process_audio_input(self, audio_path: Union[str, Path]) -> str:
        return self.get_text_from_audio(audio_path)
    
    # processes audio bytes and returns transcribed text
    def process_audio_input_bytes(self, audio_bytes: bytes) -> str:
        return self.get_text_from_audio_bytes(audio_bytes)
    
    # generates audio response from text input
    def generate_audio_response(self, text: str, output_path: Union[str, Path]) -> None:
        self.text_to_speech(text, output_path)
    
    # cleans up temporary files on object destruction
    def __del__(self):
        try:
            if hasattr(self, 'temp_dir') and self.temp_dir is not None and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            pass


if __name__ == "__main__":
    comm = Communication(model_name="tiny")
    
    audio_file = "audio_tests/RF_q5.m4a"
    if os.path.exists(audio_file):
        text = comm.process_audio_input(audio_file)
        print(f"Transcribed text: {text}")
        
        if comm.tts_enabled:
            comm.generate_audio_response("I am rocky and i am gonna answer everything you ever wanted to know", "response.mp3")
            print("Audio response generated: response.mp3")
        else:
            print("TTS is not enabled. Cannot generate audio response.")
    else:
        print(f"Audio file not found: {audio_file}")

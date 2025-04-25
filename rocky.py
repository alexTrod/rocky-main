import os
import time
from pathlib import Path
from communication import Communication
from llm_handler import LLMHandler
import argparse

class VoiceAssistant:
    # setting up the core components and directory structure for audio processing
    def __init__(self, whisper_model="tiny"):
        self.comm = Communication(model_name=whisper_model)
        self.llm = LLMHandler()
        self.input_dir = Path("input_audio")
        self.output_dir = Path("output_audio")
        os.makedirs(self.input_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
    
    # handling the language model interaction to generate meaningful responses
    def process_llm_response(self, text: str) -> str:
        # Use the LLM handler to get a response
        return self.llm.ask_question(text)
    
    # managing the end-to-end flow of audio processing and response generation
    def process_audio_file(self, audio_file: Path) -> Path:
        transcribed_text = self.comm.process_audio_input(audio_file)
        print(f"Transcribed: {transcribed_text}")
        
        response_text = self.process_llm_response(transcribed_text)
        print(f"Response: {response_text}")
        
        output_file = self.output_dir / f"response_{int(time.time())}.mp3"
        self.comm.generate_audio_response(response_text, output_file)
        print(f"Audio response saved to: {output_file}")
        
        return output_file
    
    # monitoring the input directory for new audio files and processing them
    def run_interactive(self):
        print("Voice Assistant is running in interactive mode.")
        print(f"Place audio files in the '{self.input_dir}' directory.")
        print("Press Ctrl+C to exit.")
        
        try:
            while True:
                audio_files = list(self.input_dir.glob("*.mp3"))
                
                for audio_file in audio_files:
                    print(f"Processing {audio_file}...")
                    self.process_audio_file(audio_file)
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\nVoice Assistant stopped.")


if __name__ == "__main__":
    assistant = VoiceAssistant()
    
    parser = argparse.ArgumentParser(description='Voice Assistant CLI')
    parser.add_argument('--audio', type=str, help='Path to audio file to process')
    args = parser.parse_args()
    
    audio_file = Path(args.audio) if args.audio else None
    if audio_file and audio_file.exists():
        assistant.process_audio_file(audio_file)
    else:
        print(f"Audio file not found: {audio_file}")
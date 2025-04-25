#!/usr/bin/env python3

from communication import Communication
import argparse
import os

def main():
    parser = argparse.ArgumentParser(description='Test the Text-to-Speech functionality')
    parser.add_argument('--text', type=str, default="Hello, this is a test of the text-to-speech functionality.", 
                        help='Text to convert to speech')
    parser.add_argument('--output', type=str, default="test_output.mp3", 
                        help='Output file path')
    args = parser.parse_args()
    
    print("Initializing Communication class...")
    comm = Communication()
    
    print(f"Converting text to speech: '{args.text}'")
    print(f"Output file: {args.output}")
    
    comm.generate_audio_response(args.text, args.output)
    
    if os.path.exists(args.output):
        file_size = os.path.getsize(args.output)
        print(f"Audio file created successfully. Size: {file_size} bytes")
    else:
        print("Failed to create audio file.")

if __name__ == "__main__":
    main()
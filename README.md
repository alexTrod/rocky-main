# Rocky - Voice Assistant with Fine-Tuned LLM

Rocky is a voice assistant that uses a fine-tuned LLM to answer questions based on your Notion data.

## Components

- **VoiceAssistant**: The main class that handles audio processing and response generation.
- **Communication**: Handles audio transcription and text-to-speech conversion.
- **LLMHandler**: Connects to the fine-tuned LLM to answer questions.

## Setup

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up your environment variables in a `.env` file:
   ```
   NOTION_API_KEY=your_notion_api_key
   CHROMA_DB_PERSISTENT_STORAGE=path_to_chroma_db
   ```

## Usage

### Voice Assistant

To run the voice assistant in interactive mode:

```bash
python rocky.py
```

This will monitor the `input_audio` directory for new audio files and process them.

To process a specific audio file:

```bash
python rocky.py --audio path/to/audio/file.mp3
```

### LLM Handler

To test the LLM Handler directly:

```bash
python test_llm.py
```

This will start an interactive session where you can ask questions.

To ask a specific question:

```bash
python test_llm.py --question "What is the capital of France?"
```

### Text-to-Speech Testing

To test the text-to-speech functionality with SSL error handling:

```bash
python test_tts.py
```

This will convert a default text to speech and save it to `test_output.mp3`.

To specify custom text and output file:

```bash
python test_tts.py --text "Your custom text here" --output "custom_output.mp3"
```

### Cache Management

The system includes a caching mechanism to avoid frequent retraining of the LLM. To manage the cache:

```bash
# View cache statistics
python manage_cache.py --action stats

# View cache contents
python manage_cache.py --action view

# Clear the cache
python manage_cache.py --action clear
```

You can specify which type of cache to operate on:

```bash
# Clear only the response cache
python manage_cache.py --action clear --type response

# Clear only the embedding cache
python manage_cache.py --action clear --type embedding

# Clear all caches
python manage_cache.py --action clear --type all
```

## How It Works

1. The voice assistant listens for audio input.
2. The audio is transcribed to text using Whisper.
3. The text is sent to the LLM Handler.
4. The LLM Handler queries the fine-tuned LLM to get an answer.
5. The answer is converted to speech and played back.

## Caching System

The system includes a robust caching mechanism to avoid frequent retraining:

1. **Response Cache**: Stores previously asked questions and their answers.
2. **Embedding Cache**: Stores information about the Notion pages used for training.
3. **Automatic Cache Invalidation**: The system automatically detects changes in the Notion pages and reinitializes the index when needed.

## Error Handling

The system includes robust error handling for common issues:

- **SSL Errors**: The text-to-speech functionality includes retry logic and a fallback mechanism for SSL errors.
- **Network Issues**: The LLM Handler includes error handling for network-related issues.
- **Notion API Errors**: The system includes retry logic for Notion API requests, with up to 5 retries and a 3-second delay between attempts.
- **File System Errors**: The system handles file system errors gracefully.

### Handling Network Issues in China

If you're using the system in China, you may encounter network-related issues:

1. **Notion API Access**: The system includes retry logic for Notion API requests to handle intermittent connectivity issues.
2. **Text-to-Speech**: The system includes SSL error handling and a fallback mechanism for text-to-speech.
3. **VPN Usage**: For best results, consider using a VPN that routes traffic outside of China.

## Customization

You can customize the LLM Handler by modifying the `llm_handler.py` file. For example, you can change the number of Notion pages to load or the collection name in the vector database.

## License

See the LICENSE file for details.
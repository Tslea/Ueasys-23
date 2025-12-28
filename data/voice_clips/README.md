# Voice Clips Directory

This directory contains voice clips for character voice cloning.

## Usage

Place a 10-second WAV audio clip for each character you want to voice.

### File naming convention:
```
{character_id}.wav
```

### Examples:
- `gandalf.wav` - Voice clip for Gandalf
- `galadriel.wav` - Voice clip for Galadriel
- `smaug.wav` - Voice clip for Smaug
- `aragorn.wav` - Voice clip for Aragorn
- `legolas.wav` - Voice clip for Legolas

## Requirements

- **Format**: WAV (recommended), MP3, OGG, or FLAC
- **Duration**: 10 seconds (ideal for voice cloning)
- **Quality**: Clear speech, minimal background noise
- **Content**: Natural speech in character's voice/style

## Tips for Good Voice Clips

1. **Use clear, expressive speech** - The model will clone the style and tone
2. **Minimal background noise** - Clean audio produces better results
3. **Match the character** - Use voice actors or AI-generated voices that fit
4. **Multiple emotions** - If possible, include varied emotional tones

## Sources for Voice Clips

- Movie/game audio clips (fair use for personal projects)
- AI voice generators (ElevenLabs, Resemble AI, etc.)
- Your own voice recordings
- Voice actors

## Configuration

Enable voice features in `.env`:
```env
TTS_ENABLED=true
STT_ENABLED=true
TTS_PROVIDER=chatterbox
VOICE_CLIP_DIR=data/voice_clips
```

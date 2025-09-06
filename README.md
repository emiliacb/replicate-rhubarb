# Rhubarb Lip Sync - Replicate Model

A Replicate/Cog model that provides automatic lip synchronization analysis using [Rhubarb Lip Sync](https://github.com/DanielSWolf/rhubarb-lip-sync) by Daniel Wolf. This model processes audio files and generates precise mouth cue data for lip synchronization in animations and videos.

## 🎯 Features

- **Automatic Lip Sync Analysis**: Generates mouth cue data from audio input
- **Multiple Audio Format Support**: Handles MP3, WAV, and other common audio formats
- **Chunked Processing**: Automatically splits long audio files into manageable chunks
- **JSON Output**: Returns structured mouth cue data in JSON format
- **Phonetic Recognition**: Uses phonetic recognition for accurate lip sync
- **Cloud-Ready**: Deployed on Replicate for easy API access

## 🚀 Quick Start

### Using the Replicate API

```python
import replicate

# Process audio file
output = replicate.run(
    "emiliacb/replicate-rhubarb:latest",
    input={
        "audio_data": "base64_encoded_audio_data",
        "wake_up": False
    }
)

print(output)
```

### Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/emiliacb/replicate-rhubarb.git
   cd replicate-rhubarb
   ```

2. **Install Cog** (if not already installed):
   ```bash
   curl -o /usr/local/bin/cog -L https://github.com/replicate/cog/releases/latest/download/cog_$(uname -s)_$(uname -m)
   chmod +x /usr/local/bin/cog
   ```

3. **Run the model locally**:
   ```bash
   cog predict -i audio_data="base64_encoded_audio" -i wake_up=false
   ```

## 📋 Requirements

- **Python**: 3.12
- **System Packages**:
  - `ca-certificates`
  - `libc6`
  - `unzip`
  - `libsndfile1`
  - `libportaudio2`
  - `curl`
  - `ffmpeg`

## 🔧 API Reference

### Input Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `audio_data` | string | - | Audio data as base64 encoded string |
| `wake_up` | boolean | `false` | Set to true to wake up the model without processing audio |

### Output Format

The model returns a JSON string with the following structure:

```json
{
  "mouthCues": [
    {
      "start": 0.0,
      "end": 0.1,
      "value": "X"
    },
    {
      "start": 0.1,
      "end": 0.2,
      "value": "A"
    }
  ]
}
```

#### Mouth Cue Values

- **A**: Mouth closed
- **B**: Mouth slightly open
- **C**: Mouth open
- **D**: Mouth wide open
- **E**: Mouth slightly rounded
- **F**: Mouth rounded
- **G**: Mouth wide rounded
- **H**: Mouth slightly puckered
- **X**: Mouth closed (rest position)

## 🎵 Supported Audio Formats

- MP3
- WAV
- FLAC
- AAC
- OGG
- M4A
- WMA

The model automatically converts all input audio to WAV format (44.1kHz, mono, 16-bit) for processing.

## ⚙️ Technical Details

### Audio Processing Pipeline

1. **Base64 Decoding**: Converts base64 audio data to binary
2. **Format Conversion**: Uses FFmpeg to convert to WAV format
3. **Chunking**: Splits audio into 30-second chunks for processing
4. **Rhubarb Analysis**: Processes each chunk with Rhubarb Lip Sync
5. **Result Merging**: Combines results from all chunks
6. **Cleanup**: Removes temporary files

### Rhubarb Configuration

- **Recognizer**: Phonetic
- **Export Format**: JSON
- **Machine Readable**: Enabled
- **Quiet Mode**: Enabled

## 📝 Usage Examples

### Basic Usage

```python
import base64
import replicate

# Read and encode audio file
with open("audio.mp3", "rb") as f:
    audio_data = base64.b64encode(f.read()).decode()

# Process with Replicate
result = replicate.run(
    "emiliacb/replicate-rhubarb:latest",
    input={"audio_data": audio_data}
)

# Parse the result
import json
mouth_cues = json.loads(result)
print(f"Generated {len(mouth_cues['mouthCues'])} mouth cues")
```

### Wake Up Call

```python
# Test if the model is ready
result = replicate.run(
    "emiliacb/replicate-rhubarb:latest",
    input={"wake_up": True}
)

print(result)  # {"status": "OK", "message": "Rhubarb model is ready", "mouthCues": []}
```

### Error Handling

```python
try:
    result = replicate.run(
        "emiliacb/replicate-rhubarb:latest",
        input={"audio_data": audio_data}
    )
    
    data = json.loads(result)
    
    if "error" in data:
        print(f"Error: {data['error']}")
    else:
        print(f"Success: {len(data['mouthCues'])} cues generated")
        
except Exception as e:
    print(f"Request failed: {e}")
```

## 🎬 Use Cases

- **Animation**: Generate lip sync data for animated characters
- **Video Production**: Synchronize lips in video content
- **Game Development**: Create realistic character animations
- **Accessibility**: Improve video accessibility with accurate lip sync
- **Content Creation**: Automate lip sync for video content

## 🔍 Troubleshooting

### Common Issues

1. **Empty Audio Data**: Ensure the audio file is properly encoded as base64
2. **Unsupported Format**: The model will attempt to convert unsupported formats
3. **Large Files**: Very large audio files are automatically chunked
4. **Processing Time**: Longer audio files take more time to process

### Error Messages

- `"No audio data provided"`: The `audio_data` parameter is empty or missing
- `"Audio conversion failed"`: FFmpeg couldn't convert the audio format
- `"Audio chunking failed"`: Error occurred while splitting the audio
- `"Rhubarb processing failed"`: The Rhubarb tool encountered an error

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Daniel Wolf](https://github.com/DanielSWolf) for creating the amazing [Rhubarb Lip Sync](https://github.com/DanielSWolf/rhubarb-lip-sync) tool
- [Replicate](https://replicate.com) for providing the platform to deploy ML models
- [Cog](https://github.com/replicate/cog) for making model containerization easy

## 📞 Support

If you encounter any issues or have questions:

1. Check the [troubleshooting section](#-troubleshooting)
2. Open an [issue](https://github.com/your-username/replicate-rhubarb/issues)
3. Contact the maintainers

---


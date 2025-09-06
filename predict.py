import os
import time
import json
import tempfile
import subprocess
import base64
from typing import List, Dict, Any
from cog import BasePredictor, Input


class Predictor(BasePredictor):
    def setup(self):
        """Initialize the predictor - no model loading needed for Rhubarb"""
        pass

    def predict(self, 
                audio_data: str = Input(description="Audio data as base64 string for lip sync analysis"),
                wake_up: bool = Input(default=False, description="Set to true to wake up the model without processing audio")) -> str:
        """
        Process audio data with Rhubarb lip sync analysis
        """
        try:
            # Check if this is a wake up call
            if wake_up:
                return json.dumps({
                    "status": "OK", 
                    "message": "Rhubarb model is ready",
                    "mouthCues": []
                })
            
            # Validate audio data for normal processing
            if not audio_data or audio_data.strip() == "":
                return json.dumps({
                    "error": "No audio data provided", 
                    "mouthCues": []
                })
            
            # Generate unique timestamp for temp files
            timestamp = str(int(time.time() * 1000))
            
            # Process the audio data
            result = self.process_audio_with_rhubarb(audio_data, timestamp)
            
            # Return JSON string
            return json.dumps(result)
            
        except Exception as e:
            return json.dumps({"error": str(e), "mouthCues": []})

    def process_audio_with_rhubarb(self, audio_data: str, timestamp: str) -> Dict[str, Any]:
        """
        Process audio with Rhubarb, handling chunking and cleanup
        """
        input_path = f"/tmp/input-{timestamp}.wav"
        output_path = f"/tmp/output-{timestamp}.json"
        
        try:
            # Decode base64 and save to file
            audio_bytes = base64.b64decode(audio_data)
            with open(input_path, 'wb') as f:
                f.write(audio_bytes)
            
            # Convert audio to WAV format if needed
            wav_path = self.convert_to_wav(input_path, f"/tmp/wav-{timestamp}.wav")
            
            # Split audio into 30-second chunks
            chunks = self.split_audio_into_chunks(wav_path, timestamp)
            
            all_results = []
            for i, chunk_path in enumerate(chunks):
                chunk_output = f"{output_path}-chunk{i}.json"
                chunk_result = self.run_rhubarb(chunk_path, chunk_output)
                all_results.append(chunk_result)
                
                # Cleanup chunk file
                os.unlink(chunk_path)
            
            # Merge results from all chunks
            mouth_cues = []
            for result in all_results:
                if result and "mouthCues" in result:
                    mouth_cues.extend(result["mouthCues"])
            
            # Sort by start time
            mouth_cues.sort(key=lambda x: x["start"])
            
            # Cleanup temp files
            self.cleanup_temp_files([input_path, wav_path, output_path])
            
            return {"mouthCues": mouth_cues}
            
        except Exception as e:
            # Cleanup on error
            self.cleanup_temp_files([input_path, output_path])
            raise e

    def convert_to_wav(self, input_path: str, output_path: str) -> str:
        """
        Convert audio file to WAV format using ffmpeg
        """
        try:
            # Use ffmpeg to convert to WAV
            cmd = [
                "ffmpeg", "-i", input_path, 
                "-acodec", "pcm_s16le", 
                "-ar", "44100", 
                "-ac", "1", 
                "-y",  # Overwrite output file
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"FFmpeg conversion failed: {result.stderr}")
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Audio conversion failed: {str(e)}")

    def split_audio_into_chunks(self, wav_path: str, timestamp: str) -> List[str]:
        """
        Split audio into 30-second chunks
        """
        chunks = []
        chunk_duration = 30  # seconds
        
        try:
            # Get audio duration using ffprobe
            duration_cmd = [
                "ffprobe", "-v", "quiet", "-show_entries", 
                "format=duration", "-of", "csv=p=0", wav_path
            ]
            result = subprocess.run(duration_cmd, capture_output=True, text=True)
            duration = float(result.stdout.strip())
            
            # Calculate number of chunks
            num_chunks = int(duration / chunk_duration) + 1
            
            for i in range(num_chunks):
                start_time = i * chunk_duration
                chunk_path = f"/tmp/chunk-{timestamp}-{i}.wav"
                
                # Extract chunk using ffmpeg
                chunk_cmd = [
                    "ffmpeg", "-i", wav_path,
                    "-ss", str(start_time),
                    "-t", str(chunk_duration),
                    "-acodec", "pcm_s16le",
                    "-ar", "44100", 
                    "-ac", "1",
                    "-y",
                    chunk_path
                ]
                
                subprocess.run(chunk_cmd, capture_output=True)
                chunks.append(chunk_path)
            
            return chunks
            
        except Exception as e:
            raise Exception(f"Audio chunking failed: {str(e)}")

    def run_rhubarb(self, input_path: str, output_path: str) -> Dict[str, Any]:
        """
        Run Rhubarb on a single audio chunk
        """
        try:
            cmd = [
                "rhubarb", input_path,
                "-o", output_path,
                "--exportFormat", "json",
                "--recognizer", "phonetic",
                "--machineReadable",
                "--quiet"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Rhubarb stderr: {result.stderr}")
                return {"mouthCues": []}
            
            # Read and parse the JSON output
            with open(output_path, 'r') as f:
                data = json.load(f)
            
            return data
            
        except Exception as e:
            print(f"Rhubarb processing failed: {str(e)}")
            return {"mouthCues": []}

    def cleanup_temp_files(self, file_paths: List[str]):
        """
        Clean up temporary files
        """
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}: {str(e)}")

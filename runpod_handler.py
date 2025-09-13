import runpod
import os
import json
import uuid
import tempfile
from acestep.pipeline_ace_step import ACEStepPipeline
import base64
import io

def handler(event):
    """
    RunPod serverless handler for ACE-Step music generation
    """
    try:
        job_input = event['input']
        
        # Validate required inputs
        if 'prompt' not in job_input:
            return {"error": "Missing required field: prompt"}
        
        # Initialize pipeline with optimized settings for serverless
        checkpoint_path = os.environ.get('CHECKPOINT_PATH', '/runpod-volume/checkpoints')
        
        pipeline = ACEStepPipeline(
            checkpoint_dir=checkpoint_path,
            dtype="bfloat16",
            torch_compile=True,
            cpu_offload=True,
            overlapped_decode=True
        )
        
        # Extract parameters with defaults
        audio_duration = job_input.get('duration', 30)
        prompt = job_input['prompt']
        lyrics = job_input.get('lyrics', '')
        infer_step = job_input.get('steps', 27)
        guidance_scale = job_input.get('guidance_scale', 3.5)
        scheduler_type = job_input.get('scheduler_type', 'DDIM')
        cfg_type = job_input.get('cfg_type', 'full')
        omega_scale = job_input.get('omega_scale', 1.0)
        seeds = job_input.get('seeds', [42])
        guidance_interval = job_input.get('guidance_interval', 1.0)
        guidance_interval_decay = job_input.get('guidance_interval_decay', 0.0)
        min_guidance_scale = job_input.get('min_guidance_scale', 1.0)
        use_erg_tag = job_input.get('use_erg_tag', False)
        use_erg_lyric = job_input.get('use_erg_lyric', False)
        use_erg_diffusion = job_input.get('use_erg_diffusion', False)
        oss_steps = job_input.get('oss_steps', [])
        guidance_scale_text = job_input.get('guidance_scale_text', 0.0)
        guidance_scale_lyric = job_input.get('guidance_scale_lyric', 0.0)
        
        # Create temporary output file
        output_filename = f"output_{uuid.uuid4().hex}.wav"
        output_path = f"/tmp/{output_filename}"
        
        # Prepare parameters for pipeline
        params = (
            audio_duration,
            prompt,
            lyrics,
            infer_step,
            guidance_scale,
            scheduler_type,
            cfg_type,
            omega_scale,
            ", ".join(map(str, seeds)),
            guidance_interval,
            guidance_interval_decay,
            min_guidance_scale,
            use_erg_tag,
            use_erg_lyric,
            use_erg_diffusion,
            ", ".join(map(str, oss_steps)),
            guidance_scale_text,
            guidance_scale_lyric,
        )
        
        # Generate music
        pipeline(
            *params,
            save_path=output_path
        )
        
        # Read the generated audio file
        with open(output_path, 'rb') as audio_file:
            audio_data = audio_file.read()
        
        # Encode audio as base64 for return
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        # Clean up temporary file
        os.remove(output_path)
        
        return {
            "status": "success",
            "audio_base64": audio_base64,
            "filename": output_filename,
            "duration": audio_duration,
            "prompt": prompt,
            "lyrics": lyrics
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

# Start the RunPod serverless worker
runpod.serverless.start({"handler": handler})
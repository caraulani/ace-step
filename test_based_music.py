#!/usr/bin/env python3

import os
import time
from acestep.pipeline_ace_step import ACEStepPipeline

def test_ace_step_quality():
    """
    Test ACE-Step music generation quality for BASED music app
    Running on M1 Max with CPU inference for quality evaluation
    """
    
    print("🎵 Testing ACE-Step for BASED Music Generation")
    print("=" * 50)
    
    # Test prompts similar to what users would input in BASED
    test_prompts = [
        {
            "description": "Hip hop trap beat",
            "prompt": "trap, hip hop, dark, heavy bass, male rap vocals, aggressive, modern",
            "lyrics": "[Verse 1]\nRunning through the city with my dreams intact\nNever looking back, staying on track\nMoney on my mind but I keep it real\nThis is how I feel, this is my appeal"
        },
        {
            "description": "Chill Lo-fi vibes", 
            "prompt": "lo-fi, chill, relaxed, soft piano, ambient, dreamy, female vocals, peaceful",
            "lyrics": "[Verse 1]\nSoft light through the window\nQuiet morning glow\nTake it nice and slow\nLetting feelings show"
        },
        {
            "description": "Electronic dance",
            "prompt": "electronic, dance, upbeat, synthesizer, energetic, club music, driving beat",
            "lyrics": "[Drop]\nFeel the beat, feel the sound\nLift your feet off the ground\nAll night long we're gonna dance\nGive love a fighting chance"
        }
    ]
    
    try:
        print("🚀 Initializing ACE-Step Pipeline...")
        print("Note: This will download models on first run (~2-3GB)")
        
        # Initialize pipeline for CPU inference on M1 Max
        pipeline = ACEStepPipeline(
            checkpoint_dir="",     # Use default pretrained
            dtype="float32",       # Use float32 for CPU  
            torch_compile=False,   # Disable for CPU
            cpu_offload=True,      # Enable CPU offloading
            overlapped_decode=False
        )
        
        print("✅ Pipeline initialized successfully!")
        print(f"📱 Running on device: CPU (M1 Max)")
        print(f"🎛️ CPU offloading: Enabled")
        print()
        
        results = []
        
        for i, test in enumerate(test_prompts, 1):
            print(f"🎶 Test {i}/3: {test['description']}")
            print(f"💭 Prompt: {test['prompt']}")
            print(f"📝 Lyrics preview: {test['lyrics'][:50]}...")
            print("⏱️ Generating... (this may take several minutes on CPU)")
            
            start_time = time.time()
            
            # Generate music using ACE-Step API
            output_path = f"/Users/julian/Desktop/ACE-Step/test_output_{i}_{test['description'].replace(' ', '_').lower()}.wav"
            
            pipeline(
                audio_duration=30,                    # 30 second clips
                prompt=test['prompt'],                # Style prompt
                lyrics=test['lyrics'],                # Song lyrics
                infer_step=30,                       # Fewer steps for CPU
                guidance_scale=7.5,                  # Guidance strength
                scheduler_type="dpm-solver",         # Scheduler type
                cfg_type="positive",                 # CFG type
                omega_scale=1.0,                     # Omega scale
                manual_seeds="42",                   # Seed for reproducibility
                guidance_interval=[0, 1],            # Full guidance
                guidance_interval_decay=1.0,         # No decay
                min_guidance_scale=1.0,              # Min guidance
                use_erg_tag=True,                    # Use enhanced guidance
                use_erg_lyric=True,                  # Use lyric guidance  
                use_erg_diffusion=True,              # Use diffusion guidance
                oss_steps="1",                       # OSS steps
                guidance_scale_text=1.0,             # Text guidance scale
                guidance_scale_lyric=1.0,            # Lyric guidance scale
                save_path=output_path                # Output path
            )
            
            generation_time = time.time() - start_time
            
            results.append({
                "test": test['description'],
                "generation_time": generation_time,
                "output_path": output_path,
                "file_size": os.path.getsize(output_path) if os.path.exists(output_path) else 0
            })
            
            print(f"✅ Generated in {generation_time:.1f}s")
            print(f"💾 Saved to: {output_path}")
            print(f"📊 File size: {results[-1]['file_size'] / 1024 / 1024:.1f}MB")
            print()
        
        # Summary
        print("📋 GENERATION SUMMARY")
        print("=" * 50)
        total_time = sum(r['generation_time'] for r in results)
        avg_time = total_time / len(results)
        
        print(f"🎵 Total tracks generated: {len(results)}")
        print(f"⏰ Total generation time: {total_time:.1f}s ({total_time/60:.1f} min)")
        print(f"📊 Average per track: {avg_time:.1f}s")
        print(f"🎯 Speed: {30/avg_time:.1f}x realtime (30s audio in {avg_time:.1f}s)")
        print()
        
        print("🎧 QUALITY EVALUATION:")
        print("Listen to the generated tracks and compare with ElevenLabs:")
        for r in results:
            print(f"• {r['test']}: {r['output_path']}")
        
        print()
        print("💰 COST ANALYSIS:")
        print("• Hardware cost: ~$409/month RTX 4090 server")
        print(f"• Current speed on CPU: {30/avg_time:.1f}x realtime")
        print(f"• Expected GPU speed: ~10-20x faster ({avg_time/15:.1f}-{avg_time/10:.1f}s per track)")
        print("• Break-even: 138 songs/month at $2.99 each")
        print(f"• Capacity: Easily 1000s of songs/month with GPU")
        
    except Exception as e:
        print(f"❌ Error during generation: {e}")
        print("💡 This might be due to model downloading or memory constraints")
        print("   Try running again - first run downloads large models")
        return False
    
    return True

if __name__ == "__main__":
    success = test_ace_step_quality()
    print()
    if success:
        print("🎉 ACE-Step quality test completed!")
        print("🔍 Review the generated audio files to evaluate quality vs ElevenLabs")
    else:
        print("🔧 Test encountered issues - check error messages above")
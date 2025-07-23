import asyncio
import argparse
import os
from pathlib import Path
from openai import AsyncOpenAI
import base64
import glob
import time

# Configuration parameters
MODEL = "gpt-4o"
IMAGE_QUALITY = "medium"
IMAGE_SIZE = "1024x1536"
INPUT_FIDELITY = "high"

client = AsyncOpenAI()

async def create_file(file_path):
    with open(file_path, "rb") as file_content:
        result = await client.files.create(
            file=file_content,
            purpose="vision",
        )
        return result.id

def encode_image(file_path):
    with open(file_path, "rb") as f:
        base64_image = base64.b64encode(f.read()).decode("utf-8")
    return base64_image

def load_prompts(prompts_dir):
    """Load all prompt files from the prompts directory."""
    prompt_files = glob.glob(os.path.join(prompts_dir, "*.txt"))
    prompts = {}
    
    for file_path in prompt_files:
        filename = Path(file_path).stem
        with open(file_path, 'r', encoding='utf-8') as f:
            prompts[filename] = f.read().strip()
    
    return prompts

async def generate_image(prompt_name, prompt_text, input_image_path, output_dir, force=False):
    """Generate a single image using the responses API."""
    start_time = time.time()
    try:
        output_path = os.path.join(output_dir, f"{prompt_name}_output.png")
        
        # Check if output already exists (unless force is True)
        if not force and os.path.exists(output_path):
            elapsed_time = time.time() - start_time
            print(f"⏭️  Skipping {prompt_name}: Output already exists at {output_path}")
            return {"prompt_name": prompt_name, "status": "skipped", "output_path": output_path, "duration": elapsed_time}
        
        print(f"🎨 Starting generation for: {prompt_name}")
        
        # Encode the image and create file
        base64_image = encode_image(input_image_path)
        file_id = await create_file(input_image_path)

        response = await client.responses.create(
            model=MODEL,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt_text},
                        {
                            "type": "input_image",
                            "image_url": f"data:image/png;base64,{base64_image}",
                        },
                        {
                            "type": "input_image",
                            "file_id": file_id,
                        }
                    ],
                }
            ],
            tools=[{"type": "image_generation", "quality": IMAGE_QUALITY, "size": IMAGE_SIZE, "input_fidelity": INPUT_FIDELITY}],
        )

        image_generation_calls = [
            output
            for output in response.output
            if output.type == "image_generation_call"
        ]

        image_data = [output.result for output in image_generation_calls]

        if image_data:
            image_base64 = image_data[0]
            with open(output_path, "wb") as f:
                f.write(base64.b64decode(image_base64))
            elapsed_time = time.time() - start_time
            print(f"✅ Image saved: {output_path} (⏱️ {elapsed_time:.1f}s)")
            return {"prompt_name": prompt_name, "status": "success", "output_path": output_path, "duration": elapsed_time}
        else:
            elapsed_time = time.time() - start_time
            print(f"❌ No image generated for {prompt_name} (⏱️ {elapsed_time:.1f}s)")
            print(f"Response outputs: {[output.type for output in response.output]}")
            return {"prompt_name": prompt_name, "status": "failed", "error": "No image generated", "duration": elapsed_time}
            
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"❌ Error generating image for {prompt_name}: {str(e)} (⏱️ {elapsed_time:.1f}s)")
        return {"prompt_name": prompt_name, "status": "error", "error": str(e), "duration": elapsed_time}

async def main():
    parser = argparse.ArgumentParser(description="Generate hockey diagram images using OpenAI Responses API")
    parser.add_argument(
        "--input-image", 
        default="image_gen/inputs/defense_zone.png",
        help="Path to input image file (default: image_gen/inputs/defense_zone.png)"
    )
    parser.add_argument(
        "--prompts-dir",
        default="image_gen/prompts",
        help="Directory containing prompt files (default: image_gen/prompts)"
    )
    parser.add_argument(
        "--output-dir",
        default="image_gen/outputs",
        help="Directory to save output images (default: image_gen/outputs)"
    )
    parser.add_argument(
        "--prompt",
        help="Generate image for specific prompt file (without .txt extension)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force regeneration even if output files already exist"
    )
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Check if input image exists
    if not os.path.exists(args.input_image):
        print(f"❌ Input image not found: {args.input_image}")
        return
    
    # Load prompts
    prompts = load_prompts(args.prompts_dir)
    
    if not prompts:
        print(f"❌ No prompt files found in {args.prompts_dir}")
        return
    
    # Filter to specific prompt if requested
    if args.prompt:
        if args.prompt in prompts:
            prompts = {args.prompt: prompts[args.prompt]}
        else:
            print(f"❌ Prompt '{args.prompt}' not found. Available prompts: {list(prompts.keys())}")
            return
    
    print(f"🚀 Generating images for {len(prompts)} prompts...")
    print(f"📁 Input image: {args.input_image}")
    print(f"📁 Output directory: {args.output_dir}")
    print(f"📝 Prompts: {list(prompts.keys())}")
    print("-" * 50)
    
    # Track total execution time
    total_start_time = time.time()
    
    # Run all image generations in parallel
    tasks = [
        generate_image(prompt_name, prompt_text, args.input_image, args.output_dir, args.force)
        for prompt_name, prompt_text in prompts.items()
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    total_elapsed_time = time.time() - total_start_time
    
    # Print summary
    print("\n" + "=" * 50)
    print("GENERATION SUMMARY")
    print("=" * 50)
    
    successful = 0
    failed = 0
    skipped = 0
    total_generation_time = 0
    
    for result in results:
        if isinstance(result, Exception):
            print(f"❌ Exception: {result}")
            failed += 1
        elif result["status"] == "success":
            duration = result.get("duration", 0)
            total_generation_time += duration
            print(f"✅ {result['prompt_name']}: {result['output_path']} (⏱️ {duration:.1f}s)")
            successful += 1
        elif result["status"] == "skipped":
            print(f"⏭️  {result['prompt_name']}: {result['output_path']} (already exists)")
            skipped += 1
        else:
            duration = result.get("duration", 0)
            print(f"❌ {result['prompt_name']}: {result.get('error', 'Unknown error')} (⏱️ {duration:.1f}s)")
            failed += 1
    
    # Calculate average generation time (excluding skipped)
    actual_generations = successful + failed
    avg_generation_time = total_generation_time / actual_generations if actual_generations > 0 else 0
    
    print(f"\n📊 Results: {successful} successful, {skipped} skipped, {failed} failed")
    print(f"⏱️  Total time: {total_elapsed_time:.1f}s")
    if actual_generations > 0:
        print(f"⏱️  Average generation time: {avg_generation_time:.1f}s")
        print(f"⏱️  Total generation time: {total_generation_time:.1f}s")

if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Hockey Whiteboard Image Generation with Iterative Feedback

This script implements a two-agent system:
1. Hockey Image Generator: Creates accurate hockey whiteboard diagrams
2. Hockey Image Reviewer: Reviews and scores the generated images for accuracy

The agents work in a feedback loop to iteratively improve the images.
"""

import argparse
import asyncio
import base64
import os
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal, List

from agents import Agent, ImageGenerationTool, ItemHelpers, Runner, TResponseInputItem, WebSearchTool, trace

def load_prompt(prompt_name: str) -> str:
    """Load prompt text from file"""
    prompt_path = Path(__file__).parent.parent / "prompts" / f"{prompt_name}.txt"
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    except Exception as e:
        raise Exception(f"Error loading prompt {prompt_name}: {e}")

@dataclass
class ImageFeedback:
    """Feedback structure for image evaluation"""
    feedback: str
    score: Literal["pass", "needs_improvement", "fail"]
    accuracy_score: int  # 1-10 scale
    specific_issues: List[str]


class HockeyImageGenerator:
    """Agent for generating hockey whiteboard images"""
    
    def __init__(self):
        self.agent = Agent(
            name="Hockey Image Generator",
            instructions=load_prompt("hockey_image_generator"),
            tools=[
                ImageGenerationTool(
                    tool_config={
                        "type": "image_generation", 
                        "quality": "high",
                        "size": "1024x1536",
                        "input_fidelity": "high"
                    }
                ),
                WebSearchTool(user_location={"type": "approximate", "city": "New York"})
            ]
        )


class HockeyImageReviewer:
    """Agent for reviewing hockey image accuracy"""
    
    def __init__(self):
        self.agent = Agent[ImageFeedback](
            name="Hockey Image Reviewer",
            instructions=load_prompt("hockey_image_reviewer"),
            output_type=ImageFeedback,
            tools=[
                WebSearchTool(user_location={"type": "approximate", "city": "New York"})
            ]
        )


class HockeyImageIterator:
    """Main orchestrator for the iterative image generation process"""
    
    def __init__(self, output_dir: str, max_iterations: int = 5, enable_user_feedback: bool = False):
        self.generator = HockeyImageGenerator()
        self.reviewer = HockeyImageReviewer()
        self.output_dir = Path(output_dir)
        self.max_iterations = max_iterations
        self.enable_user_feedback = enable_user_feedback
        self.iteration_history = []
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def save_image(self, image_data: str, iteration: int, session_id: str) -> str:
        """Save generated image to file system"""
        filename = f"hockey_iteration_{iteration:02d}_{session_id}.png"
        filepath = self.output_dir / filename
        
        with open(filepath, "wb") as f:
            f.write(base64.b64decode(image_data))
        
        return str(filepath)
    
    def get_user_feedback(self, iteration: int, image_path: str, ai_feedback: ImageFeedback) -> str:
        """Get feedback from user via CLI"""
        print(f"\n👤 USER FEEDBACK REQUESTED - Iteration {iteration}")
        print(f"🖼️  Image saved at: {image_path}")
        print(f"🤖 AI Reviewer says: {ai_feedback.score} ({ai_feedback.accuracy_score}/10)")
        print(f"💬 AI Feedback: {ai_feedback.feedback}")
        
        if ai_feedback.specific_issues:
            print("🔧 AI Identified Issues:")
            for issue in ai_feedback.specific_issues:
                print(f"   - {issue}")
        
        print("\n" + "="*50)
        print("Please review the generated image and provide your feedback:")
        print("Options:")
        print("  1. Press ENTER to continue with AI feedback only")
        print("  2. Type 'approve' to approve the current image")
        print("  3. Type 'skip' to skip user feedback for remaining iterations")
        print("  4. Type specific feedback to improve the image")
        print("="*50)
        
        user_input = input("Your feedback: ").strip()
        
        if user_input.lower() == "approve":
            return "USER_APPROVE"
        elif user_input.lower() == "skip":
            return "USER_SKIP"
        elif user_input == "":
            return ""
        else:
            return user_input
    
    async def generate_and_review(self, user_request: str) -> dict:
        """Main loop for generating and reviewing hockey images"""
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print(f"🏒 Starting hockey image generation session: {session_id}")
        print(f"📝 User request: {user_request}")
        print(f"📂 Output directory: {self.output_dir}")
        print(f"🔄 Max iterations: {self.max_iterations}")
        print("-" * 60)
        
        input_items: List[TResponseInputItem] = [{"content": user_request, "role": "user"}]
        
        # Track previous response IDs for conversation continuity
        generator_previous_response_id = None
        reviewer_previous_response_id = None
        
        with trace(f"Hockey Image Generation - {session_id}"):
            for iteration in range(1, self.max_iterations + 1):
                print(f"\n🎨 Iteration {iteration}/{self.max_iterations}")
                
                # Generate image
                print("  Generating hockey diagram...")
                generation_result = await Runner.run(
                    self.generator.agent,
                    input_items,
                    previous_response_id=generator_previous_response_id
                )
                
                # Update generator's previous response ID for next iteration
                generator_previous_response_id = generation_result.last_response_id
                
                # Extract image data and save the image generation call item
                image_data = None
                image_generation_item = None
                for item in generation_result.new_items:
                    if (item.type == "tool_call_item" 
                        and item.raw_item.type == "image_generation_call" 
                        and item.raw_item.result):
                        image_data = item.raw_item.result
                        image_generation_item = item.raw_item  # Save the actual generation call
                        break
                
                if not image_data:
                    print("  ❌ No image generated")
                    continue
                
                # Save image
                image_path = self.save_image(image_data, iteration, session_id)
                print(f"  💾 Image saved: {image_path}")
                
                # Prepare input for reviewer - include the image as base64
                review_input = [
                    {
                        "content": [
                            {"type": "input_text", "text": f"Please review this hockey diagram image that was generated for the user request: '{user_request}'. Focus your evaluation ONLY on what the user actually requested. Do not demand additional tactical elements unless they were specifically requested. Always search for NHL standards before reviewing."},
                            {
                                "type": "input_image",
                                "image_url": f"data:image/png;base64,{image_data}"
                            }
                        ],
                        "role": "user"
                    }
                ]
                
                # Review image
                print("  🔍 Reviewing image accuracy...")
                review_result = await Runner.run(
                    self.reviewer.agent, 
                    review_input,
                    previous_response_id=reviewer_previous_response_id
                )
                feedback: ImageFeedback = review_result.final_output
                
                # Update reviewer's previous response ID for next iteration
                reviewer_previous_response_id = review_result.last_response_id
                
                # Store iteration results
                iteration_data = {
                    "iteration": iteration,
                    "image_path": image_path,
                    "feedback": feedback,
                    "timestamp": datetime.now().isoformat(),
                    "user_feedback": None
                }
                
                # Print AI feedback
                print(f"  📊 Score: {feedback.score} (Accuracy: {feedback.accuracy_score}/10)")
                print(f"  💬 Feedback: {feedback.feedback}")
                
                if feedback.specific_issues:
                    print("  🔧 Specific Issues:")
                    for issue in feedback.specific_issues:
                        print(f"    - {issue}")
                
                # Get user feedback if enabled
                user_feedback = ""
                if self.enable_user_feedback:
                    user_feedback = self.get_user_feedback(iteration, image_path, feedback)
                    iteration_data["user_feedback"] = user_feedback
                    
                    if user_feedback == "USER_APPROVE":
                        print(f"\n✅ Image approved by user after {iteration} iterations!")
                        self.iteration_history.append(iteration_data)
                        break
                    elif user_feedback == "USER_SKIP":
                        print("  👤 User chose to skip feedback for remaining iterations")
                        self.enable_user_feedback = False
                
                self.iteration_history.append(iteration_data)
                
                # Check if we should continue based on AI feedback
                if feedback.score == "pass" and user_feedback != "USER_SKIP":
                    print(f"\n✅ Image approved by AI after {iteration} iterations!")
                    break
                
                if iteration < self.max_iterations:
                    print("  🔄 Preparing for next iteration with feedback...")
                    
                    # Combine AI and user feedback
                    feedback_components = [f"AI Reviewer feedback: {feedback.feedback}"]
                    if feedback.specific_issues:
                        feedback_components.append(f"AI identified issues: {', '.join(feedback.specific_issues)}")
                    
                    if user_feedback and user_feedback not in ["USER_APPROVE", "USER_SKIP", ""]:
                        feedback_components.append(f"User feedback: {user_feedback}")
                    
                    combined_feedback = "\n".join(feedback_components)
                    feedback_msg = f"Previous attempt feedback:\n{combined_feedback}\n\nPlease improve the image addressing these concerns."
                    
                    input_items.append({"content": feedback_msg, "role": "user"})
                else:
                    print(f"\n⏹️  Reached maximum iterations ({self.max_iterations})")
        
        return {
            "session_id": session_id,
            "total_iterations": len(self.iteration_history),
            "final_score": self.iteration_history[-1]["feedback"].score if self.iteration_history else "none",
            "iterations": self.iteration_history
        }
    
    def print_summary(self, results: dict):
        """Print comprehensive summary of the generation session"""
        print("\n" + "=" * 60)
        print("🏒 HOCKEY IMAGE GENERATION SUMMARY")
        print("=" * 60)
        
        print(f"📋 Session ID: {results['session_id']}")
        print(f"🔢 Total Iterations: {results['total_iterations']}")
        print(f"🎯 Final Score: {results['final_score']}")
        print(f"📂 Output Directory: {self.output_dir}")
        
        print(f"\n📈 Iteration Details:")
        for i, iteration in enumerate(results['iterations'], 1):
            feedback = iteration['feedback']
            print(f"\n  Iteration {iteration['iteration']}:")
            print(f"    🖼️  Image: {iteration['image_path']}")
            print(f"    📊 Score: {feedback.score} ({feedback.accuracy_score}/10)")
            print(f"    💬 Feedback: {feedback.feedback[:100]}{'...' if len(feedback.feedback) > 100 else ''}")
            
            if feedback.specific_issues:
                print(f"    🔧 Issues: {len(feedback.specific_issues)} identified")
            
            if iteration.get('user_feedback'):
                user_fb = iteration['user_feedback']
                if user_fb in ["USER_APPROVE", "USER_SKIP"]:
                    print(f"    👤 User: {user_fb}")
                else:
                    print(f"    👤 User: {user_fb[:80]}{'...' if len(user_fb) > 80 else ''}")
        
        print(f"\n📁 All images saved to: {self.output_dir}")
        
        if results['final_score'] == 'pass':
            final_image = results['iterations'][-1]['image_path']
            print(f"✅ Final approved image: {final_image}")
        else:
            print("❌ No image was approved within the iteration limit")


def main():
    parser = argparse.ArgumentParser(
        description="Generate and iteratively improve hockey whiteboard diagrams"
    )
    parser.add_argument(
        "--request",
        help="Description of the hockey diagram to generate"
    )
    parser.add_argument(
        "--output-dir",
        default="image_gen/outputs/iterations",
        help="Directory to save iteration images (default: image_gen/outputs/iterations)"
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=5,
        help="Maximum number of iterations (default: 5)"
    )
    parser.add_argument(
        "--user-feedback",
        action="store_true",
        help="Enable user feedback prompts during generation"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    if not args.request:
        print("❌ Error: --request is required")
        print("Example: python hockey_image_iterative.py --request 'defensive zone coverage diagram'")
        sys.exit(1)
    
    async def run_generation():
        iterator = HockeyImageIterator(
            output_dir=args.output_dir,
            max_iterations=args.max_iterations,
            enable_user_feedback=args.user_feedback
        )
        
        if args.user_feedback:
            print("👤 User feedback mode enabled - you will be prompted to review each iteration")
        
        try:
            results = await iterator.generate_and_review(args.request)
            iterator.print_summary(results)
            
        except KeyboardInterrupt:
            print("\n⏹️  Generation interrupted by user")
            if iterator.iteration_history:
                results = {
                    "session_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
                    "total_iterations": len(iterator.iteration_history),
                    "final_score": "interrupted",
                    "iterations": iterator.iteration_history
                }
                iterator.print_summary(results)
        except Exception as e:
            print(f"\n❌ Error during generation: {e}")
            sys.exit(1)
    
    # Run the async function
    asyncio.run(run_generation())


if __name__ == "__main__":
    main()

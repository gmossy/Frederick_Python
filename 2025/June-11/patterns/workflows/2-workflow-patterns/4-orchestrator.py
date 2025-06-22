from typing import List, Dict
from pydantic import BaseModel, Field
from openai import OpenAI
import os
import logging
import json

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = "gpt-4"

# --------------------------------------------------------------
# Step 1: Define the data models
# --------------------------------------------------------------


class SubTask(BaseModel):
    """Blog section task defined by orchestrator"""

    section_type: str = Field(description="Type of blog section to write")
    description: str = Field(description="What this section should cover")
    style_guide: str = Field(description="Writing style for this section")
    target_length: int = Field(description="Target word count for this section")


class OrchestratorPlan(BaseModel):
    """Orchestrator's blog structure and tasks"""

    topic_analysis: str = Field(description="Analysis of the blog topic")
    target_audience: str = Field(description="Intended audience for the blog")
    sections: List[SubTask] = Field(description="List of sections to write")


class SectionContent(BaseModel):
    """Content written by a worker"""

    content: str = Field(description="Written content for the section")
    key_points: List[str] = Field(description="Main points covered")


class SuggestedEdits(BaseModel):
    """Suggested edits for a section"""

    section_name: str = Field(description="Name of the section")
    suggested_edit: str = Field(description="Suggested edit")


class ReviewFeedback(BaseModel):
    """Final review and suggestions"""

    cohesion_score: float = Field(description="How well sections flow together (0-1)")
    suggested_edits: List[SuggestedEdits] = Field(
        description="Suggested edits by section"
    )
    final_version: str = Field(description="Complete, polished blog post")


# --------------------------------------------------------------
# Step 2: Define prompts
# --------------------------------------------------------------

ORCHESTRATOR_PROMPT = """
Analyze this blog topic and break it down into logical sections.

Topic: {topic}
Target Length: {target_length} words
Style: {style}

Please return your response in this JSON format:

{{
  "topic_analysis": "Your analysis here",
  "target_audience": "Your audience description here",
  "sections": [
    {{
      "section_type": "Introduction",
      "description": "Brief overview of the topic",
      "style_guide": "Keep it engaging and informative",
      "target_length": 200
    }}
  ]
}}

Make sure to replace the example values with actual content.
"""

WORKER_PROMPT = """
Write a blog section based on:
Topic: {topic}
Section Type: {section_type}
Section Goal: {description}
Style Guide: {style_guide}

Previous Sections:
{previous_sections}

Please return your response in this JSON format:

{{
  "content": "Your section content here",
  "key_points": [
    "Main point 1",
    "Main point 2",
    "Main point 3"
  ]
}}

Important: Make sure your response is valid JSON. Do not include any extra characters or newlines inside the JSON object. Keep the content concise and avoid using special characters that could break the JSON format.
"""

REVIEWER_PROMPT = """
Review the blog post and provide feedback.

Topic: {topic}
Target Audience: {audience}

Blog Structure:
{plan}

Written Sections:
{sections}

Please return your response in this JSON format:

{{
  "cohesion_score": 0.85,
  "suggested_edits": [
    {{
      "section_name": "section_name",
      "suggested_edit": "suggested_edit"
    }}
  ],
  "final_version": "Complete, polished blog post"
}}

Make sure to replace the example values with actual content.
"""

# --------------------------------------------------------------
# Step 3: Implement orchestrator
# --------------------------------------------------------------


class BlogOrchestrator:
    def __init__(self):
        self.sections_content = {}

    def get_plan(self, topic: str, target_length: int, style: str) -> OrchestratorPlan:
        """Get orchestrator's blog structure plan"""
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": ORCHESTRATOR_PROMPT.format(
                            topic=topic, target_length=target_length, style=style
                        ),
                    }
                ],
            )
            response = completion.choices[0].message.content
            logger.info(f"Got plan response: {response[:200]}...")
            
            # Parse JSON response
            try:
                data = json.loads(response)
                return OrchestratorPlan(**data)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {str(e)}")
                logger.error(f"Response content: {response}")
                raise ValueError("Invalid JSON format in response")
                
        except Exception as e:
            logger.error(f"Error getting plan: {str(e)}")
            raise

    def write_section(self, topic: str, section: SubTask) -> SectionContent:
        """Worker: Write a specific blog section with context from previous sections.

        Args:
            topic: The main blog topic
            section: SubTask containing section details

        Returns:
            SectionContent: The written content and key points
        """
        try:
            # Create context from previously written sections
            previous_sections = "\n\n".join(
                [
                    f"=== {section_type} ===\n{content.content}"
                    for section_type, content in self.sections_content.items()
                ]
            )

            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": WORKER_PROMPT.format(
                            topic=topic,
                            previous_sections=previous_sections,
                            section_type=section.section_type,
                            description=section.description,
                            style_guide=section.style_guide,
                            target_length=section.target_length,
                        ),
                    }
                ],
            )
            response = completion.choices[0].message.content
            logger.info(f"Got section response for {section.section_type}: {response[:100]}...")
            
            # Parse JSON response
            try:
                # Clean up the response by removing any extra characters and newlines
                cleaned_response = response.strip()
                cleaned_response = ''.join(cleaned_response.splitlines())
                cleaned_response = cleaned_response.replace('"', '"')  # Fix double quotes
                
                data = json.loads(cleaned_response)
                return SectionContent(**data)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {str(e)}")
                logger.error(f"Cleaned response: {cleaned_response}")
                logger.error(f"Original response: {response}")
                raise ValueError("Invalid JSON format in response")
                
        except Exception as e:
            logger.error(f"Error writing section {section.section_type}: {str(e)}")
            raise

    def review_post(self, topic: str, plan: OrchestratorPlan) -> ReviewFeedback:
        """Reviewer: Analyze and improve overall cohesion"""
        try:
            sections_text = "\n\n".join(
                [
                    f"=== {section_type} ===\n{content.content}"
                    for section_type, content in self.sections_content.items()
                ]
            )

            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": REVIEWER_PROMPT.format(
                            topic=topic,
                            audience=plan.target_audience,
                            plan=plan.model_dump_json(indent=2),
                            sections=sections_text,
                        ),
                    }
                ],
            )
            response = completion.choices[0].message.content
            logger.info(f"Got review response: {response[:100]}...")
            
            # Parse JSON response
            try:
                data = json.loads(response)
                return ReviewFeedback(**data)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {str(e)}")
                logger.error(f"Response content: {response}")
                raise ValueError("Invalid JSON format in response")
                
        except Exception as e:
            logger.error(f"Error reviewing post: {str(e)}")
            raise

    def write_blog(
        self, topic: str, target_length: int = 1000, style: str = "informative"
    ) -> Dict:
        """Process the entire blog writing task"""
        logger.info(f"Starting blog writing process for: {topic}")

        # Get blog structure plan
        plan = self.get_plan(topic, target_length, style)
        logger.info(f"Blog structure planned: {len(plan.sections)} sections")
        logger.info(f"Blog structure planned: {plan.model_dump_json(indent=2)}")

        # Write each section
        for section in plan.sections:
            logger.info(f"Writing section: {section.section_type}")
            content = self.write_section(topic, section)
            self.sections_content[section.section_type] = content

        # Review and polish
        logger.info("Reviewing full blog post")
        review = self.review_post(topic, plan)

        return {"structure": plan, "sections": self.sections_content, "review": review}


# --------------------------------------------------------------
# Step 4: Example usage
# --------------------------------------------------------------

if __name__ == "__main__":
    orchestrator = BlogOrchestrator()

    # Example: Technical blog post
    topic = "The impact of AI on software development"
    result = orchestrator.write_blog(
        topic=topic, target_length=1200, style="technical but accessible"
    )

    print("\nFinal Blog Post:")
    print(result["review"].final_version)

    print("\nCohesion Score:", result["review"].cohesion_score)
    if result["review"].suggested_edits:
        for edit in result["review"].suggested_edits:
            print(f"Section: {edit.section_name}")
            print(f"Suggested Edit: {edit.suggested_edit}")

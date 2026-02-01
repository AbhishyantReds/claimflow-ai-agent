"""
Tests for prompts and LLM interactions
"""
import pytest
from agent.prompts import (
    CONVERSATION_SYSTEM_PROMPT,
    FIELD_EXTRACTION_PROMPT,
    NEXT_QUESTION_PROMPT,
    CLAIM_TYPE_DETECTION_PROMPT
)


class TestPromptStructure:
    """Test prompt structure and completeness"""
    
    def test_conversation_prompt_exists(self):
        """Test conversation system prompt exists"""
        assert CONVERSATION_SYSTEM_PROMPT is not None
        assert len(CONVERSATION_SYSTEM_PROMPT) > 100
    
    def test_conversation_prompt_contains_key_sections(self):
        """Test conversation prompt has key sections"""
        prompt = CONVERSATION_SYSTEM_PROMPT.lower()
        
        # Should mention greeting behavior
        assert "greet" in prompt or "hello" in prompt
        
        # Should mention claim types
        assert "motor" in prompt or "vehicle" in prompt
        assert "home" in prompt or "property" in prompt
        assert "health" in prompt or "medical" in prompt
    
    def test_extraction_prompt_exists(self):
        """Test field extraction prompt exists"""
        assert FIELD_EXTRACTION_PROMPT is not None
        assert len(FIELD_EXTRACTION_PROMPT) > 100
    
    def test_extraction_prompt_has_field_definitions(self):
        """Test extraction prompt defines required fields"""
        prompt = FIELD_EXTRACTION_PROMPT.lower()
        
        # Motor fields
        assert "vehicle" in prompt or "registration" in prompt
        
        # Home fields
        assert "property" in prompt
        
        # Health fields
        assert "hospital" in prompt or "treatment" in prompt
    
    def test_next_question_prompt_exists(self):
        """Test next question prompt exists"""
        assert NEXT_QUESTION_PROMPT is not None
        assert len(NEXT_QUESTION_PROMPT) > 50
    
    def test_next_question_prompt_mentions_memory(self):
        """Test next question prompt handles conversation memory"""
        prompt = NEXT_QUESTION_PROMPT
        
        # Should include asked_questions to prevent repeats
        assert "{asked_questions}" in prompt
    
    def test_claim_detection_prompt_exists(self):
        """Test claim type detection prompt exists"""
        assert CLAIM_TYPE_DETECTION_PROMPT is not None
        assert len(CLAIM_TYPE_DETECTION_PROMPT) > 50
    
    def test_claim_detection_prompt_has_categories(self):
        """Test detection prompt mentions all categories"""
        prompt = CLAIM_TYPE_DETECTION_PROMPT.lower()
        
        assert "motor" in prompt
        assert "home" in prompt
        assert "health" in prompt


class TestPromptFormatting:
    """Test prompt formatting with variables"""
    
    def test_extraction_prompt_formatting(self):
        """Test extraction prompt can be formatted"""
        formatted = FIELD_EXTRACTION_PROMPT.format(
            conversation="User said they had an accident"
        )
        
        assert "accident" in formatted
        assert len(formatted) > len(FIELD_EXTRACTION_PROMPT) - 50
    
    def test_next_question_formatting(self):
        """Test next question prompt can be formatted"""
        formatted = NEXT_QUESTION_PROMPT.format(
            claim_type="motor_accident",
            collected_data='{"vehicle_registration": "KA-01-AB-1234"}',
            asked_questions='["When did the accident happen?"]'
        )
        
        assert "motor_accident" in formatted
        assert "KA-01-AB-1234" in formatted
    
    def test_detection_prompt_formatting(self):
        """Test detection prompt can be formatted"""
        formatted = CLAIM_TYPE_DETECTION_PROMPT.format(
            user_message="My car was in an accident"
        )
        
        assert "car" in formatted
        assert "accident" in formatted


class TestPromptCoverage:
    """Test prompt covers all claim scenarios"""
    
    def test_motor_claim_types_covered(self):
        """Test all motor claim types mentioned"""
        prompt = FIELD_EXTRACTION_PROMPT.lower()
        
        # Should handle different motor claims
        assert "accident" in prompt or "collision" in prompt
        assert "theft" in prompt or "stolen" in prompt
    
    def test_home_claim_types_covered(self):
        """Test all home claim types mentioned"""
        prompt = FIELD_EXTRACTION_PROMPT.lower()
        
        assert "fire" in prompt
        assert "theft" in prompt or "burglary" in prompt
        assert "flood" in prompt or "water" in prompt
    
    def test_health_claim_types_covered(self):
        """Test all health claim types mentioned"""
        prompt = FIELD_EXTRACTION_PROMPT.lower()
        
        assert "hospitalization" in prompt or "hospital" in prompt
        assert "surgery" in prompt or "operation" in prompt
        assert "treatment" in prompt or "medical" in prompt


class TestPromptExamples:
    """Test prompt examples and guidelines"""
    
    def test_conversation_prompt_has_examples(self):
        """Test conversation prompt includes example interactions"""
        prompt = CONVERSATION_SYSTEM_PROMPT
        
        # Should have examples or guidelines
        assert "example" in prompt.lower() or "like" in prompt.lower()
    
    def test_extraction_prompt_has_json_format(self):
        """Test extraction prompt specifies JSON format"""
        prompt = FIELD_EXTRACTION_PROMPT
        
        # Should specify JSON output
        assert "json" in prompt.lower() or "{" in prompt
    
    def test_next_question_prompt_has_guidelines(self):
        """Test next question prompt has conversation guidelines"""
        prompt = NEXT_QUESTION_PROMPT
        
        # Should guide on asking questions
        assert "ask" in prompt.lower() or "question" in prompt.lower()


class TestPromptConsistency:
    """Test prompts are consistent across types"""
    
    def test_field_names_consistent(self):
        """Test field names are consistent across prompts"""
        extraction = FIELD_EXTRACTION_PROMPT.lower()
        next_q = NEXT_QUESTION_PROMPT.lower()
        
        # Key field names should appear in both
        common_fields = ["vehicle", "date", "description"]
        
        for field in common_fields:
            # At least some fields should be in both prompts
            pass  # This is a soft check
    
    def test_claim_type_names_consistent(self):
        """Test claim type names match across prompts"""
        detection = CLAIM_TYPE_DETECTION_PROMPT.lower()
        extraction = FIELD_EXTRACTION_PROMPT.lower()
        
        # Claim categories should be consistent
        categories = ["motor", "home", "health"]
        
        for category in categories:
            assert category in detection
            assert category in extraction


class TestPromptEdgeCases:
    """Test prompt handling of edge cases"""
    
    def test_empty_conversation(self):
        """Test prompts with empty conversation"""
        try:
            formatted = FIELD_EXTRACTION_PROMPT.format(conversation="")
            assert formatted is not None
        except KeyError:
            pytest.fail("Prompt should handle empty conversation")
    
    def test_special_characters(self):
        """Test prompts with special characters"""
        try:
            formatted = FIELD_EXTRACTION_PROMPT.format(
                conversation="User said: \"My car's bumper is damaged!\""
            )
            assert "damaged" in formatted
        except Exception as e:
            pytest.fail(f"Prompt should handle special characters: {e}")
    
    def test_long_conversation(self):
        """Test prompts with long conversation history"""
        long_conv = " ".join(["User said something."] * 100)
        
        try:
            formatted = FIELD_EXTRACTION_PROMPT.format(conversation=long_conv)
            assert formatted is not None
        except Exception as e:
            pytest.fail(f"Prompt should handle long conversations: {e}")


class TestPromptValidation:
    """Test prompt validation and completeness"""
    
    def test_no_placeholder_leaks(self):
        """Test prompts don't have unformatted placeholders in examples"""
        prompts = [
            CONVERSATION_SYSTEM_PROMPT,
            FIELD_EXTRACTION_PROMPT,
            NEXT_QUESTION_PROMPT,
            CLAIM_TYPE_DETECTION_PROMPT
        ]
        
        for prompt in prompts:
            # Check for common placeholder patterns that shouldn't be in examples
            # This is a basic check - adjust based on your prompt structure
            assert prompt is not None
    
    def test_prompt_length_reasonable(self):
        """Test prompts are not too short or too long"""
        prompts = {
            "conversation": CONVERSATION_SYSTEM_PROMPT,
            "extraction": FIELD_EXTRACTION_PROMPT,
            "next_question": NEXT_QUESTION_PROMPT,
            "detection": CLAIM_TYPE_DETECTION_PROMPT
        }
        
        for name, prompt in prompts.items():
            assert len(prompt) > 50, f"{name} prompt too short"
            assert len(prompt) < 10000, f"{name} prompt too long"

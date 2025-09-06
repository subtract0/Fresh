#!/usr/bin/env python3
"""
Test Suite: Enhanced Father Orchestrator
"""
import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import json
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts import enhanced_father_documentation_orchestrator as orchestrator_module

class TestEnhancedFatherOrchestrator:
    @pytest.fixture
    def valid_json_response(self):
        return {
            "optimization_assessment": "test assessment",
            "system_optimization_backlog": [
                {
                    "type": "integration",
                    "priority": "critical",
                    "file_path": "test/path",
                    "title": "test task",
                    "description": "test details",
                    "agent_benefit": "test benefit",
                    "success_criteria": "test criteria"
                }
            ],
            "learning_strategy": "test strategy"
        }
    
    def test_analyze_system_efficiency(self):
        """Test system efficiency analysis"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(stdout="test/file.py\ntest/other.py", returncode=0)
            result = orchestrator_module.analyze_system_efficiency()
            
            assert isinstance(result, dict)
            assert "code_debt_issues" in result
            assert "agent_blockers" in result
            assert "missing_integrations" in result
    
    def test_create_strategic_planning_prompt(self):
        """Test prompt creation for strategic planning"""
        system_analysis = {"test": "data"}
        prompt = orchestrator_module.create_strategic_planning_prompt(system_analysis)
        
        assert "LEAN AUTONOMOUS SYSTEM OPTIMIZATION" in prompt
        assert "SPACEX" in prompt.upper()
        assert json.dumps(system_analysis, indent=2) in prompt
    
    def test_create_fallback_optimization_strategy(self):
        """Test fallback strategy creation"""
        system_analysis = {"test": "data"}
        strategy = orchestrator_module.create_fallback_optimization_strategy(system_analysis)
        
        assert "optimization_assessment" in strategy
        assert "system_optimization_backlog" in strategy
        assert "learning_strategy" in strategy
        assert len(strategy["system_optimization_backlog"]) > 0
    
    @pytest.mark.asyncio
    async def test_consult_enhanced_father_gpt5_success(self, valid_json_response):
        """Test Enhanced Father consultation with GPT-5 success"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content=json.dumps(valid_json_response)))]
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            mock_client.chat.completions.create.return_value = mock_response
            
            system_analysis = {"test": "data"}
            result = await orchestrator_module.consult_strategic_planner(system_analysis)
            
            assert result == valid_json_response
            # Verify GPT-5 parameters
            call_kwargs = mock_client.chat.completions.create.call_args.kwargs
            assert call_kwargs["model"] == "gpt-5"
            assert call_kwargs["reasoning_effort"] == "high"
            assert call_kwargs["verbosity"] == "low"
    
    @pytest.mark.asyncio
    async def test_consult_enhanced_father_fallback_to_gpt4o(self, valid_json_response):
        """Test fallback from GPT-5 to GPT-4o"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content=json.dumps(valid_json_response)))]
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            # First call (GPT-5) raises exception, second call (GPT-4o) succeeds
            mock_client.chat.completions.create.side_effect = [
                Exception("Model not found"),
                mock_response
            ]
            
            system_analysis = {"test": "data"}
            result = await orchestrator_module.consult_strategic_planner(system_analysis)
            
            assert result == valid_json_response
            assert mock_client.chat.completions.create.call_count == 2
    
    @pytest.mark.asyncio  
    async def test_consult_enhanced_father_json_extraction(self):
        """Test JSON extraction from various response formats"""
        valid_json = {"optimization_assessment": "test", "system_optimization_backlog": [], "learning_strategy": "test"}
        
        test_cases = [
            json.dumps(valid_json),  # Direct JSON
            f"```json\n{json.dumps(valid_json)}\n```",  # JSON in code block
            f"Some text before {json.dumps(valid_json)} and after",  # JSON in text
        ]
        
        for test_response in test_cases:
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content=test_response))]
            
            with patch('openai.OpenAI') as mock_openai:
                mock_client = Mock()
                mock_openai.return_value = mock_client
                mock_client.chat.completions.create.return_value = mock_response
                
                system_analysis = {"test": "data"}
                result = await orchestrator_module.consult_strategic_planner(system_analysis)
                
                assert "optimization_assessment" in result
                assert "system_optimization_backlog" in result
                assert "learning_strategy" in result

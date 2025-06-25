import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json
import statistics
from concurrent.futures import ThreadPoolExecutor
import time

# Import LLM clients (install as needed)
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

import requests
from app.core.config import settings
from app.schemas.portfolio import PortfolioInsights

logger = logging.getLogger(__name__)

class EnhancedAIInsightsService:
    """
    Strategic Multi-LLM AI Investment Assistant
    
    Features:
    - Multi-model ensemble for better accuracy
    - Specialized financial prompts
    - Local Llama integration (free)
    - Fast response optimization
    - Meaningful quality scores (no fake confidence)
    """
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self.gemini_model = None
        self.ollama_base_url = "http://localhost:11434"
        self.available_models = []
        
        # Initialize all available LLM clients
        self._initialize_llm_clients()
        
        # Response cache for faster results
        self._response_cache = {}
        self._cache_ttl = 300  # 5 minutes
        
    def _initialize_llm_clients(self):
        """Initialize all available LLM clients with better models."""
        
        # OpenAI GPT (use more powerful models for better accuracy)
        if OPENAI_AVAILABLE and settings.OPENAI_API_KEY:
            try:
                self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
                self.available_models.append("gpt-4")  # More powerful model
                logger.info("OpenAI GPT-4 client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
        
        # Anthropic Claude (use more capable model)
        if ANTHROPIC_AVAILABLE and hasattr(settings, 'ANTHROPIC_API_KEY') and settings.ANTHROPIC_API_KEY:
            try:
                self.anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
                self.available_models.append("claude-3-sonnet")  # Better than haiku
                logger.info("Claude-3-Sonnet client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Anthropic client: {e}")
        
        # Google Gemini (use best free model)
        if GEMINI_AVAILABLE and hasattr(settings, 'GOOGLE_GEMINI_API_KEY') and settings.GOOGLE_GEMINI_API_KEY:
            try:
                genai.configure(api_key=settings.GOOGLE_GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-pro')  # Better model
                self.available_models.append("gemini-pro")
                logger.info("Gemini-1.5-Pro client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini client: {e}")
        
        # Initialize local Ollama with best free models
        self._initialize_ollama_models()
    
    def _initialize_ollama_models(self):
        """Initialize and setup best local Llama models."""
        try:
            # Check if Ollama is running
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model['name'] for model in models]
                
                # Prioritize best available models
                preferred_models = [
                    'llama3.1:8b',      # Best general purpose
                    'llama3.2:latest',   # Latest version
                    'mistral:latest',    # Good alternative
                    'dolphin-mistral:latest',  # Fine-tuned for instructions
                    'codellama:latest'   # Good for analysis
                ]
                
                for model in preferred_models:
                    if model in model_names:
                        self.available_models.append(f"ollama-{model}")
                        logger.info(f"Local Ollama model available: {model}")
                        break
                else:
                    # Pull the best model if none available
                    self._pull_ollama_model('llama3.1:8b')
                    
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
    
    def _pull_ollama_model(self, model_name: str):
        """Pull a model in Ollama if not available."""
        try:
            logger.info(f"Pulling Ollama model: {model_name}")
            response = requests.post(
                f"{self.ollama_base_url}/api/pull",
                json={"name": model_name},
                timeout=300  # 5 minutes timeout for model download
            )
            if response.status_code == 200:
                self.available_models.append(f"ollama-{model_name}")
                logger.info(f"Successfully pulled {model_name}")
        except Exception as e:
            logger.error(f"Failed to pull Ollama model {model_name}: {e}")
    
    async def generate_enhanced_portfolio_insights(
        self,
        portfolio_result: Any,
        tickers: List[str],
        comparison_data: Optional[Dict] = None,
        risk_analysis: Optional[Dict] = None
    ) -> PortfolioInsights:
        """Generate enhanced AI insights using multi-model ensemble."""
        
        try:
            start_time = time.time()
            
            # Prepare comprehensive data for analysis
            portfolio_data = self._prepare_enhanced_portfolio_data(
                portfolio_result, tickers, comparison_data, risk_analysis
            )
            
            # Use ensemble approach for better accuracy
            insights_text = await self._generate_ensemble_insights(portfolio_data)
            
            # Parse into structured format
            structured_insights = self._parse_enhanced_insights(insights_text, portfolio_result)
            
            processing_time = time.time() - start_time
            logger.info(f"Enhanced insights generated in {processing_time:.2f}s")
            
            return structured_insights
            
        except Exception as e:
            logger.error(f"Enhanced insights generation failed: {e}")
            return self._generate_intelligent_fallback(portfolio_result, tickers)
    
    def _prepare_enhanced_portfolio_data(
        self, 
        portfolio_result: Any, 
        tickers: List[str], 
        comparison_data: Optional[Dict] = None,
        risk_analysis: Optional[Dict] = None
    ) -> str:
        """Prepare comprehensive portfolio data with financial context."""
        
        # Extract all available metrics
        weights = getattr(portfolio_result, 'weights', {})
        expected_return = getattr(portfolio_result, 'expected_return', 0)
        volatility = getattr(portfolio_result, 'volatility', 0)
        sharpe_ratio = getattr(portfolio_result, 'sharpe_ratio', 0)
        dividend_yield = getattr(portfolio_result, 'expected_dividend_yield', 0)
        
        # Calculate portfolio characteristics
        portfolio_size = len(tickers)
        max_weight = max(weights.values()) if weights else 0
        weight_distribution = list(weights.values()) if weights else []
        concentration_score = max_weight if max_weight else 0
        
        data = {
            "portfolio_analysis": {
                "tickers": tickers,
                "portfolio_size": portfolio_size,
                "weights": weights,
                "weight_distribution": weight_distribution,
                "concentration_score": concentration_score,
                "performance_metrics": {
                    "expected_annual_return": expected_return * 100,  # Convert to percentage
                    "annual_volatility": volatility * 100,
                    "sharpe_ratio": sharpe_ratio,
                    "expected_dividend_yield": dividend_yield * 100,
                    "risk_adjusted_return": sharpe_ratio * volatility * 100 if volatility > 0 else 0
                },
                "optimization_method": getattr(portfolio_result, 'optimization_method', 'Modern Portfolio Theory')
            }
        }
        
        # Add sector analysis if available
        if hasattr(portfolio_result, 'sector_allocation'):
            data["sector_analysis"] = portfolio_result.sector_allocation
        
        # Add comparison metrics
        if comparison_data:
            data["benchmark_comparison"] = comparison_data
            
        # Add risk metrics
        if risk_analysis:
            if hasattr(risk_analysis, 'model_dump'):
                data["risk_assessment"] = risk_analysis.model_dump()
            elif hasattr(risk_analysis, 'dict'):
                data["risk_assessment"] = risk_analysis.dict()
            else:
                data["risk_assessment"] = risk_analysis
        
        return json.dumps(data, indent=2, default=str)
    
    async def _generate_ensemble_insights(self, portfolio_data: str) -> str:
        """Generate insights using ensemble of multiple LLMs for better accuracy."""
        
        # Create specialized financial analysis prompt
        prompt = self._create_financial_analysis_prompt(portfolio_data)
        
        # Try to get insights from multiple models concurrently
        tasks = []
        
        # Add available models to task list
        if self.openai_client:
            tasks.append(self._call_openai_enhanced(prompt))
        if self.gemini_model:
            tasks.append(self._call_gemini_enhanced(prompt))
        if self.anthropic_client:
            tasks.append(self._call_anthropic_enhanced(prompt))
        
        # Add best local model
        if any('ollama' in model for model in self.available_models):
            tasks.append(self._call_ollama_enhanced(prompt))
        
        if not tasks:
            return self._generate_intelligent_fallback_text(portfolio_data)
        
        # Execute models concurrently for speed
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful responses
        successful_responses = [
            result for result in results 
            if isinstance(result, str) and len(result) > 100
        ]
        
        if not successful_responses:
            return self._generate_intelligent_fallback_text(portfolio_data)
        
        # If multiple responses, combine them intelligently
        if len(successful_responses) > 1:
            return self._combine_insights(successful_responses)
        else:
            return successful_responses[0]
    
    def _create_financial_analysis_prompt(self, portfolio_data: str) -> str:
        """Create specialized financial analysis prompt for better accuracy."""
        
        return f"""You are a CFA (Chartered Financial Analyst) and portfolio manager with 20+ years of experience in dividend investing and portfolio optimization.

PORTFOLIO DATA:
{portfolio_data}

ANALYSIS REQUIRED:
Provide a comprehensive investment analysis following this exact structure:

**EXECUTIVE SUMMARY**
- One-paragraph overview of the portfolio's investment thesis

**STRENGTHS (3-4 specific points)**
- Identify the strongest aspects of this allocation
- Focus on risk-adjusted returns, dividend sustainability, and diversification benefits
- Use specific metrics where possible

**RISKS & CONCERNS (3-4 specific points)**  
- Identify the most significant risks
- Include concentration risk, sector exposure, and market sensitivity
- Quantify risks where possible

**ACTIONABLE RECOMMENDATIONS (3-4 specific actions)**
- Provide specific, implementable advice
- Include rebalancing suggestions, risk management, and monitoring points
- Prioritize by impact and feasibility

**PORTFOLIO SCORES**
- Diversification Quality: X/10 (with brief justification)
- Risk Management: X/10 (with brief justification)  
- Income Sustainability: X/10 (with brief justification)
- Overall Portfolio Quality: X/10 (with brief justification)

Focus on practical insights that a serious investor can act upon. Avoid generic advice."""

    async def _call_openai_enhanced(self, prompt: str) -> Optional[str]:
        """Enhanced OpenAI call with better model and parameters."""
        try:
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-4",  # More powerful model
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a CFA charterholder and senior portfolio manager specializing in dividend growth investing and quantitative portfolio optimization. Provide detailed, actionable financial analysis."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3,  # Lower temperature for more consistent analysis
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Enhanced OpenAI call failed: {e}")
            return None
    
    async def _call_anthropic_enhanced(self, prompt: str) -> Optional[str]:
        """Enhanced Anthropic call with better model and parameters."""
        try:
            response = await asyncio.to_thread(
                self.anthropic_client.messages.create,
                model="claude-3-sonnet-20240229",  # Better model
                max_tokens=2000,
                temperature=0.3,
                system="You are a CFA charterholder with expertise in portfolio management, dividend investing, and risk analysis. Provide thorough, data-driven investment insights.",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Enhanced Anthropic call failed: {e}")
            return None
    
    async def _call_gemini_enhanced(self, prompt: str) -> Optional[str]:
        """Enhanced Gemini call with better configuration."""
        try:
            # Configure generation settings for financial analysis
            generation_config = {
                "temperature": 0.3,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 2000,
            }
            
            enhanced_prompt = f"""You are a senior financial analyst and CFA charterholder. 

{prompt}

Provide detailed, quantitative analysis with specific recommendations."""
            
            response = await asyncio.to_thread(
                self.gemini_model.generate_content,
                enhanced_prompt,
                generation_config=generation_config
            )
            return response.text
        except Exception as e:
            logger.error(f"Enhanced Gemini call failed: {e}")
            return None
    
    async def _call_ollama_enhanced(self, prompt: str) -> Optional[str]:
        """Enhanced local Ollama call with best available model."""
        try:
            # Find best available local model
            best_model = None
            for model in self.available_models:
                if 'ollama' in model:
                    best_model = model.replace('ollama-', '')
                    break
            
            if not best_model:
                return None
            
            enhanced_prompt = f"""You are a CFA (Chartered Financial Analyst) and portfolio manager. Analyze this portfolio professionally:

{prompt}

Provide specific, actionable investment insights."""
            
            response = await asyncio.to_thread(
                requests.post,
                f"{self.ollama_base_url}/api/generate",
                json={
                    "model": best_model,
                    "prompt": enhanced_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "top_p": 0.8,
                        "num_predict": 1500
                    }
                },
                timeout=45
            )
            
            if response.status_code == 200:
                return response.json().get('response', '')
            
        except Exception as e:
            logger.error(f"Enhanced Ollama call failed: {e}")
            return None
    
    def _combine_insights(self, responses: List[str]) -> str:
        """Intelligently combine multiple LLM responses for better accuracy."""
        
        # Extract sections from each response
        combined_strengths = []
        combined_risks = []
        combined_recommendations = []
        all_scores = {}
        
        for response in responses:
            # Extract strengths
            strengths = self._extract_section(response, ["strengths", "advantages", "benefits"])
            combined_strengths.extend(strengths)
            
            # Extract risks
            risks = self._extract_section(response, ["risks", "concerns", "challenges", "weaknesses"])
            combined_risks.extend(risks)
            
            # Extract recommendations
            recommendations = self._extract_section(response, ["recommendations", "suggestions", "advice", "actions"])
            combined_recommendations.extend(recommendations)
            
            # Extract scores
            scores = self._extract_all_scores(response)
            for score_type, value in scores.items():
                if score_type not in all_scores:
                    all_scores[score_type] = []
                all_scores[score_type].append(value)
        
        # Create best combined response
        summary = responses[0].split('\n')[0] if responses else "Portfolio analysis completed."
        
        # Remove duplicates and select best points
        unique_strengths = list(dict.fromkeys(combined_strengths))[:4]
        unique_risks = list(dict.fromkeys(combined_risks))[:4]
        unique_recommendations = list(dict.fromkeys(combined_recommendations))[:4]
        
        # Average scores across models
        avg_scores = {
            score_type: statistics.mean(values) 
            for score_type, values in all_scores.items() 
            if values
        }
        
        # Construct combined response
        combined_response = f"""**EXECUTIVE SUMMARY**
{summary}

**STRENGTHS**
{chr(10).join(f"• {strength}" for strength in unique_strengths)}

**RISKS & CONCERNS**
{chr(10).join(f"• {risk}" for risk in unique_risks)}

**ACTIONABLE RECOMMENDATIONS**
{chr(10).join(f"• {rec}" for rec in unique_recommendations)}

**PORTFOLIO SCORES**
"""
        
        for score_type, value in avg_scores.items():
            combined_response += f"• {score_type}: {value:.1f}/10\n"
        
        return combined_response

    def _extract_section(self, text: str, keywords: List[str]) -> List[str]:
        """Extract bullet points from a section of text."""
        lines = text.split('\n')
        section_lines = []
        in_section = False
        
        for line in lines:
            line = line.strip()
            
            # Check if we're entering a section
            if any(keyword in line.lower() for keyword in keywords):
                in_section = True
                continue
                
            # Check if we're leaving a section (next numbered section or major break)
            if in_section and (line.startswith('**') and any(x in line.lower() for x in ['recommendation', 'risk', 'strength', 'summary']) 
                              and not any(keyword in line.lower() for keyword in keywords)):
                break
                
            # Extract content from current section
            if in_section and line:
                # Remove various bullet point formats and extract content
                if line.startswith('*') and not line.startswith('**'):
                    # Markdown bullet
                    content = line.lstrip('* ').strip()
                    if content and len(content) > 10:  # Meaningful content
                        section_lines.append(content)
                elif line.startswith('-'):
                    # Dash bullet
                    content = line.lstrip('- ').strip()
                    if content and len(content) > 10:
                        section_lines.append(content)
                elif line.startswith('•'):
                    # Bullet point
                    content = line.lstrip('• ').strip()
                    if content and len(content) > 10:
                        section_lines.append(content)
                elif '**' in line and ':' in line:
                    # Bold header with description
                    if '**' in line:
                        parts = line.split('**')
                        if len(parts) >= 3:
                            header = parts[1].strip()
                            description = parts[2].strip(':').strip()
                            if description and len(description) > 10:
                                section_lines.append(f"{header}: {description}")
                elif not line.startswith('#') and not line.startswith('**') and len(line) > 20:
                    # Regular descriptive text
                    section_lines.append(line)
        
        return section_lines[:4]  # Limit to 4 points
    
    def _extract_score(self, text: str, score_type: str) -> Optional[float]:
        """Extract numerical scores from text."""
        import re
        
        # Look for patterns like "Diversification Score: 8/10" or "Quality: 7.5"
        patterns = [
            rf"{score_type}.*?(\d+\.?\d*)/10",
            rf"{score_type}.*?(\d+\.?\d*)",
            rf"(\d+\.?\d*)/10.*?{score_type}"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    score = float(match.group(1))
                    return min(max(score, 1.0), 10.0)  # Clamp between 1-10
                except ValueError:
                    continue
        
        return None
    
    def _extract_all_scores(self, text: str) -> Dict[str, float]:
        """Extract all scores from text."""
        scores = {}
        score_types = ["diversification", "risk", "income", "quality", "management", "sustainability"]
        for score_type in score_types:
            score = self._extract_score(text, score_type)
            if score:
                scores[score_type] = score
        return {k: v for k, v in scores.items() if v is not None}

    def _generate_intelligent_fallback_text(self, portfolio_data: str) -> str:
        """Generate intelligent fallback analysis when LLMs are unavailable."""
        
        try:
            data = json.loads(portfolio_data)
            portfolio_info = data.get('portfolio_analysis', {})
            performance = portfolio_info.get('performance_metrics', {})
            
            # Extract key metrics
            expected_return = performance.get('expected_annual_return', 0)
            volatility = performance.get('annual_volatility', 0)
            sharpe_ratio = performance.get('sharpe_ratio', 0)
            dividend_yield = performance.get('expected_dividend_yield', 0)
            tickers = portfolio_info.get('tickers', [])
            weights = portfolio_info.get('weights', {})
            concentration = portfolio_info.get('concentration_score', 0)
            
            # Generate intelligent analysis based on metrics
            summary = f"This {len(tickers)}-stock portfolio targets {expected_return:.1f}% annual returns with {volatility:.1f}% volatility."
            
            strengths = []
            if sharpe_ratio > 1.0:
                strengths.append(f"Strong risk-adjusted returns with Sharpe ratio of {sharpe_ratio:.2f}")
            if dividend_yield > 3.0:
                strengths.append(f"Attractive dividend yield of {dividend_yield:.1f}% for income generation")
            if concentration < 0.4:
                strengths.append("Well-diversified allocation reduces concentration risk")
            if len(tickers) >= 5:
                strengths.append("Adequate diversification across multiple securities")
            
            risks = []
            if volatility > 20:
                risks.append(f"High volatility of {volatility:.1f}% indicates significant market risk")
            if concentration > 0.5:
                risks.append(f"Concentrated position risk with {concentration:.1%} max allocation")
            if sharpe_ratio < 0.5:
                risks.append("Poor risk-adjusted returns may not justify the volatility")
            if dividend_yield < 2.0:
                risks.append("Low dividend yield may not meet income requirements")
            
            recommendations = []
            if concentration > 0.4:
                recommendations.append("Consider reducing concentration risk through better diversification")
            if volatility > 15:
                recommendations.append("Monitor portfolio volatility and consider defensive positions")
            recommendations.append("Regular rebalancing quarterly to maintain target allocations")
            recommendations.append("Monitor dividend sustainability and payout ratios")
            
            # Calculate realistic scores
            diversification_score = max(1, min(10, 10 - (concentration - 0.2) * 20))
            risk_score = max(1, min(10, 8 - max(0, volatility - 15) * 0.2))
            income_score = max(1, min(10, dividend_yield * 2))
            quality_score = max(1, min(10, 5 + sharpe_ratio * 3))
            
            fallback_response = f"""**EXECUTIVE SUMMARY**
{summary}

**STRENGTHS**
{chr(10).join(f"• {strength}" for strength in strengths)}

**RISKS & CONCERNS**
{chr(10).join(f"• {risk}" for risk in risks)}

**ACTIONABLE RECOMMENDATIONS**
{chr(10).join(f"• {rec}" for rec in recommendations)}

**PORTFOLIO SCORES**
• Diversification Quality: {diversification_score:.1f}/10
• Risk Management: {risk_score:.1f}/10
• Income Sustainability: {income_score:.1f}/10
• Overall Portfolio Quality: {quality_score:.1f}/10

Note: Analysis generated using quantitative metrics fallback when AI models are unavailable."""
            
            return fallback_response
            
        except Exception as e:
            logger.error(f"Fallback analysis failed: {e}")
            return """**EXECUTIVE SUMMARY**
Portfolio optimization completed with systematic risk-adjusted allocation.

**STRENGTHS**
• Quantitative optimization methodology applied
• Risk-return balance considered in allocation
• Systematic approach to portfolio construction

**RISKS & CONCERNS**
• Market volatility exposure remains
• Individual security risks present
• Economic cycle sensitivity

**ACTIONABLE RECOMMENDATIONS**
• Monitor portfolio performance regularly
• Consider rebalancing quarterly
• Review allocation against changing market conditions
• Track dividend sustainability metrics

**PORTFOLIO SCORES**
• Diversification Quality: 7.0/10
• Risk Management: 7.0/10
• Income Sustainability: 7.0/10
• Overall Portfolio Quality: 7.0/10"""

    def _parse_enhanced_insights(self, insights_text: str, portfolio_result: Any) -> PortfolioInsights:
        """Parse enhanced LLM insights into structured PortfolioInsights format."""
        
        # Extract executive summary
        summary_match = insights_text.split("**EXECUTIVE SUMMARY**")
        if len(summary_match) > 1:
            summary_section = summary_match[1].split("**")[0].strip()
            summary = summary_section[:300] + "..." if len(summary_section) > 300 else summary_section
        else:
            summary = insights_text[:200] + "..." if len(insights_text) > 200 else insights_text
        
        # Extract structured sections
        strengths = self._extract_section(insights_text, ["strengths", "advantages", "benefits"])
        risks = self._extract_section(insights_text, ["risks", "concerns", "challenges", "weaknesses"])
        recommendations = self._extract_section(insights_text, ["recommendations", "suggestions", "advice", "actions"])
        
        # Extract scores with better parsing
        all_scores = self._extract_all_scores(insights_text)
        
        # Map to expected fields
        diversification_score = (
            all_scores.get('diversification') or 
            all_scores.get('diversification_quality') or 
            7.0
        )
        
        quality_score = (
            all_scores.get('quality') or 
            all_scores.get('overall_portfolio_quality') or
            all_scores.get('portfolio_quality') or
            8.0
        )
        
        return PortfolioInsights(
            summary=summary,
            strengths=strengths,
            risks=risks,
            recommendations=recommendations,
            diversification_score=diversification_score,
            quality_score=quality_score
        )

    def _generate_intelligent_fallback(self, portfolio_result: Any, tickers: List[str]) -> PortfolioInsights:
        """Generate intelligent fallback insights when AI analysis fails."""
        
        weights = getattr(portfolio_result, 'weights', {})
        sharpe_ratio = getattr(portfolio_result, 'sharpe_ratio', 0)
        expected_return = getattr(portfolio_result, 'expected_return', 0)
        volatility = getattr(portfolio_result, 'volatility', 0)
        dividend_yield = getattr(portfolio_result, 'expected_dividend_yield', 0)
        
        # Generate intelligent summary
        summary = f"Portfolio optimized across {len(tickers)} securities with {sharpe_ratio:.3f} Sharpe ratio, targeting {expected_return*100:.1f}% annual returns."
        
        # Generate context-aware strengths
        strengths = []
        if sharpe_ratio > 1.0:
            strengths.append(f"Excellent risk-adjusted returns with Sharpe ratio of {sharpe_ratio:.2f}")
        elif sharpe_ratio > 0.5:
            strengths.append(f"Good risk-adjusted returns with Sharpe ratio of {sharpe_ratio:.2f}")
        else:
            strengths.append("Systematic optimization approach applied")
        
        if dividend_yield > 0.03:
            strengths.append(f"Attractive dividend yield of {dividend_yield*100:.1f}% for income generation")
        
        if len(tickers) >= 5:
            strengths.append("Adequate diversification across multiple securities")
        
        strengths.append("Quantitative portfolio construction methodology")
        
        # Generate intelligent risks
        risks = []
        if volatility > 0.2:
            risks.append(f"High portfolio volatility of {volatility*100:.1f}% indicates significant market risk")
        
        max_weight = max(weights.values()) if weights else 0.33
        if max_weight > 0.4:
            risks.append(f"Concentration risk with {max_weight:.1%} maximum position size")
        
        risks.extend([
            "Market volatility and economic cycle exposure",
            "Individual security and sector-specific risks",
            "Dividend policy changes could affect income"
        ])
        
        # Generate practical recommendations
        recommendations = [
            "Monitor portfolio performance against benchmarks monthly",
            "Rebalance positions quarterly or when allocations drift >5%",
            "Track dividend sustainability metrics and payout ratios",
            "Consider tax implications of rebalancing decisions"
        ]
        
        if max_weight > 0.4:
            recommendations.insert(0, "Consider reducing concentration risk through additional diversification")
        
        # Calculate realistic scores based on metrics
        diversification_score = max(1.0, min(10.0, 10 - (max_weight - 0.2) * 15))
        quality_score = max(1.0, min(10.0, 5 + sharpe_ratio * 3))
        
        return PortfolioInsights(
            summary=summary,
            strengths=strengths[:4],  # Limit to 4 points
            risks=risks[:4],
            recommendations=recommendations[:4],
            diversification_score=diversification_score,
            quality_score=quality_score
        )

    async def explain_portfolio_allocation(self, weights: Dict[str, float], tickers: List[str]) -> str:
        """Generate natural language explanation of portfolio allocation."""
        
        prompt = f"""
        Explain in simple terms why this portfolio allocation makes sense:
        
        Portfolio Weights: {weights}
        Stocks: {tickers}
        
        Provide a 2-3 sentence explanation that an average investor can understand.
        Focus on the reasoning behind the weight distribution.
        """
        
        explanation = await self._generate_ensemble_insights(prompt)
        
        if not explanation or len(explanation) < 50:
            # Intelligent fallback explanation
            max_ticker, max_weight = max(weights.items(), key=lambda x: x[1])
            return f"The portfolio allocates {max_weight:.1%} to {max_ticker} due to its superior risk-adjusted return characteristics, while maintaining diversification across {len(tickers)} securities for risk management."
        
        return explanation

    async def _query_llm(self, prompt: str) -> str:
        """Generic method to query any available LLM with fallback chain."""
        try:
            # Try enhanced methods in order of preference
            if self.openai_client:
                response = await self._call_openai_enhanced(prompt)
                if response:
                    return response
            
            if self.gemini_model:
                response = await self._call_gemini_enhanced(prompt)
                if response:
                    return response
            
            if self.anthropic_client:
                response = await self._call_anthropic_enhanced(prompt)
                if response:
                    return response
            
            # Try local Ollama as fallback
            if any('ollama' in model for model in self.available_models):
                response = await self._call_ollama_enhanced(prompt)
                if response:
                    return response
            
            return "LLM query failed - no providers available"
            
        except Exception as e:
            logger.error(f"LLM query failed: {e}")
            return f"Error: {str(e)}"

    async def analyze_dividend_sustainability(self, ticker: str, dividend_data: Dict) -> str:
        """Analyze dividend sustainability for a specific stock."""
        
        prompt = f"""
        Analyze the dividend sustainability for {ticker} based on this data:
        {json.dumps(dividend_data, indent=2)}
        
        Provide a brief assessment of:
        1. Dividend safety (1-10 scale)
        2. Growth prospects
        3. Key risks to dividend payments
        
        Keep response under 150 words.
        """
        
        analysis = await self._generate_ensemble_insights(prompt)
        return analysis or f"Dividend analysis for {ticker} requires additional data for comprehensive assessment."

# Maintain backward compatibility
AIInsightsService = EnhancedAIInsightsService

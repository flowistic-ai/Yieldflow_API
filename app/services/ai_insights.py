import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

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

class AIInsightsService:
    """Enhanced AI-powered insights for portfolio analysis using multiple LLM providers."""
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self.gemini_model = None
        
        # Initialize available LLM clients
        self._initialize_llm_clients()
        
    def _initialize_llm_clients(self):
        """Initialize available LLM clients based on API keys."""
        
        # OpenAI GPT
        if OPENAI_AVAILABLE and settings.OPENAI_API_KEY:
            try:
                self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("OpenAI client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
        
        # Anthropic Claude
        if ANTHROPIC_AVAILABLE and hasattr(settings, 'ANTHROPIC_API_KEY') and settings.ANTHROPIC_API_KEY:
            try:
                self.anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
                logger.info("Anthropic client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Anthropic client: {e}")
        
        # Google Gemini
        if GEMINI_AVAILABLE and hasattr(settings, 'GEMINI_API_KEY') and settings.GEMINI_API_KEY:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("Gemini client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini client: {e}")
    
    async def generate_portfolio_insights(
        self,
        portfolio_result: Any,
        tickers: List[str],
        comparison_data: Optional[Dict] = None,
        risk_analysis: Optional[Dict] = None
    ) -> PortfolioInsights:
        """Generate comprehensive AI-powered portfolio insights."""
        
        try:
            # Prepare data for LLM analysis
            portfolio_data = self._prepare_portfolio_data(
                portfolio_result, tickers, comparison_data, risk_analysis
            )
            
            # Generate insights using best available LLM
            insights_text = await self._generate_llm_insights(portfolio_data)
            
            # Parse and structure the insights
            structured_insights = self._parse_insights(insights_text, portfolio_result)
            
            return structured_insights
            
        except Exception as e:
            logger.error(f"Failed to generate AI insights: {e}")
            return self._fallback_insights(portfolio_result, tickers)
    
    def _prepare_portfolio_data(
        self, 
        portfolio_result: Any, 
        tickers: List[str], 
        comparison_data: Optional[Dict] = None,
        risk_analysis: Optional[Dict] = None
    ) -> str:
        """Prepare portfolio data for LLM analysis."""
        
        data = {
            "portfolio_summary": {
                "tickers": tickers,
                "weights": portfolio_result.weights if hasattr(portfolio_result, 'weights') else {},
                "expected_return": getattr(portfolio_result, 'expected_return', 0),
                "volatility": getattr(portfolio_result, 'volatility', 0),
                "sharpe_ratio": getattr(portfolio_result, 'sharpe_ratio', 0),
                "dividend_yield": getattr(portfolio_result, 'expected_dividend_yield', 0),
                "optimization_method": getattr(portfolio_result, 'optimization_method', 'Unknown')
            }
        }
        
        if comparison_data:
            data["comparison"] = comparison_data
            
        if risk_analysis:
            # Convert Pydantic model to dict if needed
            if hasattr(risk_analysis, 'model_dump'):
                data["risk_metrics"] = risk_analysis.model_dump()
            elif hasattr(risk_analysis, 'dict'):
                data["risk_metrics"] = risk_analysis.dict()
            else:
                data["risk_metrics"] = risk_analysis
        
        try:
            return json.dumps(data, indent=2, default=str)
        except Exception as e:
            logger.warning(f"JSON serialization failed: {e}")
            # Fallback without risk analysis
            data.pop("risk_metrics", None)
            data.pop("comparison", None)
            return json.dumps(data, indent=2, default=str)
    
    async def _generate_llm_insights(self, portfolio_data: str) -> str:
        """Generate insights using the best available LLM."""
        
        prompt = f"""
        As a professional financial analyst, analyze this portfolio optimization result and provide detailed insights:

        Portfolio Data:
        {portfolio_data}

        Please provide a comprehensive analysis including:
        1. Portfolio Summary: Brief overview of the allocation strategy
        2. Strengths: Key advantages of this portfolio composition
        3. Risks: Potential concerns and risk factors
        4. Recommendations: Specific actionable advice for improvement
        5. Diversification Score (1-10): Rate the portfolio's diversification
        6. Quality Score (1-10): Rate the overall portfolio quality

        Format your response as clear, actionable insights that an investor can understand and act upon.
        Focus on dividend sustainability, risk management, and growth potential.
        """
        
        # Try OpenAI first (usually best quality)
        if self.openai_client:
            try:
                response = await self._call_openai(prompt)
                if response:
                    return response
            except Exception as e:
                logger.warning(f"OpenAI call failed: {e}")
        
        # Try Anthropic Claude
        if self.anthropic_client:
            try:
                response = await self._call_anthropic(prompt)
                if response:
                    return response
            except Exception as e:
                logger.warning(f"Anthropic call failed: {e}")
        
        # Try Gemini
        if self.gemini_model:
            try:
                response = await self._call_gemini(prompt)
                if response:
                    return response
            except Exception as e:
                logger.warning(f"Gemini call failed: {e}")
        
        # Try local Ollama as final fallback
        try:
            response = await self._call_ollama(prompt)
            if response:
                return response
        except Exception as e:
            logger.warning(f"Ollama call failed: {e}")
        
        # If all LLMs fail, return basic analysis
        return self._generate_basic_insights(portfolio_data)
    
    async def _call_openai(self, prompt: str) -> Optional[str]:
        """Call OpenAI GPT API."""
        try:
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-4o-mini",  # Cost-effective model
                messages=[
                    {"role": "system", "content": "You are a professional financial analyst with expertise in portfolio optimization and dividend investing."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return None
    
    async def _call_anthropic(self, prompt: str) -> Optional[str]:
        """Call Anthropic Claude API."""
        try:
            response = await asyncio.to_thread(
                self.anthropic_client.messages.create,
                model="claude-3-haiku-20240307",  # Cost-effective model
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return None
    
    async def _call_gemini(self, prompt: str) -> Optional[str]:
        """Call Google Gemini API."""
        try:
            response = await asyncio.to_thread(
                self.gemini_model.generate_content,
                prompt
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return None
    
    async def _call_ollama(self, prompt: str) -> Optional[str]:
        """Call local Ollama API (free option)."""
        try:
            response = await asyncio.to_thread(
                requests.post,
                'http://localhost:11434/api/generate',
                json={
                    'model': 'llama3.2',  # Or any other local model
                    'prompt': prompt,
                    'stream': False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get('response', '')
            else:
                logger.warning(f"Ollama returned status code: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            return None
    
    def _generate_basic_insights(self, portfolio_data: str) -> str:
        """Generate basic insights when no LLM is available."""
        return """
        Portfolio Analysis Summary:
        
        Your portfolio has been optimized using Enhanced Portfolio Optimization methodology.
        
        Strengths:
        - Systematic risk-adjusted allocation
        - Dividend-focused investment strategy
        - Correlation shrinkage for improved diversification
        
        Risks:
        - Market volatility exposure
        - Dividend sustainability concerns
        - Concentration risk in selected sectors
        
        Recommendations:
        - Monitor dividend sustainability metrics
        - Consider regular rebalancing
        - Review portfolio composition quarterly
        
        Note: Enhanced AI insights require LLM configuration.
        """
    
    def _parse_insights(self, insights_text: str, portfolio_result: Any) -> PortfolioInsights:
        """Parse LLM-generated insights into structured format."""
        
        # Extract key information from insights text
        # This is a simplified parser - you could make it more sophisticated
        
        lines = insights_text.split('\n')
        summary = insights_text[:200] + "..." if len(insights_text) > 200 else insights_text
        
        # Extract sections (simplified)
        strengths = self._extract_section(insights_text, ["strengths", "advantages", "benefits"])
        risks = self._extract_section(insights_text, ["risks", "concerns", "challenges"])
        recommendations = self._extract_section(insights_text, ["recommendations", "suggestions", "advice"])
        
        # Extract scores (look for numbers out of 10)
        diversification_score = self._extract_score(insights_text, "diversification") or 7.0
        quality_score = self._extract_score(insights_text, "quality") or 8.0
        
        return PortfolioInsights(
            summary=summary,
            strengths=strengths,
            risks=risks,
            recommendations=recommendations,
            diversification_score=diversification_score,
            quality_score=quality_score
        )
    
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
    
    def _fallback_insights(self, portfolio_result: Any, tickers: List[str]) -> PortfolioInsights:
        """Generate fallback insights when AI analysis fails."""
        
        weights = getattr(portfolio_result, 'weights', {})
        sharpe_ratio = getattr(portfolio_result, 'sharpe_ratio', 0)
        
        # Basic analysis based on portfolio characteristics
        summary = f"Portfolio optimized across {len(tickers)} securities with Sharpe ratio of {sharpe_ratio:.3f}"
        
        strengths = [
            "Systematic optimization approach",
            "Risk-adjusted allocation",
            "Dividend-focused strategy"
        ]
        
        risks = [
            "Market volatility exposure",
            "Dividend policy changes",
            "Sector concentration risk"
        ]
        
        recommendations = [
            "Monitor dividend sustainability",
            "Review allocation quarterly",
            "Consider market conditions"
        ]
        
        # Calculate basic scores
        max_weight = max(weights.values()) if weights else 0.33
        diversification_score = max(1.0, 10 - (max_weight - 0.33) * 20)  # Penalize concentration
        quality_score = min(10.0, max(1.0, sharpe_ratio * 10))  # Based on Sharpe ratio
        
        return PortfolioInsights(
            summary=summary,
            strengths=strengths,
            risks=risks,
            recommendations=recommendations,
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
        
        explanation = await self._generate_llm_insights(prompt)
        
        if not explanation or len(explanation) < 50:
            # Fallback explanation
            max_ticker = max(weights.items(), key=lambda x: x[1])
            return f"The portfolio allocates {max_ticker[1]:.1%} to {max_ticker[0]} due to its superior risk-adjusted return characteristics, while maintaining diversification across {len(tickers)} securities for risk management."
        
        return explanation

    async def _query_llm(self, prompt: str) -> str:
        """Generic method to query any available LLM."""
        try:
            # Try OpenAI first
            if self.openai_client:
                response = await self._call_openai(prompt)
                if response:
                    return response
            
            # Try Gemini
            if self.gemini_model:
                response = await self._call_gemini(prompt)
                if response:
                    return response
            
            # Try Anthropic Claude
            if self.anthropic_client:
                response = await self._call_anthropic(prompt)
                if response:
                    return response
            
            # Try local Ollama as fallback
            response = await self._call_ollama(prompt)
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
        
        analysis = await self._generate_llm_insights(prompt)
        return analysis or f"Dividend analysis for {ticker} requires additional data for comprehensive assessment."
